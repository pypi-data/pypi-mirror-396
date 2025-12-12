# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Validation logic for the AutoNLP multiclass scenario."""
from typing import Optional

import logging

import numpy as np
import pandas as pd

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import InsufficientUniqueLabels, \
    MixedMulticlassTypes
from azureml.automl.dnn.nlp.common.constants import ValidationLiterals
from azureml.automl.dnn.nlp.validation.validators import AbstractNLPClassificationDataValidator

_logger = logging.getLogger(__name__)


class NLPMulticlassDataValidator(AbstractNLPClassificationDataValidator):
    """Validator object specific to multiclass task."""

    def check_custom_validation(
            self,
            label_column_name: str,
            train_data: pd.DataFrame,
            valid_data: Optional[pd.DataFrame] = None
    ) -> None:
        """
        Data validation logic specific to the multiclass task, to be checked after any shared validation logic.

        :param label_column_name: Name of label column.
        :param train_data: The training set data to validate.
        :param valid_data: The validation set data to validate.
        :return: None
        """
        self._check_min_label_classes(label_column_name=label_column_name,
                                      train_df=train_data,
                                      valid_df=valid_data)

    def _check_min_label_classes(self,
                                 label_column_name: str,
                                 train_df: pd.DataFrame,
                                 valid_df: Optional[pd.DataFrame] = None) -> None:
        """
        Raise validation error if the training data does not contain a minimum number of unique class labels.

        :param label_column_name: Name of the label column.
        :param train_df: Training dataset.
        :param valid_df: Validation dataset.
        :return: None
        """
        num_unique_classes = self._check_label_types_and_get_length(train_df[label_column_name].values)
        if num_unique_classes < ValidationLiterals.MIN_LABEL_CLASSES:
            raise DataException._with_error(
                AzureMLError.create(
                    InsufficientUniqueLabels,
                    exp_cnt=ValidationLiterals.MIN_LABEL_CLASSES,
                    act_cnt=num_unique_classes,
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )
        if valid_df is not None:
            self._check_label_types_and_get_length(valid_df[label_column_name].values)

    def _check_label_types_and_get_length(self, label_list: np.array) -> int:
        """
        Validate the input array of labels to filter out types apart from str, int or bool and return number of
        unique labels
        :param label_list: The array of label values.
        :return: Number of unique labels
        """
        labels_set = set()
        for label in label_list:
            if not (isinstance(label, (int, bool, str))
                    or isinstance(label, np.generic) and label.dtype.kind in set("Ubiu")):
                raise DataException._with_error(
                    AzureMLError.create(
                        MixedMulticlassTypes,
                        bad_type=type(label),
                        target=ValidationLiterals.DATA_EXCEPTION_TARGET
                    )
                )
            labels_set.add(str(label))
        return len(labels_set)
