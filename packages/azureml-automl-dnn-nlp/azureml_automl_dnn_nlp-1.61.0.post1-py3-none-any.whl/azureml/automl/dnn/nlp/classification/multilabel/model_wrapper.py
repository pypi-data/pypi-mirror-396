# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Model Wrapper class to encapsulate automl model functionality"""
from scipy.special import expit
from sklearn.preprocessing import MultiLabelBinarizer
from transformers.tokenization_utils import PreTrainedTokenizer
from transformers.trainer import Trainer
from transformers.training_args import TrainingArguments

import numpy as np
import pandas as pd
import tempfile
import torch

from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import MultilabelDatasetWrapper
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration


class ModelWrapper:
    """Class to wrap AutoML NLP models in the AutoMLTransformer interface"""

    def __init__(self,
                 model: torch.nn.Module,
                 tokenizer: PreTrainedTokenizer,
                 training_configuration: TrainingConfiguration,
                 y_transformer: MultiLabelBinarizer):
        """
        Transform the input data into outputs tensors from model

        :param model: Trained model
        :param tokenizer: Tokenizer used to tokenize text data during training
        :param training_configuration: a collection of parameters to dictate the training procedure.
        :param y_transformer: Fitted MultiLabelBinarizer
        """
        super().__init__()
        self.model = model.to(torch.device("cpu"))
        self.tokenizer = tokenizer
        self.training_configuration = training_configuration
        self.y_transformer = y_transformer
        self.classes_ = y_transformer.classes_

    def predict_proba(self,
                      X: pd.DataFrame) -> np.ndarray:
        """
        Helper function for transforming the input data into outputs tensors using model

        :param X: pandas dataframe in the same format as the training data
        :return: (n_rows, n_labels) numpy array of prediction probabilities
        """
        dataset = MultilabelDatasetWrapper(X,
                                           self.tokenizer,
                                           self.training_configuration,
                                           label_column_name=None,
                                           y_transformer=None)  # set label-related values to None, for inference.
        with tempfile.TemporaryDirectory() as td:
            trainer = Trainer(args=TrainingArguments(output_dir=td),
                              model=self.model)
            predictions = trainer.predict(test_dataset=dataset).predictions
        return expit(predictions)

    def predict(self,
                X: pd.DataFrame,
                threshold: float = 0.5):
        """
        Predict output labels for text datasets

        :param X: pandas dataframe in the same format as training data, without label columns
        :param threshold: model output threshold at which labels are selected
        :return: returns a list of tuples representing the predicted labels
        """
        predict_probas = self.predict_proba(X)  # predict_proba's output shape is (n_rows, n_labels)
        return self.y_transformer.inverse_transform(predict_probas > threshold)
