from unittest.mock import patch, Mock

import numpy as np
import torch
import unittest

from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import MalformedNerInferenceInput, \
    NerInferenceTypeMismatch
from azureml.automl.dnn.nlp.common.model_parameters import DEFAULT_NLP_PARAMETERS, DEFAULT_NER_PARAMETERS
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration
from azureml.automl.dnn.nlp.ner.model_wrapper import ModelWrapper

from ..mocks import get_local_tokenizer


class TestModelWrapper(unittest.TestCase):
    def setUp(self) -> None:
        settings = DEFAULT_NLP_PARAMETERS.copy()
        settings.update(DEFAULT_NER_PARAMETERS)
        self.training_configuration = TrainingConfiguration(settings, _internal=True)

    @patch('azureml.automl.dnn.nlp.ner.model_wrapper.ModelWrapper.predict_proba')
    def test_predict(self, mock_predict_proba):
        mock_predict_proba.return_value = "Monitor B-TECH 0.999\narms I-TECH 0.999\nare O 0.945\nnice O 0.984\n\n" \
                                          "But O 0.999\nthey O 0.999\nare O 0.943\nexpensive O 0.935\n"
        wrapped_model = ModelWrapper(model=Mock(),
                                     label_list=["O", "B-TECH", "I-TECH"],
                                     tokenizer="some tokenizer",
                                     training_configuration=self.training_configuration)
        preds = wrapped_model.predict("input string")

        expected_preds = ["Monitor B-TECH\narms I-TECH\nare O\nnice O\n\nBut O\nthey O\nare O\nexpensive O\n"]
        self.assertEqual(expected_preds, preds)

    def test_predict_raises_on_malformed_input(self):
        wrapped_model = ModelWrapper(model=Mock(),
                                     label_list=[],
                                     tokenizer="some tokenizer",
                                     training_configuration=self.training_configuration)
        with self.assertRaises(DataException) as e:
            wrapped_model.predict(np.array(["Too many", "inputs in list"]))
        self.assertEqual(e.exception.error_code, MalformedNerInferenceInput.__name__)

    def test_predict_raises_on_type_mismatch(self):
        wrapped_model = ModelWrapper(model=Mock(),
                                     label_list=[],
                                     tokenizer="some tokenizer",
                                     training_configuration=self.training_configuration)
        with self.assertRaises(DataException) as e:
            wrapped_model.predict(np.array([0]))  # Single element, but not a string.
        self.assertEqual(e.exception.error_code, NerInferenceTypeMismatch.__name__)

        with self.assertRaises(DataException) as e:
            wrapped_model.predict(0)  # The type is neither a numpy array nor a string.
        self.assertEqual(e.exception.error_code, NerInferenceTypeMismatch.__name__)

    @patch('azureml.automl.dnn.nlp.ner.model_wrapper.Trainer.predict')
    def test_predict_proba(self, mock_predict):
        label_ids = np.array([-100, 0, 0, 0, -100, 0, 0, -100] + [-100] * 120
                             + [-100, 0, 0, 0, 0, -100, -100, 0] + [-100] * 120).reshape((2, 128))
        preds = np.random.rand(2, 128, 2)
        # Random values where ignore tokens are; intentional values elsewhere.
        preds[0, 1:4, :] = np.log([[0.90, 0.10],
                                   [0.90, 0.10],
                                   [0.80, 0.20]])
        preds[0, 5:7, :] = np.log([[0.85, 0.15],
                                   [0.75, 0.25]])
        preds[1, 1:5, :] = np.log([[0.15, 0.85],
                                   [0.95, 0.05],
                                   [0.60, 0.40],
                                   [0.10, 0.90]])
        preds[1, 7, :] = np.log([0.90, 0.10])
        mock_predict.return_value = preds, label_ids, {}
        test_input = "Double\ndouble\ntoil\nand\ntrouble\n\nFire\nburn\nand\ncauldron\nbubble\n"
        mock_model = Mock(spec=torch.nn.Module, hf_device_map=None)
        mock_model.to.return_value = mock_model  # persists through device casting.
        wrapped_model = ModelWrapper(model=mock_model,
                                     label_list=["O", "B-NOUN"],
                                     tokenizer=get_local_tokenizer(),
                                     training_configuration=self.training_configuration)

        expected_pred_probas = "Double O 0.900\ndouble O 0.900\ntoil O 0.800\nand O 0.850\ntrouble O 0.750\n\n" \
                               "Fire B-NOUN 0.850\nburn O 0.950\nand O 0.600\ncauldron B-NOUN 0.900\nbubble O 0.900"
        pred_probas = wrapped_model.predict_proba(test_input)
        self.assertEqual(expected_pred_probas, pred_probas)
