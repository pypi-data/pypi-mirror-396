# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains dataloader functions for the classification tasks."""
from typing import Any, Dict, Optional, Tuple
from sklearn.preprocessing import MultiLabelBinarizer
from torch.utils.data import Dataset as PyTorchDataset
from transformers.tokenization_utils_base import PreTrainedTokenizerBase

import logging
import numpy as np
import pandas as pd

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.classification.io.read._labeling_data_helper import load_datasets_for_labeling_service
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import (
    MultilabelDatasetWrapper,
    MulticlassDatasetWrapper
)
from azureml.automl.dnn.nlp.classification.io.read.read_utils import get_y_transformer
from azureml.automl.dnn.nlp.classification.multiclass.utils import get_max_seq_length
from azureml.automl.dnn.nlp.common._data_utils import get_dataset
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import IncorrectClassificationDatasetType
from azureml.automl.dnn.nlp.common.constants import DataLiterals, Split, TrainingInputLiterals, ValidationLiterals
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration
from azureml.automl.dnn.nlp.validation.multiclass_validator import NLPMulticlassDataValidator
from azureml.automl.dnn.nlp.validation.multilabel_validator import NLPMultilabelDataValidator
from azureml.core.workspace import Workspace
from azureml.data import TabularDataset

_logger = logging.getLogger(__name__)


def load_and_validate_multiclass_dataset(
        workspace: Workspace,
        data_dir: str,
        label_column_name: str,
        tokenizer: PreTrainedTokenizerBase,
        automl_settings: Dict[str, Any],
        training_configuration: TrainingConfiguration,
        mltable_data_json: Optional[str] = None,
        is_labeling_run: bool = False,
        enable_long_range_text: bool = True,
) -> Tuple[PyTorchDataset,
           PyTorchDataset,
           np.ndarray,
           np.ndarray,
           Optional[np.ndarray]]:
    """
    To get the training_set, validation_set and various label lists to generate metrics

    :param workspace: workspace where dataset is stored in blob
    :param data_dir: Location to download file dataset into
    :param label_column_name: Name/title of the label column
    :param tokenizer: tokenizer to be used to tokenize the data
    :param automl_settings: dictionary with automl settings
    :param training_configuration: a collection of parameters to dictate the training procedure.
    :param mltable_data_json: mltable data json containing location of data
    :param is_labeling_run: Whether the experiment is from labeling service
    :param enable_long_range_text: param to enable long range text calculation. True by default.

    :return: training dataset, validation dataset, all class labels, train labels, y-validation
    """
    with log_utils.log_activity(
            _logger,
            activity_name=constants.TelemetryConstants.DATA_PREPARATION
    ):
        train_df, validation_df = _load_dataframe(
            workspace, data_dir, automl_settings, mltable_data_json, is_labeling_run
        )

        # The only guarantee we have right now about the train and validation dataframes is that they're dataframes.
        # DO NOT ADD CODE BETWEEN DATA LOADING (above) and VALIDATION (below) THAT RELIES ON ADDITIONAL ASSUMPTIONS.
        _logger.info(f"Raw input training dataset detected with shape {train_df.shape}.")
        if validation_df is not None:
            _logger.info(f"Raw input validation dataset detected with shape {validation_df.shape}.")

        # Data validation
        validator = NLPMulticlassDataValidator()
        validator.validate(label_column_name, train_df, validation_df)
        train_df[label_column_name] = train_df[label_column_name].astype(str)
        if validation_df is not None:
            validation_df[label_column_name] = validation_df[label_column_name].astype(str)
        training_configuration[TrainingInputLiterals.MAX_SEQ_LENGTH] = \
            get_max_seq_length(train_df=train_df,
                               tokenizer=tokenizer,
                               label_column_name=label_column_name,
                               training_configuration=training_configuration,
                               enable_long_range_text=enable_long_range_text)

        # Let's sort it for determinism
        train_label_list = np.sort(pd.unique(train_df[label_column_name]))
        label_list = train_label_list
        validation_set = None
        y_val = None
        if validation_df is not None:
            y_val = validation_df[label_column_name].values
            val_label_list = pd.unique(y_val)
            label_list = np.union1d(train_label_list, val_label_list)
            validation_set = MulticlassDatasetWrapper(dataframe=validation_df,
                                                      label_list=label_list,
                                                      tokenizer=tokenizer,
                                                      training_configuration=training_configuration,
                                                      label_column_name=label_column_name)
        training_set = MulticlassDatasetWrapper(dataframe=train_df,
                                                label_list=label_list,
                                                tokenizer=tokenizer,
                                                training_configuration=training_configuration,
                                                label_column_name=label_column_name)

    # For now, return the label_list twice, similar to multilabel,
    # such that the model is aware of unseen validation labels even at training time.
    return training_set, validation_set, label_list, label_list, y_val


