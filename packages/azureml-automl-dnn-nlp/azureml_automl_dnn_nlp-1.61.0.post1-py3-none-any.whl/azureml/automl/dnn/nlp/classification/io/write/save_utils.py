# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility saving functions for multiclass/multilabel metrics and other training outputs."""
import logging
import os
import pandas as pd

from azureml.automl.dnn.nlp.common.constants import OutputLiterals

logger = logging.getLogger(__name__)


def save_metrics(metrics_dict):
    """
    Save a metrics to outputs directory.

    :param metrics_dict: Metrics produced using different thresholds
    :type metrics_dict: dictionary
    """
    os.makedirs(OutputLiterals.OUTPUT_DIR, exist_ok=True)
    metrics_path = os.path.join(OutputLiterals.OUTPUT_DIR, "metrics.csv")

    # Save metrics to csv
    metrics_df = pd.DataFrame(metrics_dict)
    metrics_df.to_csv(metrics_path, index=False)
    logger.info("Metrics saved")


def save_predicted_results(predicted_df: pd.DataFrame, file_name: str):
    """
    Save predicted output

    :param predicted_df: predicted output to save
    :param file_name: location to save
    :return:
    """
    os.makedirs(OutputLiterals.OUTPUT_DIR, exist_ok=True)
    predictions_path = os.path.join(OutputLiterals.OUTPUT_DIR, file_name)
    predicted_df.to_csv(predictions_path, index=False)
    logger.info("Prediction results saved")
