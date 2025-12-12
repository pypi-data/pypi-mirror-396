# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Scoring functions that can load a serialized model and predict."""
from typing import Optional, Union
from sklearn.preprocessing import MultiLabelBinarizer

import json
import logging
import pandas as pd
import torch

from azureml.automl.dnn.nlp.classification.common.constants import DatasetLiterals
from azureml.automl.dnn.nlp.classification.io.read._labeling_data_helper import (
    generate_predictions_output_for_labeling_service_multilabel,
    load_dataset_for_labeling_service
)
from azureml.automl.dnn.nlp.classification.io.write.save_utils import save_predicted_results
from azureml.automl.dnn.nlp.classification.multilabel.model_wrapper import ModelWrapper
from azureml.automl.dnn.nlp.classification.multilabel.utils import change_label_col_format
from azureml.automl.dnn.nlp.common._data_utils import get_dataset
from azureml.automl.dnn.nlp.common._utils import is_data_labeling_run_with_file_dataset
from azureml.automl.dnn.nlp.common.constants import DataLiterals, OutputLiterals, Split, ValidationLiterals, Warnings
from azureml.automl.dnn.nlp.common.io.utils import load_model_wrapper
from azureml.core.run import Run

_logger = logging.getLogger(__name__)


class MultilabelInferencer:
    """Class to perform inferencing on an unlabeled dataset using training run artifacts."""

    def __init__(
            self,
            run: Run,
            device: Union[str, torch.device]
    ):
        """
        Function to initialize the inferencing object

        :param run: the run object
        :param device: device to be used for inferencing.
        """
        self.run_object = run
        self.device = device

        if self.device == "cpu":
            _logger.warning(Warnings.CPU_DEVICE_WARNING)

        self.workspace = self.run_object.experiment.workspace

    def predict(
            self,
            wrapped_model: ModelWrapper,
            y_transformer: MultiLabelBinarizer,
            test_df: pd.DataFrame,
            label_column_name: str
    ) -> pd.DataFrame:
        """
        Generate predictions using model

        :param wrapped_model: model wrapper
        :param y_transformer: y_transformer
        :param test_df: DataFrame to make predictions on
        :param label_column_name: name/title of the label column
        :return: test df with new columns for list of all labels and prediction probabilities
        """

        fin_outputs = wrapped_model.predict_proba(test_df)

        # create dataframes with label columns
        label_columns = y_transformer.classes_
        predicted_df = pd.DataFrame(fin_outputs).astype(str)
        predicted_df.columns = list(label_columns)
        return predicted_df

    def score(
            self,
            input_dataset_id: Optional[str] = None,
            input_mltable_uri: Optional[str] = None,
            enable_datapoint_id_output: Optional[bool] = None
    ) -> pd.DataFrame:
        """
        Generate predictions from input files.

        :param input_dataset_id: The input dataset id
        :param input_mltable_uri: The input mltable uri.
        :param enable_datapoint_id_output: Whether to include datapoint_id in the output
        :return: Dataframe with predictions
        """
        model_wrapper = load_model_wrapper(self.run_object)
        label_column_name = json.loads(
            self.run_object.parent.parent.properties.get("AMLSettingsJsonString")
        ).get('label_column_name', DataLiterals.LABEL_COLUMN)

        is_file_dataset_labeling_run = is_data_labeling_run_with_file_dataset(self.run_object)
        input_file_paths = []
        test_dataset = get_dataset(
            self.workspace,
            Split.test,
            dataset_id=input_dataset_id,
            mltable_uri=input_mltable_uri
        )

        # Fetch dataframe
        if is_file_dataset_labeling_run:
            test_df, input_file_paths = load_dataset_for_labeling_service(
                test_dataset, DataLiterals.DATA_DIR, False, Split.test
            )
        else:
            test_df = test_dataset.to_pandas_dataframe()

        if test_df.shape[0] > 0 and label_column_name in test_df.columns and \
                test_df.iloc[0][label_column_name][0] != "[":
            _logger.warning("You are using the old format of the label column. It may parse labels incorrectly. "
                            "Please update your label column format to the new format, "
                            f"per {ValidationLiterals.DATA_PREPARATION_DOC_LINK}.")
            change_label_col_format(test_df, label_column_name)

        # Drop datapoint_id column as it is not part of the text to be trained for but keep data to add back later
        datapoint_column = pd.Series()
        columns_to_drop = [label_column_name, DatasetLiterals.DATAPOINT_ID]
        if enable_datapoint_id_output:
            datapoint_column = test_df[DatasetLiterals.DATAPOINT_ID]
        test_df = test_df[test_df.columns.difference(columns_to_drop)]

        predicted_df = self.predict(wrapped_model=model_wrapper,
                                    y_transformer=model_wrapper.y_transformer,
                                    test_df=test_df,
                                    label_column_name=label_column_name)

        if is_file_dataset_labeling_run:
            generate_predictions_output_for_labeling_service_multilabel(
                predicted_df, input_file_paths, OutputLiterals.PREDICTIONS_TXT_FILE_NAME, label_column_name
            )
        else:
            # Don't save the actual text in the inference data to the generated predictions file for privacy reasons
            if enable_datapoint_id_output:
                predicted_df.insert(0, DatasetLiterals.DATAPOINT_ID, datapoint_column)
            save_predicted_results(predicted_df, OutputLiterals.PREDICTIONS_CSV_FILE_NAME)

        return predicted_df
