# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Model Wrapper class to encapsulate automl model functionality"""
from scipy.special import softmax
from transformers import AutoTokenizer
from transformers.trainer import Trainer
from transformers.training_args import TrainingArguments
from transformers.data.data_collator import default_data_collator

import pandas as pd
import numpy as np
import tempfile
import torch

from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import MulticlassDatasetWrapper
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration


class ModelWrapper:
    """Class to wrap AutoML NLP models in the AutoMLTransformer interface"""

    def __init__(self,
                 model: torch.nn.Module,
                 label_list: np.ndarray,
                 tokenizer: AutoTokenizer,
                 training_configuration: TrainingConfiguration):
        """
        Transform the input data into outputs tensors from model

        :param model: the model to wrap.
        :param label_list: the list of labels from union of train and valid datasets
        :param tokenizer: the tokenizer for the data.
        :param training_configuration: a collection of parameters to dictate the training procedure.
        """
        super().__init__()
        self.model = model.to("cpu")
        self.tokenizer = tokenizer
        self.classes_ = label_list
        self.training_configuration = training_configuration

    def predict(self, X: pd.DataFrame):
        """
        Predict output labels for text datasets

        :param X: pandas dataframe in the same format as training data, without label columns
        :return: list of output labels equal to the size of X
        """
        pred_probas = self.predict_proba(X)
        preds = np.argmax(pred_probas, axis=1)
        predicted_labels = [self.classes_[cls_idx] for cls_idx in preds]
        return predicted_labels

    def predict_proba(self,
                      X: pd.DataFrame):
        """
        Output prediction probabilities for input text dataset.

        :param X: Pandas DataFrame in the same format as training data, without label columns.
        :return: Class-wise prediction probabilities.
        """
        dataset = MulticlassDatasetWrapper(X,
                                           self.classes_,
                                           self.tokenizer,
                                           self.training_configuration,
                                           label_column_name=None)
        with tempfile.TemporaryDirectory() as td:
            trainer = Trainer(args=TrainingArguments(output_dir=td),
                              model=self.model,
                              data_collator=default_data_collator)
            predictions = trainer.predict(test_dataset=dataset).predictions
        return softmax(predictions, axis=1)
