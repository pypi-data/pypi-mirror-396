from tests.mocks import aml_dataset_mock, multilabel_trainer_mock
from unittest.mock import MagicMock, patch, Mock

import os
import pandas as pd
import pytest

from azureml.automl.core.shared.constants import Tasks
from azureml.automl.dnn.nlp.classification.io.read.dataloader import load_and_validate_multilabel_dataset
from azureml.automl.dnn.nlp.classification.multilabel.trainer import PytorchTrainer
from azureml.automl.dnn.nlp.common.constants import \
    ModelNames, SystemSettings, TrainingInputLiterals, OutputLiterals
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration
from azureml.automl.dnn.nlp.common.model_parameters import DEFAULT_NLP_PARAMETERS, DEFAULT_MULTILABEL_PARAMETERS

DEFAULT_USER_SETTINGS = {**DEFAULT_NLP_PARAMETERS, **DEFAULT_MULTILABEL_PARAMETERS,
                         TrainingInputLiterals.MODEL_NAME: ModelNames.BERT_BASE_UNCASED,
                         TrainingInputLiterals.MODEL_NAME_OR_PATH: "some_path",
                         TrainingInputLiterals.TOKENIZER_NAME_OR_PATH: "some_tokenizer_path"}


@patch("azureml.automl.dnn.nlp.classification.multilabel.trainer.AutoModelForSequenceClassification.from_pretrained")
@patch("azureml.automl.dnn.nlp.classification.multilabel.trainer.AutoTokenizer.from_pretrained")
@patch("azureml.automl.dnn.nlp.classification.multilabel.trainer.AutoConfig.from_pretrained")
def test_initialization_variables(config_factory_mock, tokenizer_factory_mock, model_factory_mock):
    PytorchTrainer(TrainingConfiguration(DEFAULT_USER_SETTINGS.copy(), _internal=True), 2)


@pytest.mark.usefixtures('MultilabelDatasetTester')
@pytest.mark.usefixtures('MultilabelValDatasetTester')
@pytest.mark.parametrize('multiple_text_column', [True, False])
@pytest.mark.parametrize('enable_distributed', [True, False])
@patch("azureml.automl.dnn.nlp.classification.multilabel.trainer.AutoModelForSequenceClassification.from_pretrained")
@patch("azureml.automl.dnn.nlp.classification.multilabel.trainer.AutoTokenizer.from_pretrained")
@patch("azureml.automl.dnn.nlp.classification.multilabel.trainer.AutoConfig.from_pretrained")
@patch("azureml.automl.dnn.nlp.classification.multilabel.trainer.Trainer")
@patch("azureml.automl.dnn.nlp.classification.multilabel.trainer.DistributedTrainer")
@patch("azureml.core.Dataset.get_by_id")
def test_train(get_by_id_mock, distributed_trainer_mock, trainer_mock,
               config_factory_mock, tokenizer_factory_mock, model_factory_mock,
               MultilabelDatasetTester, MultilabelValDatasetTester, enable_distributed):
    train_df = MultilabelDatasetTester.get_data().copy()
    validation_df = MultilabelValDatasetTester.get_data().copy()
    label_column_name = "labels_col"
    concat_df = pd.concat([train_df, validation_df], ignore_index=True)
    mock_aml_dataset = aml_dataset_mock(concat_df)
    get_by_id_mock.return_value = mock_aml_dataset
    aml_workspace_mock = MagicMock()
    automl_settings = dict()
    automl_settings['dataset_id'] = 'mock_id'
    automl_settings['validation_dataset_id'] = 'mock_validation_id'

    training_configuration = TrainingConfiguration(DEFAULT_USER_SETTINGS.copy(), _internal=True)

    training_set, validation_set, _, train_label_list, label_list, _, _ = load_and_validate_multilabel_dataset(
        aml_workspace_mock, "data_dir", label_column_name, Mock(), automl_settings, training_configuration
    )

    trainer = PytorchTrainer(training_configuration, 2, enable_distributed=enable_distributed)

    # trainer mock
    mock_trainer = multilabel_trainer_mock(len(concat_df))
    distributed_mock_trainer = multilabel_trainer_mock(len(concat_df))
    trainer_mock.return_value = mock_trainer
    distributed_trainer_mock.return_value = distributed_mock_trainer

    trainer.train(training_set, validation_set)

    assert trainer.training_args.per_device_train_batch_size == \
           DEFAULT_USER_SETTINGS[TrainingInputLiterals.TRAIN_BATCH_SIZE]
    assert trainer.training_args.num_train_epochs == \
           DEFAULT_USER_SETTINGS[TrainingInputLiterals.NUM_TRAIN_EPOCHS]

    # train function
    trainer.trainer.train.assert_called_once()
    trainer.trainer.save_model.assert_called_once()
    trainer.trainer.save_state.assert_called_once()

    if enable_distributed is True:
        assert trainer.trainer is distributed_mock_trainer


