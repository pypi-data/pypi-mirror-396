from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd
import pytest

from azureml.automl.core.shared.constants import Tasks
from azureml.automl.dnn.nlp.classification.io.read.dataloader import load_and_validate_multiclass_dataset
from azureml.automl.dnn.nlp.classification.multiclass.trainer import TextClassificationTrainer
from azureml.automl.dnn.nlp.common.constants import ModelNames, SystemSettings, TrainingDefaultSettings
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration
from ...mocks import multiclass_trainer_mock, aml_dataset_mock


@pytest.mark.usefixtures('MulticlassDatasetTester')
@pytest.mark.usefixtures('MulticlassValDatasetTester')
@pytest.mark.usefixtures('MulticlassTokenizer')
@pytest.mark.parametrize('multiple_text_column', [True, False])
@pytest.mark.parametrize('include_label_col', [True])
@pytest.mark.parametrize('enable_distributed', [True, False])
@pytest.mark.parametrize('is_long_range_text', [True, False])
@pytest.mark.parametrize('enable_long_range_text', [True, False])
class TestTextClassificationTrainerTests:
    """Tests for Text Classification trainer."""
    @patch("azureml.automl.dnn.nlp.common.training_configuration.ResourcePathResolver",
           return_value=Mock(model_name=ModelNames.BERT_BASE_CASED,
                             model_path="some_path",
                             tokenizer_path="some_tokenizer_path"))
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer"
           ".AutoModelForSequenceClassification.from_pretrained")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoTokenizer.from_pretrained")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoConfig.from_pretrained")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.DistributedTrainer")
    @patch("azureml.core.Dataset.get_by_id")
    def test_train_valid(self,
                         get_by_id_mock,
                         distributed_trainer_mock,
                         trainer_mock,
                         config_factory_mock,
                         tokenizer_factory_mock,
                         model_factory_mock,
                         path_resolver_mock,
                         MulticlassDatasetTester,
                         MulticlassValDatasetTester,
                         enable_distributed,
                         MulticlassTokenizer,
                         is_long_range_text,
                         enable_long_range_text):
        train_df = MulticlassDatasetTester.get_data(is_long_range_text).copy()
        validation_df = MulticlassValDatasetTester.get_data(is_long_range_text).copy()
        label_column_name = "labels_col"
        concat_df = pd.concat([train_df, validation_df], ignore_index=True)
        mock_aml_dataset = aml_dataset_mock(concat_df)
        get_by_id_mock.return_value = mock_aml_dataset
        aml_workspace_mock = MagicMock()
        automl_settings = dict()
        automl_settings['dataset_id'] = 'mock_id'
        automl_settings['validation_dataset_id'] = 'mock_validation_id'
        tokenizer = MagicMock()
        tokenizer.name_or_path = "some_tokenizer_path"
        tokenizer_factory_mock.return_value = tokenizer
        training_configuration = TrainingConfiguration.populate_from_scope(task_type=Tasks.TEXT_CLASSIFICATION,
                                                                           dataset_language="eng",
                                                                           automl_settings={})
        training_set, validation_set, label_list, train_label_list, _ = \
            load_and_validate_multiclass_dataset(workspace=aml_workspace_mock,
                                                 data_dir="data_dir",
                                                 label_column_name=label_column_name,
                                                 tokenizer=MulticlassTokenizer,
                                                 automl_settings=automl_settings,
                                                 training_configuration=training_configuration,
                                                 enable_long_range_text=enable_long_range_text)

        trainer = TextClassificationTrainer(train_label_list=train_label_list,
                                            label_list=label_list,
                                            training_configuration=training_configuration,
                                            enable_distributed=enable_distributed)

        # trainer mock
        mock_trainer = multiclass_trainer_mock(len(concat_df))
        distributed_mock_trainer = multiclass_trainer_mock(len(concat_df))
        trainer_mock.return_value = mock_trainer
        distributed_trainer_mock.return_value = distributed_mock_trainer

        trainer.train(training_set, validation_dataset=validation_set)
        if enable_long_range_text and is_long_range_text:
            assert training_set.max_seq_length == TrainingDefaultSettings.LONG_RANGE_MAX
            assert trainer.training_args.gradient_accumulation_steps == 2
            assert trainer.training_args.per_device_train_batch_size == 16
        else:
            assert training_set.max_seq_length == TrainingDefaultSettings.DEFAULT_SEQ_LEN
            assert trainer.training_args.gradient_accumulation_steps == 1
            assert trainer.training_args.per_device_train_batch_size == 32

        # train function
        trainer.trainer.train.assert_called_once()
        trainer.trainer.save_model.assert_called_once()
        trainer.trainer.save_state.assert_called_once()

        # validate function
        predictions = trainer.validate(validation_set)
        trainer.trainer.predict.assert_called_once()
        assert predictions.shape == (len(concat_df), len(label_list))
        trainer.trainer.save_metrics.assert_called_once()
        assert tokenizer_factory_mock.call_args[0][0] == "some_tokenizer_path"
        assert config_factory_mock.call_args[0][0] == "some_tokenizer_path"
        assert model_factory_mock.call_args[0][0] == "some_path"
        if enable_distributed is True:
            assert trainer.trainer is distributed_mock_trainer


@patch('azureml.automl.dnn.nlp.common.training_configuration.ResourcePathResolver',
       return_value=Mock(model_name=ModelNames.BERT_BASE_CASED,
                         model_path="some_path",
                         tokenizer_path="some_tokenizer_path"))
@patch('azureml.automl.dnn.nlp.classification.multiclass.trainer.np.save')
@patch('azureml.automl.dnn.nlp.classification.multiclass.trainer.os.path.exists')
@patch('azureml.automl.dnn.nlp.classification.multiclass.trainer.ORTDeepspeedTrainer')
@patch('azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoConfig.from_pretrained')
@patch('azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoModelForSequenceClassification.from_pretrained')
@patch('azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoTokenizer.from_pretrained')
@patch('azureml.automl.dnn.nlp.common._utils.TrainingArguments')
def test_ort_trainer(training_arguments,
                     tokenizer_factory_mock,
                     model_factory_mock,
                     config_factory_mock,
                     ort_trainer_mock,
                     mock_path_check,
                     mock_np_save,
                     path_resolver_mock):
    trainer = TextClassificationTrainer(train_label_list=np.arange(5),
                                        label_list=np.arange(5),
                                        training_configuration=TrainingConfiguration.populate_from_scope(
                                            task_type=Tasks.TEXT_CLASSIFICATION,
                                            dataset_language="eng",
                                            automl_settings={}),
                                        enable_distributed_ort_ds=True)
    mock_path_check.side_effect = [False, True, True, True]
    dataset = MagicMock(max_seq_length=128)
    # ORT trainer without deepspeed enabled
    trainer.train(train_dataset=dataset, validation_dataset=dataset)
    assert ort_trainer_mock.call_count == 1
    assert training_arguments.call_args[1]['deepspeed'] is None
    assert training_arguments.call_args[1]['fp16'] is False
    assert ort_trainer_mock.return_value.save_metrics.call_count == 1

    # ORT trainer with deepspeed enabled
    trainer.train(train_dataset=dataset, validation_dataset=dataset)
    assert ort_trainer_mock.call_count == 2
    assert training_arguments.call_args[1]['deepspeed'] == SystemSettings.DEEP_SPEED_CONFIG
    assert training_arguments.call_args[1]['fp16'] is True
    assert ort_trainer_mock.return_value.save_metrics.call_count == 2
