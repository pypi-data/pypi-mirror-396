from sklearn.preprocessing import MultiLabelBinarizer
from unittest.mock import patch

import numpy as np
import pandas as pd
import unittest

from azureml.automl.dnn.nlp.classification.multilabel.model_wrapper import ModelWrapper

try:
    import torch
    has_torch = True
except ImportError:
    has_torch = False


class MockTextDataset(torch.utils.data.Dataset):
    def __init__(self, size, num_labels):
        # Inputs created using BertTokenizer('this is a sentence')
        self.inputs = {'input_ids': [101, 2023, 2003, 1037, 6251, 102],
                       'token_type_ids': [0, 0, 0, 0, 0, 0],
                       'attention_mask': [1, 1, 1, 1, 1, 1]}
        self.dataset_size = size
        self.num_labels = num_labels

    def __len__(self):
        return self.dataset_size

    def __getitem__(self, index):
        return {
            'input_ids': torch.tensor(self.inputs['input_ids'], dtype=torch.long),
            'attention_mask': torch.tensor(self.inputs['attention_mask'], dtype=torch.long),
            'token_type_ids': torch.tensor(self.inputs['token_type_ids'], dtype=torch.long)
        }


class MockModel(torch.nn.Module):
    def __init__(self, num_labels):
        super(MockModel, self).__init__()
        self.num_labels = num_labels
        self.n_forward_called = 0

    def forward(self, input_ids, attention_mask, token_type_ids):
        self.n_forward_called = self.n_forward_called + 1
        return torch.rand(input_ids.shape[0], self.num_labels)


@unittest.skipIf(not has_torch, "torch not installed")
@patch('azureml.automl.dnn.nlp.classification.multilabel.model_wrapper.MultilabelDatasetWrapper')
def test_predict_proba(mock_dataset_wrapper):
    mock_dataset_wrapper.return_value = MockTextDataset(5, 2)  # set wrapped dataset
    model = MockModel(2)
    y_transformer = MultiLabelBinarizer()
    y_transformer.fit([["label0", "label1"]])
    wrapper = ModelWrapper(model=model,
                           tokenizer="some_tokenizer",
                           training_configuration="some_training_configuration",
                           y_transformer=y_transformer)
    expected_proba = np.array([[0.59456366, 0.72298276],
                               [0.5963906, 0.6458611],
                               [0.56379354, 0.6886127],
                               [0.71925545, 0.53324735],
                               [0.7180072, 0.6441861]], dtype=np.float32)
    output = wrapper.predict_proba("some text data")
    assert model.n_forward_called == 1
    assert len(output) == 5
    assert np.array_equal(expected_proba, output)


@unittest.skipIf(not has_torch, "torch not installed")
def test_predict():
    data = pd.DataFrame({"text": ["some data input"]})
    model = MockModel(2)
    y_transformer = MultiLabelBinarizer()
    y_transformer.fit([["label0", "label1"]])
    expected_labels = [("label0", "label1")] * 5
    wrapper = ModelWrapper(model, "some_tokenizer", "some_dataset_language", y_transformer)
    datawrapper = "azureml.automl.dnn.nlp.classification.multilabel.model_wrapper.MultilabelDatasetWrapper"
    with patch(datawrapper, return_value=MockTextDataset(5, 2)):
        output = wrapper.predict(data)
    assert len(output) == 5
    assert output == expected_labels
