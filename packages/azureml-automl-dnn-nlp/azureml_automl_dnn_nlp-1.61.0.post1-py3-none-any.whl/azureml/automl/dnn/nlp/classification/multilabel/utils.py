# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities for text-classification-multilabel task."""
from scipy.special import expit
from sklearn import metrics
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import precision_recall_fscore_support
from typing import Any, Dict, Union, Tuple

import logging
import numpy as np
import pandas as pd

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.exceptions import ResourceException, DataException
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InsufficientMemory, TextDnnBadData
from azureml.automl.dnn.nlp.common.constants import ValidationLiterals
from azureml.automl.runtime.shared.score import scoring
from azureml.automl.runtime.shared.score.constants import CLASSIFICATION_NLP_MULTILABEL_SET

logger = logging.getLogger(__name__)


def compute_metrics(predictions: np.ndarray, label_ids, y_transformer) \
        -> Tuple[Dict[str, Union[float, Dict[str, Any]]], Dict[str, list]]:
    """
    Function to compute metrics like accuracy and auc-weighted

    :param predictions: (Raw logit) predictions on the validation/test dataset used for computing metrics.
    :param label_ids: Ground truth labels (one hot encoded).
    :param y_transformer: transformer used in training.
    :return: A dictionary mapping metric name to metric score, a dictionary containing metrics produced
    using different thresholds.
    """
    predictions = expit(predictions)
    threshold_metrics = compute_threshold_metrics(predictions, label_ids)
    constant_metrics = compute_constant_metrics(predictions, label_ids, y_transformer)
    return constant_metrics, threshold_metrics


def compute_constant_metrics(predictions, label_ids, y_transformer):
    """
    Function to compute non-threshold metrics, from the multilabel metric set.

    :param predictions: the predictions, as probabilities.
    :param label_ids: ground truth labels (one-hot encoded).
    :param y_transformer: the y transformer used in training.
    :return: a dictionary mapping metric name to metric score.
    """
    L = len(y_transformer.classes_)
    return scoring.score_classification(
        y_test=np.array(label_ids),
        y_pred_probs=np.array(predictions),
        metrics=CLASSIFICATION_NLP_MULTILABEL_SET,
        class_labels=np.arange(L),
        train_labels=np.arange(L),
        y_transformer=y_transformer,
        multilabel=True
    )


def change_label_col_format(input_df: pd.DataFrame, label_col_name: str) -> None:
    """
    Function to change the old multilabel label column format into the new one, in place.

    The old one follows format "label1,label2,label3"
    The new one follows format "['label1','label2','label3']"
    The labels will be parsed from the original string with sklearn.feature_extraction.text.CountVectorizer

    :param input_df: the dataset in pd.DataFrame format
    :param label_col_name: the name of label column
    :return: None as all changes are inplace
    """
    vectorizer = CountVectorizer(token_pattern=r"(?u)\b\w+\b", lowercase=False)
    encoded = vectorizer.fit_transform(input_df[label_col_name])

    # catching datasets with an excessive number of samples or vocabulary size
    try:
        encoded = encoded.toarray()
    except MemoryError:
        logger.error("Unable to validate dataset as the VM size does not have enough memory for the dataset size.")
        raise ResourceException._with_error(
            AzureMLError.create(
                InsufficientMemory,
                target=ValidationLiterals.DATA_EXCEPTION_TARGET,
            )
        )
    except ValueError as err:
        if err.args[0] == "Maximum allowed dimension exceeded":
            logger.error("Vocabulary size (number of distinct labels) and/or sample size are/is too large.")
            raise DataException._with_error(
                AzureMLError.create(
                    TextDnnBadData,
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET,
                    error_details="Too many samples and/or unique labels. "
                                  "Truncate the dataset to fewer samples and/or unique labels.",
                )
            )

    labels = vectorizer.inverse_transform(encoded)
    labels = ["['" + "','".join(item) + "']" for item in labels]
    labels = [item if len(item) > 4 else "[]" for item in labels]  # remove "['']"
    input_df[label_col_name] = labels


def compute_threshold_metrics(predictions, label_ids):
    """
    Function to compute metrics using different thresholds on confidence values

    :param predictions: np.array consisting of prediction probabilities per label
    :param label_ids: np.array consisting of ground truth labels (one-hot encoded)
    :return: dictionary containing metrics produced using different thresholds
    """

    threshold_values = np.linspace(0, 1, 21)
    threshold_values = threshold_values.round(decimals=2)

    metrics_dict = {
        'threshold': threshold_values,
        'accuracy': [],
        'f1_score_micro': [],
        'f1_score_macro': [],
        'f1_score_weighted': [],
        'recall_micro': [],
        'recall_macro': [],
        'recall_weighted': [],
        'precision_micro': [],
        'precision_macro': [],
        'precision_weighted': [],
        'num_labels': []
    }

    for threshold in threshold_values:
        t_outputs = np.array(predictions) >= threshold
        accuracy = metrics.accuracy_score(label_ids, t_outputs)
        macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
            label_ids, t_outputs, average="macro")
        weighted_precision, weighted_recall, weighted_f1, _ = precision_recall_fscore_support(
            label_ids, t_outputs, average="weighted")
        micro_precision, micro_recall, micro_f1, _ = precision_recall_fscore_support(
            label_ids, t_outputs, average="micro")

        metrics_dict['accuracy'].append(accuracy)
        metrics_dict['f1_score_micro'].append(micro_f1)
        metrics_dict['f1_score_macro'].append(macro_f1)
        metrics_dict['f1_score_weighted'].append(weighted_f1)
        metrics_dict['recall_micro'].append(micro_recall)
        metrics_dict['recall_macro'].append(macro_recall)
        metrics_dict['recall_weighted'].append(weighted_recall)
        metrics_dict['precision_micro'].append(micro_precision)
        metrics_dict['precision_macro'].append(macro_precision)
        metrics_dict['precision_weighted'].append(weighted_precision)
        metrics_dict['num_labels'].append(np.sum(t_outputs))

    return metrics_dict
