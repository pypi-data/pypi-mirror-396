# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility functions to load the final model and y_transformer during inferencing"""
import logging
import ast
import pandas as pd

from sklearn.preprocessing import MultiLabelBinarizer
from typing import Optional

_logger = logging.getLogger(__name__)


def get_y_transformer(
    train_df: pd.DataFrame,
    val_df: Optional[pd.DataFrame],
    label_column_name: str
) -> MultiLabelBinarizer:
    """
    Obtain labels transformer

    :param train_df: Training DataFrame
    :param val_df: Validation DataFrame
    :param label_column_name: Name/title of the label column
    :return: label transformer
    """
    # Combine both dataframes if val_df exists
    if val_df is not None:
        combined_df = pd.concat([train_df, val_df])
    else:
        combined_df = train_df

    # Get combined label column
    combined_label_col = combined_df[label_column_name].apply(ast.literal_eval)
    combined_label_col = [[str(x) for x in item] for item in combined_label_col]

    y_transformer = MultiLabelBinarizer(sparse_output=True)
    y_transformer.fit(combined_label_col)

    return y_transformer