def load_and_validate_multilabel_dataset(
        workspace: Workspace,
        data_dir: str,
        label_column_name: str,
        tokenizer: PreTrainedTokenizerBase,
        automl_settings: Dict[str, Any],
        training_configuration: TrainingConfiguration,
        mltable_data_json: Optional[str] = None,
        is_labeling_run: bool = False,
) -> Tuple[PyTorchDataset, PyTorchDataset, int, np.ndarray, np.ndarray, np.ndarray, MultiLabelBinarizer]:
    """To get the training_set, validation_set and num_label_columns for multilabel scenario

    :param workspace: Workspace where dataset is stored in blob
    :param data_dir: Location to download text files into
    :param label_column_name: Name/title of the label column
    :param tokenizer: tokenizer for the data.
    :param automl_settings: dictionary with automl settings
    :param training_configuration: a collection of parameters to dictate the training procedure.
    :param mltable_data_json: mltable data json containing location of data
    :param is_labeling_run: Whether the experiment is from labeling service
    :return: training dataset, validation dataset, num of label columns, train labels, all class labels,
        y-validation, y_transformer
    """

    train_df, valid_df = _load_dataframe(
        workspace, data_dir, automl_settings, mltable_data_json, is_labeling_run
    )

    # The only guarantee we have right now about the train and validation dataframes is that they're dataframes.
    # DO NOT ADD CODE BETWEEN DATA LOADING (above) and VALIDATION (below) THAT RELIES ON ADDITIONAL ASSUMPTIONS.
    _logger.info(f"Raw input training dataset detected with shape {train_df.shape}.")
    if valid_df is not None:
        _logger.info(f"Input validation dataset detected with shape {valid_df.shape}.")

    validator = NLPMultilabelDataValidator()
    validator.validate(label_col_name=label_column_name, train_data=train_df, valid_data=valid_df)

    # Fit a MultiLabelBinarizer on the label column so that we can transform labels column
    y_transformer = get_y_transformer(train_df, valid_df, label_column_name)
    num_label_cols = len(y_transformer.classes_)

    # train labels and all class labels are equivalent in multilabel training
    # return label_list for train labels and all class labels
    label_list = y_transformer.classes_

    # Convert dataset into a format ingestible by model
    training_set = MultilabelDatasetWrapper(dataframe=train_df,
                                            tokenizer=tokenizer,
                                            training_configuration=training_configuration,
                                            label_column_name=label_column_name,
                                            y_transformer=y_transformer)
    validation_set = None
    y_val = None
    if valid_df is not None:
        y_val = valid_df[label_column_name].values
        validation_set = MultilabelDatasetWrapper(dataframe=valid_df,
                                                  tokenizer=tokenizer,
                                                  training_configuration=training_configuration,
                                                  label_column_name=label_column_name,
                                                  y_transformer=y_transformer)
    return training_set, validation_set, num_label_cols, label_list, label_list, y_val, y_transformer


def _load_dataframe(
        workspace: Workspace,
        data_dir: str,
        automl_settings: Dict[str, Any],
        mltable_data_json: Optional[str] = None,
        is_labeling_run: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    load train and valid dataframe from either dataset id or mltable data json
    """
    dataset_id = automl_settings.get(DataLiterals.DATASET_ID, None)
    validation_dataset_id = automl_settings.get(DataLiterals.VALIDATION_DATASET_ID, None)
    train_dataset = get_dataset(workspace, Split.train, dataset_id, mltable_data_json)
    validation_dataset = get_dataset(workspace, Split.valid, validation_dataset_id, mltable_data_json)

    if is_labeling_run:
        train_df, validation_df = load_datasets_for_labeling_service(
            train_dataset,
            validation_dataset,
            data_dir,
            include_label=True
        )
    else:
        if not isinstance(train_dataset, TabularDataset):
            raise DataException._with_error(
                AzureMLError.create(
                    IncorrectClassificationDatasetType,
                    split_type=Split.train,
                    info_link=ValidationLiterals.DATA_PREPARATION_DOC_LINK,
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )
        train_df = train_dataset.to_pandas_dataframe()
        validation_df = None
        if validation_dataset:
            if not isinstance(validation_dataset, TabularDataset):
                raise DataException._with_error(
                    AzureMLError.create(
                        IncorrectClassificationDatasetType,
                        split_type=Split.valid,
                        info_link=ValidationLiterals.DATA_PREPARATION_DOC_LINK,
                        target=ValidationLiterals.DATA_EXCEPTION_TARGET
                    )
                )
            validation_df = validation_dataset.to_pandas_dataframe()

    return train_df, validation_df
