from unittest.mock import MagicMock, patch

import os
import pytest
import numpy as np
import unittest

from azureml.automl.core.shared.constants import Metric
from azureml.automl.core.shared.exceptions import ValidationException
from azureml.automl.dnn.nlp.common.constants import OutputLiterals, SystemSettings, TrainingInputLiterals
from azureml.automl.dnn.nlp.common.model_parameters import DEFAULT_NLP_PARAMETERS
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration
from azureml.automl.dnn.nlp.ner.trainer import NERPytorchTrainer

from ..mocks import ner_trainer_mock


@pytest.mark.usefixtures('new_clean_dir')
class NERTrainerTests(unittest.TestCase):
    """Tests for NER trainer."""
    @pytest.fixture(autouse=True)
    def _before_each(self):
        settings = DEFAULT_NLP_PARAMETERS.copy()
        settings.update({TrainingInputLiterals.MODEL_NAME_OR_PATH: "some path",
                         TrainingInputLiterals.TOKENIZER_NAME_OR_PATH: "some tokenizer path",
                         TrainingInputLiterals.FINETUNING_TASK: "ner",
                         TrainingInputLiterals.USE_MEMS_EVAL: False})
        self.training_configuration = TrainingConfiguration(settings, _internal=True)
        yield

    @patch("azureml.automl.dnn.nlp.ner.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoConfig.from_pretrained")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoModelForTokenClassification.from_pretrained")
    def test_train_valid(
            self,
            model_factory_mock,
            config_factory_mock,
            trainer_mock
    ):
        # Trainer mock
        mock_trainer = ner_trainer_mock()
        trainer_mock.return_value = mock_trainer

        # Prepare input params for trainer
        train_dataset = MagicMock()
        eval_dataset = MagicMock()
        label_list = ["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]
        output_dir = OutputLiterals.OUTPUT_DIR
        trainer = NERPytorchTrainer(training_configuration=self.training_configuration,
                                    label_list=label_list,
                                    output_dir=output_dir)

        # train
        assert model_factory_mock.call_args[0][0] == "some path"
        trainer.train(train_dataset, eval_dataset)
        trainer.trainer.train.assert_called_once()
        trainer.trainer.save_model.assert_called_once()
        trainer.trainer.save_state.assert_called_once()

        # valid
        results = trainer.validate(eval_dataset)
        trainer.trainer.evaluate.assert_called_once()
        assert results is not None
        for primary_metric in Metric.TEXT_NER_PRIMARY_SET:
            assert primary_metric in results

    @patch("azureml.automl.dnn.nlp.ner.trainer.DistributedTrainer")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoConfig.from_pretrained")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoModelForTokenClassification.from_pretrained")
    def test_distributed_trainer(
            self,
            model_factory_mock,
            config_factory_mock,
            distributed_trainer_mock
    ):
        # Trainer mock
        mock_trainer = ner_trainer_mock()
        distributed_trainer_mock.return_value = mock_trainer

        # Prepare input params for trainer
        train_dataset = MagicMock()
        label_list = ["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]
        output_dir = OutputLiterals.OUTPUT_DIR
        trainer = NERPytorchTrainer(
            training_configuration=self.training_configuration,
            label_list=label_list,
            output_dir=output_dir,
            enable_distributed=True
        )

        trainer.train(train_dataset, MagicMock())
        mock_trainer.train.assert_called_once()

    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoConfig.from_pretrained")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoModelForTokenClassification.from_pretrained")
    def test_validation_without_train(self, model_factory_mock, config_factory_mock):
        # Prepare input params
        eval_dataset = MagicMock()
        label_list = ["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]
        output_dir = OutputLiterals.OUTPUT_DIR
        trainer = NERPytorchTrainer(training_configuration=self.training_configuration,
                                    label_list=label_list,
                                    output_dir=output_dir)

        with self.assertRaises(ValidationException):
            trainer.validate(eval_dataset)

        assert trainer.trainer is None

    @patch('azureml.automl.dnn.nlp.ner.trainer.os.path.exists')
    @patch('azureml.automl.dnn.nlp.ner.trainer.ORTDeepspeedTrainer')
    @patch('azureml.automl.dnn.nlp.ner.trainer.AutoConfig.from_pretrained')
    @patch('azureml.automl.dnn.nlp.ner.trainer.AutoModelForTokenClassification.from_pretrained')
    @patch('azureml.automl.dnn.nlp.common._utils.TrainingArguments')
    def test_ort_trainer(self,
                         training_arguments,
                         model_factory_mock,
                         config_factory_mock,
                         ort_trainer_mock,
                         mock_path_check):
        trainer = NERPytorchTrainer(training_configuration=self.training_configuration,
                                    label_list=np.array(["O", "B-MISC", "I-MISC", "B-PER", "I-PER"]),
                                    output_dir="output-dir",
                                    enable_distributed_ort_ds=True)
        mock_path_check.side_effect = [False, True]
        # ORT trainer without deepspeed enabled
        trainer.train(MagicMock(), MagicMock())
        assert ort_trainer_mock.call_count == 1
        assert training_arguments.call_args[1]['deepspeed'] is None
        assert training_arguments.call_args[1]['fp16'] is False

        # ORT trainer with deepspeed enabled
        trainer.train(MagicMock(), MagicMock())
        assert ort_trainer_mock.call_count == 2
        assert training_arguments.call_args[1]['deepspeed'] == SystemSettings.DEEP_SPEED_CONFIG
        assert training_arguments.call_args[1]['fp16'] is True
        assert model_factory_mock.call_count == 3
        model_file = os.path.join(OutputLiterals.OUTPUT_DIR, OutputLiterals.PT_MODEL_BIN_FILE_NAME)
        assert model_factory_mock.call_args_list[2][0][0] == model_file
