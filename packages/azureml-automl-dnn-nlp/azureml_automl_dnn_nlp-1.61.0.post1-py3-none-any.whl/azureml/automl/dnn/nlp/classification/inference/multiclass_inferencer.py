# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Scoring functions that can load a serialized model and predict."""
from typing import Optional, Union

import json
import logging
import numpy as np
import pandas as pd
import torch

from azureml.automl.dnn.nlp.classification.common.constants import DatasetLiterals
from azureml.automl.dnn.nlp.classification.io.read._labeling_data_helper import (
    generate_predictions_output_for_labeling_service_multiclass,
    load_dataset_for_labeling_service
)
from azureml.automl.dnn.nlp.classification.io.write.save_utils import save_predicted_results
from azureml.automl.dnn.nlp.classification.multiclass.model_wrapper import ModelWrapper
from azureml.automl.dnn.nlp.common._data_utils import get_dataset
from azureml.automl.dnn.nlp.common._utils import is_data_labeling_run_with_file_dataset
from azureml.automl.dnn.nlp.common.constants import (
    DataLiterals,
    OutputLiterals,
    Split,
    Warnings
)
from azureml.automl.dnn.nlp.common.io.utils import load_model_wrapper
from azureml.core.run import Run

logger = logging.getLogger(__name__)


class MulticlassInferencer:
    """Class to perform inferencing on an unlabeled dataset using training run artifacts."""

    def __init__(self,
                 run: Run,
                 device: Union[str, torch.device]):
        """
        Function to initialize the inferencing object

        :param: Run object
        :param device: device to be used for inferencing
        """
        self.run_object = run
        self.device = device

        if self.device == "cpu":
            logger.warning(Warnings.CPU_DEVICE_WARNING)

        self.workspace = self.run_object.experiment.workspace

    def predict(self,
                wrapped_model: ModelWrapper,
                test_df: pd.DataFrame,
                label_column_name: str) -> pd.DataFrame:
        """
        Generate predictions using model

        :param wrapped_model: the wrapped model.
        :param test_df: DataFrame to make predictions on
        :param label_column_name: Name/title of the label column
        :return: Dataframe with predictions
        """
        pred_probas = wrapped_model.predict_proba(test_df)
        preds = np.argmax(pred_probas, axis=1)

        predicted_labels = [wrapped_model.classes_[cls_idx] for cls_idx in preds]
        label_confidences = np.amax(pred_probas, axis=1)
        test_df[label_column_name] = predicted_labels
        test_df[DataLiterals.LABEL_CONFIDENCE] = label_confidences
        return test_df

    def score(self,
              input_dataset_id: Optional[str] = None,
              input_mltable_uri: Optional[str] = None,
              enable_datapoint_id_output: Optional[bool] = None) -> pd.DataFrame:
        """
        Generate predictions from input files.

        :param input_dataset_id: the input dataset id.
        :param input_mltable_uri: the input mltable uri.
        :param enable_datapoint_id_output: whether to include datapoint_id in the output.
        :return: DataFrame with predictions.
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
        # Fetch data
        if is_file_dataset_labeling_run:
            test_df, input_file_paths = load_dataset_for_labeling_service(
                test_dataset, DataLiterals.DATA_DIR, False, Split.test
            )
        else:
            test_df = test_dataset.to_pandas_dataframe()

        # Drop label column if it exists since it is for scoring
        # Drop datapoint_id column as it is not part of the text to be trained for but keep data to add back later
        datapoint_column = pd.Series()
        columns_to_drop = [label_column_name, DatasetLiterals.DATAPOINT_ID]
        if enable_datapoint_id_output:
            datapoint_column = test_df[DatasetLiterals.DATAPOINT_ID]
        test_df = test_df[test_df.columns.difference(columns_to_drop)]

        predicted_df = self.predict(wrapped_model=model_wrapper,
                                    test_df=test_df,
                                    label_column_name=label_column_name)

        if is_file_dataset_labeling_run:
            generate_predictions_output_for_labeling_service_multiclass(
                predicted_df, input_file_paths, OutputLiterals.PREDICTIONS_TXT_FILE_NAME, label_column_name
            )
        else:
            # Don't save the actual text in the inference data to the generated predictions file for privacy reasons
            if enable_datapoint_id_output:
                predicted_df[DatasetLiterals.DATAPOINT_ID] = datapoint_column
                output_cols = [DatasetLiterals.DATAPOINT_ID, label_column_name, DataLiterals.LABEL_CONFIDENCE]
                predicted_df = predicted_df[output_cols]
            else:
                output_cols = [label_column_name, DataLiterals.LABEL_CONFIDENCE]
                predicted_df = predicted_df[output_cols]

            save_predicted_results(
                predicted_df, OutputLiterals.PREDICTIONS_CSV_FILE_NAME
            )

        return predicted_df