@pytest.mark.usefixtures('MultilabelDatasetTester')
@pytest.mark.usefixtures('MultilabelValDatasetTester')
@pytest.mark.parametrize('multiple_text_column', [True, False])
@pytest.mark.parametrize('enable_distributed', [True, False])
@patch("azureml.automl.dnn.nlp.classification.multilabel.trainer.AutoModelForSequenceClassification.from_pretrained")
@patch("azureml.automl.dnn.nlp.classification.multilabel.trainer.AutoTokenizer.from_pretrained")
@patch("azureml.automl.dnn.nlp.classification.multilabel.trainer.AutoConfig.from_pretrained")
@patch("azureml.automl.dnn.nlp.classification.multilabel.trainer.Trainer")
@patch("azureml.automl.dnn.nlp.classification.multilabel.trainer.DistributedTrainer")
@patch("azureml.core.Dataset.get_by_id")
def test_validate(get_by_id_mock, distributed_trainer_mock, trainer_mock,
                  config_factory_mock, tokenizer_factory_mock, model_factory_mock,
                  MultilabelDatasetTester, MultilabelValDatasetTester, enable_distributed):
    # validate function
    train_df = MultilabelDatasetTester.get_data().copy()
    validation_df = MultilabelValDatasetTester.get_data().copy()
    concat_df = pd.concat([train_df, validation_df], ignore_index=True)
    mock_aml_dataset = aml_dataset_mock(concat_df)
    get_by_id_mock.return_value = mock_aml_dataset

    label_column_name = "labels_col"

    aml_workspace_mock = MagicMock()
    automl_settings = dict()
    automl_settings['dataset_id'] = 'mock_id'
    automl_settings['validation_dataset_id'] = 'mock_validation_id'

    training_configuration = TrainingConfiguration(DEFAULT_USER_SETTINGS.copy(), _internal=True)

    training_set, validation_set, _, train_label_list, label_list, _, _ = load_and_validate_multilabel_dataset(
        aml_workspace_mock, "data_dir", label_column_name, Mock(), automl_settings, training_configuration
    )

    trainer = PytorchTrainer(training_configuration, 2, enable_distributed=enable_distributed)
    mock_trainer = multilabel_trainer_mock(len(concat_df))
    distributed_mock_trainer = multilabel_trainer_mock(len(concat_df))
    trainer_mock.return_value = mock_trainer
    distributed_trainer_mock.return_value = distributed_mock_trainer

    trainer.train(training_set, validation_set)

    predictions, label_ids = trainer.validate(validation_set)
    trainer.trainer.predict.assert_called_once()
    assert predictions.shape[0] == (len(concat_df))
    assert label_ids.shape[0] == (len(concat_df))
    trainer.trainer.save_metrics.assert_called_once()


@patch('azureml.automl.dnn.nlp.common.training_configuration.ResourcePathResolver',
       return_value=Mock(model_name=ModelNames.BERT_BASE_UNCASED,
                         model_path="some_path",
                         tokenizer_path="some_tokenizer_path"))
@patch('azureml.automl.dnn.nlp.classification.multilabel.trainer.os.path.exists')
@patch('azureml.automl.dnn.nlp.classification.multilabel.trainer.ORTDeepspeedTrainer')
@patch('azureml.automl.dnn.nlp.classification.multilabel.trainer.AutoModelForSequenceClassification.from_pretrained')
@patch('azureml.automl.dnn.nlp.classification.multilabel.trainer.AutoTokenizer.from_pretrained')
@patch('azureml.automl.dnn.nlp.classification.multilabel.trainer.AutoConfig.from_pretrained')
@patch('azureml.automl.dnn.nlp.common._utils.TrainingArguments')
def test_ort_trainer(training_arguments, config_factory_mock, tokenizer_factory_mock, model_factory_mock,
                     ort_trainer_mock, mock_path_check, path_resolver_mock):
    trainer = PytorchTrainer(
        training_configuration=TrainingConfiguration.populate_from_scope(
            task_type=Tasks.TEXT_CLASSIFICATION_MULTILABEL,
            dataset_language="eng",
            automl_settings={}),
        num_label_cols=2,
        enable_distributed_ort_ds=True)
    mock_path_check.side_effect = [False, True]
    dataset = MagicMock()
    # ORT trainer without deepspeed enabled
    trainer.train(train_dataset=dataset, validation_dataset=dataset)
    assert ort_trainer_mock.call_count == 1
    assert training_arguments.call_args[1]['deepspeed'] is None
    assert training_arguments.call_args[1]['fp16'] is False

    # ORT trainer with deepspeed enabled
    trainer.train(train_dataset=dataset, validation_dataset=dataset)
    assert ort_trainer_mock.call_count == 2
    assert training_arguments.call_args[1]['deepspeed'] == SystemSettings.DEEP_SPEED_CONFIG
    assert training_arguments.call_args[1]['fp16'] is True
    assert tokenizer_factory_mock.call_args[0][0] == "some_tokenizer_path"
    assert model_factory_mock.call_count == 3
    model_file = os.path.join(OutputLiterals.OUTPUT_DIR, OutputLiterals.PT_MODEL_BIN_FILE_NAME)
    assert model_factory_mock.call_args_list[2][0][0] == model_file
