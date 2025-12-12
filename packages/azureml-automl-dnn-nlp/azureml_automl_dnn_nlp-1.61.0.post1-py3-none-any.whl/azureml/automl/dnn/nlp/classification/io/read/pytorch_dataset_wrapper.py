# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
#
# For DatasetWrappers:
#
# MIT License
#
# Copyright (c) 2020 Abhishek Kumar Mishra
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""DatasetWrapper classes for text tasks"""
from typing import Optional
from torch.utils.data import Dataset as PyTorchDataset
from transformers.tokenization_utils_base import PreTrainedTokenizerBase

import logging
import ast
import numpy as np
import pandas as pd
import torch

from azureml.automl.dnn.nlp.common._utils import concat_text_columns
from azureml.automl.dnn.nlp.common.constants import DataLiterals, TrainingInputLiterals
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration

_logger = logging.getLogger(__name__)


class MultilabelDatasetWrapper(PyTorchDataset):
    """Class for obtaining multilabel dataset to be passed into model."""

    def __init__(self,
                 dataframe: pd.DataFrame,
                 tokenizer: PreTrainedTokenizerBase,
                 training_configuration: TrainingConfiguration,
                 label_column_name=None,
                 y_transformer=None):
        """
        Init function definition

        :param dataframe: pd.DataFrame holding data to be passed
        :param tokenizer: tokenizer to be used to tokenize the data.
        :param training_configuration: a collection of parameters to dictate the training procedure.
        :param label_column_name: name/title of the label column
        :param y_transformer: Optional fitted MultiLabelBinarizer to transform the
                              Multilabel labels column to one-hot encoding
        :return: None.
        """
        self.training_configuration = training_configuration
        self.data = dataframe

        self.sparse_encoded_targets = None
        if label_column_name is not None:
            array_formatted_targets = self.data[label_column_name].apply(ast.literal_eval)
            self.sparse_encoded_targets = y_transformer.transform(
                np.array([[str(x) for x in item] for item in array_formatted_targets]))
        self.label_column_name = label_column_name

        self.tokenizer = tokenizer
        self.max_len = training_configuration[TrainingInputLiterals.MAX_SEQ_LENGTH]
        self.y_transformer = y_transformer

    def __len__(self):
        """Len function definition."""
        return len(self.data)

    def __getitem__(self, index):
        """Getitem function definition."""
        comment_text = concat_text_columns(self.data.iloc[index], self.data.columns, self.label_column_name)
        inputs = self.tokenizer(comment_text,
                                max_length=self.max_len,
                                padding=self.training_configuration[TrainingInputLiterals.PADDING_STRATEGY],
                                truncation=True)

        for tokenizer_key in inputs:
            inputs[tokenizer_key] = torch.tensor(inputs[tokenizer_key], dtype=torch.long)

        if self.sparse_encoded_targets is not None:
            labels = self.sparse_encoded_targets[index].toarray().astype(int)[0]
            # Multi-label loss function used in training procedure requires float-type labels.
            inputs[DataLiterals.LABEL_COLUMN] = torch.tensor(labels, dtype=torch.float)

        return inputs

    @property
    def labels(self) -> np.ndarray:
        """
        Get labels associated with this dataset.

        :return: numpy array of labels.
        """
        return self.sparse_encoded_targets.toarray().astype(int)


class MulticlassDatasetWrapper(PyTorchDataset):
    """
    Class for obtaining dataset to be passed into model for multi-class classification.
    """

    def __init__(self,
                 dataframe: pd.DataFrame,
                 label_list: np.ndarray,
                 tokenizer: PreTrainedTokenizerBase,
                 training_configuration: TrainingConfiguration,
                 label_column_name: Optional[str] = None):
        """
        Init function definition

        :param dataframe: pd.DataFrame holding data to be passed
        :param label_list: list of labels from union of training and validation data
        :param tokenizer: tokenizer to be used to tokenize the data
        :param training_configuration: a collection of parameters to dictate the training procedure.
        :param label_column_name: name/title of the label column
        """
        self.label_to_id = {v: i for i, v in enumerate(label_list)}
        self.tokenizer = tokenizer
        self.data = dataframe
        self.label_column_name = label_column_name
        self.padding = training_configuration[TrainingInputLiterals.PADDING_STRATEGY]
        self.max_seq_length = min(training_configuration[TrainingInputLiterals.MAX_SEQ_LENGTH],
                                  self.tokenizer.model_max_length)

    def __len__(self):
        """Len function definition."""
        return len(self.data)

    def __getitem__(self, index):
        """Getitem function definition."""
        sample = concat_text_columns(self.data.iloc[index], self.data.columns, self.label_column_name)
        tokenized = self.tokenizer(sample, padding=self.padding, max_length=self.max_seq_length, truncation=True)
        for tokenizer_key in tokenized:
            tokenized[tokenizer_key] = torch.tensor(tokenized[tokenizer_key], dtype=torch.long)

        if self.label_column_name is not None and self.label_to_id is not None and \
           self.label_column_name in self.data.columns:
            label = self.data[self.label_column_name].iloc[index]
            tokenized[DataLiterals.LABEL_COLUMN] = torch.tensor(self.label_to_id[label], dtype=torch.long)

        return tokenized

    @property
    def labels(self) -> np.ndarray:
        """
        Get labels associated with this dataset.

        :return: numpy array of labels.
        """
        return self.data[self.label_column_name].values
