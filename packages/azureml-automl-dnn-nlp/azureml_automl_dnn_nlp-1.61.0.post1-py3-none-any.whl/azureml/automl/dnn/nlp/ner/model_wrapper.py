# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Model Wrapper class to encapsulate automl model functionality"""
from typing import List, Union

from transformers.data.data_collator import default_data_collator
from transformers.tokenization_utils import PreTrainedTokenizer
from transformers.trainer import Trainer
from transformers.training_args import TrainingArguments

import numpy as np
import re
import tempfile
import torch

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import MalformedNerInferenceInput, \
    NerInferenceTypeMismatch
from azureml.automl.dnn.nlp.common.constants import DataLiterals, Split, ValidationLiterals
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration
from azureml.automl.dnn.nlp.ner.io.read.dataset_wrapper import NerDatasetWrapper
from azureml.automl.dnn.nlp.ner.token_classification_metrics import TokenClassificationMetrics


class ModelWrapper:
    """Class to wrap AutoML NLP models in the AutoMLTransformer interface"""

    def __init__(self,
                 model: torch.nn.Module,
                 label_list: list,
                 tokenizer: PreTrainedTokenizer,
                 training_configuration: TrainingConfiguration):
        """
        Transform the input data into outputs tensors from model

        :param model: Trained model, preferably trained using HuggingFace trainer
        :param label_list: List of labels that the model was trained on
        :param tokenizer: PretrainedTokenizer used by the NerDatasetWrapper while training
        :param training_configuration: a collection of parameters to dictate the training procedure.
        """
        super().__init__()
        self.model = model.to("cpu")
        self.label_list = label_list
        self.tokenizer = tokenizer
        self.training_configuration = training_configuration

    def predict_proba(self, X: str) -> str:
        """
        Predict output labels and label confidences for text datasets.

        :param X: string of tokens in CoNLL format, without labels.
        :return: string of labeled X with label confidences, in CoNLL format.
        """
        dataset = NerDatasetWrapper(X,
                                    tokenizer=self.tokenizer,
                                    labels=self.label_list,
                                    training_configuration=self.training_configuration,
                                    mode=Split.test)

        token_classification_metrics = TokenClassificationMetrics(self.label_list)
        with tempfile.TemporaryDirectory() as td:
            trainer = Trainer(args=TrainingArguments(output_dir=td),
                              model=self.model,
                              data_collator=default_data_collator,
                              compute_metrics=token_classification_metrics.compute_metrics)
            raw_predictions, label_ids, metrics = trainer.predict(test_dataset=dataset)
            preds_list, _, preds_proba_list = \
                token_classification_metrics.align_predictions_with_proba(raw_predictions, label_ids)

        prediction_strings = []
        for idx in range(len(preds_list)):
            # Don't predict on ignored -DOCSTART- lines.
            if dataset.data[idx].startswith("-DOCSTART-"):
                prediction_strings.append(dataset.data[idx].strip())
            else:
                # dataset.data[idx] should be one multiline CoNLL example. In the labeled case, something like
                # `Hello O\nthere O`, and in the unlabeled case, `Hello\nthere`.
                words = []
                for item in dataset.data[idx].split("\n"):
                    if re.fullmatch(DataLiterals.NER_IGNORE_TOKENS_REGEX, item) is None:
                        match_groups = re.fullmatch(DataLiterals.NER_LINE_FORMAT, item)
                        if match_groups is None:
                            match_groups = re.fullmatch(DataLiterals.NER_UNLABELED_LINE_FORMAT, item)
                        words.append(match_groups[1])
                preds = preds_list[idx]
                pred_probas = preds_proba_list[idx]

                sample_str = "\n".join(["{} {} {:.3f}".format(item[0], item[1], item[2]) for item in
                                        zip(words, preds, pred_probas)])
                prediction_strings.append(sample_str)
        return "\n\n".join(prediction_strings)

    def predict(self, X: Union[np.ndarray, str]) -> List[str]:
        """
        Predict output labels for text datasets

        :param X: Single element numpy array containing the string of tokens in CoNLL format, without labels.
        :return: Single element python list containing string of labeled X, in CoNLL format.
        """
        if isinstance(X, np.ndarray):
            flattened_input = X.flatten()
            if flattened_input.shape != (1,):
                raise DataException._with_error(
                    AzureMLError.create(
                        MalformedNerInferenceInput,
                        list_length=len(X),
                        target=ValidationLiterals.DATA_EXCEPTION_TARGET
                    )
                )
            X = flattened_input[0]  # type: str

        if not isinstance(X, str):
            raise DataException._with_error(
                AzureMLError.create(
                    NerInferenceTypeMismatch,
                    bad_type=type(X),
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )

        predictions_with_probabilities = self.predict_proba(X)
        # Strip the probabilities, since they're not wanted in this case.
        examples = predictions_with_probabilities.split('\n\n')
        stripped_predictions = []
        for example in examples:
            # Go from 'SOCCER O 0.99934983' to 'SOCCER O'
            sample_str = "\n".join(
                [re.sub(r"([\S]+ (?:O|I-[\S]*|B-[\S]*)) \d+[.]?\d*\s*",
                        lambda match: match.group(1), ex) for ex in example.split('\n')]
            )
            stripped_predictions.append(sample_str)
        return ["\n\n".join(stripped_predictions)]
