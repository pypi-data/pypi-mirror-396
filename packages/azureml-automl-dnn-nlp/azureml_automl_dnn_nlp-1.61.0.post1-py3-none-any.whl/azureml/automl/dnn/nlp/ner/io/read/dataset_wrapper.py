# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Named entity recognition dataset wrapper class."""

import logging
import re

from torch import nn
from torch.utils.data.dataset import Dataset
from transformers.tokenization_utils import PreTrainedTokenizer
from typing import List

from azureml.automl.dnn.nlp.common.constants import DataLiterals, ModelNames, Split, TrainingInputLiterals
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration

logger = logging.getLogger(__name__)


class NerDatasetWrapper(Dataset):
    """This will be superseded by a framework-agnostic approach soon."""

    def __init__(
            self,
            data,
            tokenizer: PreTrainedTokenizer,
            labels: List[str],
            training_configuration: TrainingConfiguration,
            mode: Split = Split.train
    ):
        """
        Token classification dataset constructor func.

        :param data: the raw data to wrap.
        :param tokenizer: the tokenizer for this NER task.
        :param labels: the labels from union of training and validation sets.
        :param training_configuration: a collection of parameters to dictate the training procedure.
        :param mode: type of training.
        :return: None.
        """
        self.training_configuration = training_configuration

        if mode != Split.test:
            # Remove DOCSTART tokens meant to be ignored during training.
            data = data.replace("-DOCSTART- O\n\n", "")

        self.data = data.split("\n\n")

        self.tokenizer = tokenizer
        self.label_map = {label: i for i, label in enumerate(labels)}
        self.mode = mode

    def __len__(self):
        """Token classification dataset len func."""
        return len(self.data)

    def __getitem__(self, idx):
        """Token classification dataset getitem func."""

        tokens = self.data[idx].split("\n")
        words, labels = [], []
        for item in tokens:
            if re.fullmatch(DataLiterals.NER_IGNORE_TOKENS_REGEX, item) is None:
                match_groups = re.fullmatch(DataLiterals.NER_LINE_FORMAT, item) or re.fullmatch(
                    DataLiterals.NER_UNLABELED_LINE_FORMAT, item)
                words.append(match_groups[1])
                # if training, validating, or if test contains labels, read labels from the dataset
                # else append label which will be used to align predictions only
                # Using "O" for test to ensure that unseen label in the test set are handled gracefully
                labels.append(match_groups[2] if self.mode != Split.test else "O")

        tokenized = self.tokenizer(words,
                                   None,
                                   max_length=self.training_configuration[TrainingInputLiterals.MAX_SEQ_LENGTH],
                                   padding=self.training_configuration[TrainingInputLiterals.PADDING_STRATEGY],
                                   truncation=True,
                                   is_split_into_words=True)

        word_idx = 0
        token_idx = 0
        label_ids = []
        pad_id = int(nn.CrossEntropyLoss().ignore_index)
        token_budget = self.training_configuration[TrainingInputLiterals.MAX_SEQ_LENGTH] - 2  # Budget for CLS, SEP.
        while word_idx < len(words) and token_idx < token_budget:
            label_ids.append(self.label_map[labels[word_idx]])
            # TODO: Remove extra tokenization step if possible.
            num_toks = len(self.tokenizer.tokenize(words[word_idx]))
            # If word leads to multi-token expansion, pad for the remaining K-1 unlabeled sub-word tokens.
            label_ids.extend([pad_id] * (num_toks - 1))
            token_idx += num_toks
            word_idx += 1

        pad_array = []
        if len(label_ids) < token_budget:  # We need to pad to max length.
            pad_array = [pad_id] * (token_budget - len(label_ids))
        else:
            # Account for the edge case where sub-word padding makes label_ids be slightly too long.
            label_ids = label_ids[:token_budget]

        if self.training_configuration[TrainingInputLiterals.MODEL_NAME] in [ModelNames.XLNET_BASE_CASED,
                                                                             ModelNames.XLNET_LARGE_CASED]:
            label_ids = pad_array + label_ids + [pad_id, pad_id]
        else:
            label_ids = [pad_id] + label_ids + [pad_id] + pad_array
        tokenized["label_ids"] = label_ids

        return tokenized
