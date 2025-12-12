from unittest.mock import patch, Mock

import pickle
import unittest

from azureml.automl.core.shared.constants import Tasks
from azureml.automl.core.shared.exceptions import UserException
from azureml.automl.dnn.nlp.common.training_configuration import _NLPSettingParser, TrainingConfiguration
from azureml.automl.dnn.nlp.common.constants import ModelNames, TrainingInputLiterals


class TestNLPSettingParser(unittest.TestCase):
    def test_parser_raises_azure_compatible_exception(self):
        parser = _NLPSettingParser()
        with self.assertRaises(UserException):
            parser.error('')


@patch('azureml.automl.dnn.nlp.common.training_configuration.ResourcePathResolver',
       return_value=Mock(model_name="some model", model_path="some path",
                         tokenizer_path="some tokenizer path"))
@patch('azureml.automl.dnn.nlp.common.training_configuration.vars')
@patch('azureml.automl.dnn.nlp.common.training_configuration._NLPSettingParser.parse_known_args',
       return_value=({}, ()))
@patch('azureml.automl.dnn.nlp.common.training_configuration.NLPSettingsValidator.validate')
class TestTrainingConfiguration(unittest.TestCase):
    @patch('azureml.automl.dnn.nlp.common.training_configuration.DefaultParameterFactory')
    def test_populate_from_scope(self,
                                 mock_parameter_factory, skip_validation,
                                 skip_parse_args, mock_vars, mock_path_resolver):
        user_settings = {"some key": "some value"}
        mock_vars.return_value = user_settings
        training_configuration = TrainingConfiguration.populate_from_scope(task_type=Tasks.TEXT_CLASSIFICATION,
                                                                           dataset_language="eng",
                                                                           automl_settings={})
        # Resource paths gets set correctly from the path resolver
        self.assertEqual("some model", user_settings[TrainingInputLiterals.MODEL_NAME])
        self.assertEqual("some path", user_settings[TrainingInputLiterals.MODEL_NAME_OR_PATH])
        self.assertEqual("some tokenizer path", user_settings[TrainingInputLiterals.TOKENIZER_NAME_OR_PATH])

        # We delegate to the parameter factory to get the right default settings
        mock_parameter_factory.get.assert_called_once_with(task_type=Tasks.TEXT_CLASSIFICATION,
                                                           model_name="some model")
        # Override default settings with user settings
        mock_parameter_factory.get.return_value.update.assert_called_once_with(user_settings)

        # Finally, the user_settings object is what's used to back the training configuration object.
        self.assertEqual(mock_parameter_factory.get.return_value, training_configuration._settings_dict)

    @patch('azureml.automl.dnn.nlp.common.training_configuration.DefaultParameterFactory')
    def test_populate_from_scope_with_fixed_settings(self,
                                                     mock_parameter_factory, skip_validation,
                                                     skip_parse_args, mock_vars, mock_path_resolver):
        user_settings = {TrainingInputLiterals.LEARNING_RATE: '5e-5'}
        mock_vars.return_value = user_settings
        automl_settings = {TrainingInputLiterals.LEARNING_RATE: 5e-6,
                           TrainingInputLiterals.WARMUP_RATIO: 0.1,
                           TrainingInputLiterals.TRAIN_BATCH_SIZE: None}
        training_configuration = TrainingConfiguration.populate_from_scope(task_type=Tasks.TEXT_CLASSIFICATION,
                                                                           dataset_language="eng",
                                                                           automl_settings=automl_settings)
        # Check resource paths
        self.assertEqual("some model", user_settings[TrainingInputLiterals.MODEL_NAME])
        self.assertEqual("some path", user_settings[TrainingInputLiterals.MODEL_NAME_OR_PATH])
        self.assertEqual("some tokenizer path", user_settings[TrainingInputLiterals.TOKENIZER_NAME_OR_PATH])

        # We delegate to the parameter factory to get the right default settings
        mock_parameter_factory.get.assert_called_once_with(task_type=Tasks.TEXT_CLASSIFICATION,
                                                           model_name="some model")

        # Most importantly, the settings dictionary is updated as expected, accounting for the fixed parameters.
        self.assertEqual(5e-6, float(user_settings[TrainingInputLiterals.LEARNING_RATE]))
        self.assertEqual(0.1, float(user_settings[TrainingInputLiterals.WARMUP_RATIO]))
        self.assertFalse(TrainingInputLiterals.WEIGHT_DECAY in user_settings)
        self.assertFalse(TrainingInputLiterals.TRAIN_BATCH_SIZE in user_settings)

        self.assertEqual(mock_parameter_factory.get.return_value, training_configuration._settings_dict)

    def test_no_seq_len_multiplier_for_explicit_train_batch_size(self,
                                                                 skip_validation, skip_parse_args,
                                                                 mock_vars, mock_path_resolver):
        user_settings = {"training_batch_size": 32}
        mock_vars.return_value = user_settings
        TrainingConfiguration.populate_from_scope(task_type=Tasks.TEXT_CLASSIFICATION_MULTILABEL,
                                                  dataset_language="eng",
                                                  automl_settings={})
        self.assertFalse(user_settings[TrainingInputLiterals.USE_SEQ_LEN_MULTIPLIER])

    def test_no_seq_len_multiplier_for_explicit_grad_accum(self,
                                                           skip_validation, skip_parse_args,
                                                           mock_vars, mock_path_resolver):
        user_settings = {"gradient_accumulation_steps": 2}
        mock_vars.return_value = user_settings
        TrainingConfiguration.populate_from_scope(task_type=Tasks.TEXT_NER,
                                                  dataset_language="eng",
                                                  automl_settings={})
        self.assertFalse(user_settings[TrainingInputLiterals.USE_SEQ_LEN_MULTIPLIER])

    def test_seq_len_multiplier_override_not_present_by_default(self,
                                                                skip_validation, skip_parse_args,
                                                                mock_vars, mock_path_resolver):
        user_settings = {"some key": "some value"}
        mock_vars.return_value = user_settings
        TrainingConfiguration.populate_from_scope(task_type=Tasks.TEXT_CLASSIFICATION,
                                                  dataset_language="mul",
                                                  automl_settings={})
        # No override present, so the default value of True will be used.
        self.assertFalse(TrainingInputLiterals.USE_SEQ_LEN_MULTIPLIER in user_settings)

    def test_training_configuration_getter(self,
                                           skip_validation, skip_parse_args,
                                           mock_vars, mock_path_resolver):
        settings = {TrainingInputLiterals.MODEL_NAME: "some model"}
        training_configuration = TrainingConfiguration(settings, _internal=True)
        settings[TrainingInputLiterals.MODEL_NAME] = "some other model"
        # Getter just passes through to underlying dict.
        self.assertEqual("some other model", training_configuration[TrainingInputLiterals.MODEL_NAME])

    def test_training_configuration_setter(self,
                                           skip_validation, skip_parse_args,
                                           mock_vars, mock_path_resolver):
        settings = {}
        training_configuration = TrainingConfiguration(settings, _internal=True)
        training_configuration[TrainingInputLiterals.LONG_RANGE_LENGTH] = 512
        # Setter modifies backing dict.
        self.assertEqual(512, settings[TrainingInputLiterals.LONG_RANGE_LENGTH])

    def test_training_configuration_round_trip(self,
                                               skip_validation, skip_parse_args,
                                               mock_vars, mock_path_resolver):
        settings = {TrainingInputLiterals.MODEL_NAME_OR_PATH: "some path",
                    TrainingInputLiterals.TOKENIZER_NAME_OR_PATH: "some tokenizer path"}
        training_configuration = pickle.loads(pickle.dumps(TrainingConfiguration(settings, _internal=True)))
        self.assertEqual(settings, training_configuration._settings_dict)
        self.assertFalse(TrainingInputLiterals.MODEL_NAME_OR_PATH in training_configuration)
        self.assertFalse(TrainingInputLiterals.TOKENIZER_NAME_OR_PATH in training_configuration)

    def test_training_configuration_disables_seq_len_mul_for_distilled_models(self,
                                                                              skip_validation, skip_parse_args,
                                                                              mock_vars, mock_path_resolver):
        mock_vars.return_value = {}
        for distilled_model in [ModelNames.DISTILBERT_BASE_CASED, ModelNames.DISTILROBERTA_BASE]:
            mock_path_resolver.return_value.model_name = distilled_model
            training_configuration = TrainingConfiguration.populate_from_scope(task_type=Tasks.TEXT_CLASSIFICATION,
                                                                               dataset_language="eng",
                                                                               automl_settings={})
            self.assertFalse(training_configuration[TrainingInputLiterals.USE_SEQ_LEN_MULTIPLIER])


@patch('azureml.automl.dnn.nlp.common.training_configuration.ResourcePathResolver',
       return_value=Mock(model_name="some model", model_path="some path",
                         tokenizer_path="some tokenizer path"))
@patch('azureml.automl.dnn.nlp.common.training_configuration.NLPSettingsValidator.validate')
class TestTrainingConfigurationParsing(unittest.TestCase):
    def test_parser_recognizes_ignored_arguments(self, skip_validation, mock_path_resolver):
        with patch('sys.argv', ["script", "--" + TrainingInputLiterals.DATA_FOLDER, "some value",
                                "--" + TrainingInputLiterals.LABELS_FILE_ROOT, "some other value",
                                "--" + TrainingInputLiterals.IGNORED_ARGUMENT, "0"]):
            training_config = TrainingConfiguration.populate_from_scope(task_type=Tasks.TEXT_CLASSIFICATION,
                                                                        dataset_language="eng",
                                                                        automl_settings={})
        self.assertEqual(0, skip_validation.call_args[1]["unknown_cnt"])  # all arguments were recognized
        for ignored_arg in TrainingInputLiterals.IGNORED_ARGUMENTS:
            self.assertNotIn(ignored_arg, training_config)

    def test_parser_recognized_ignored_arguments_with_no_values(self, skip_validation, mock_path_resolver):
        # These arguments aren't set by NLP, so we should be as flexible as possible with respect to their values.
        # That is, regardless of if they're changed or removed, we know what to do.
        with patch('sys.argv', ["script", "--" + TrainingInputLiterals.DATA_FOLDER,
                                "--" + TrainingInputLiterals.LABELS_FILE_ROOT,
                                "--" + TrainingInputLiterals.IGNORED_ARGUMENT]):
            training_config = TrainingConfiguration.populate_from_scope(task_type=Tasks.TEXT_CLASSIFICATION,
                                                                        dataset_language="eng",
                                                                        automl_settings={})
        self.assertEqual(0, skip_validation.call_args[1]["unknown_cnt"])  # all arguments were recognized
        for ignored_arg in TrainingInputLiterals.IGNORED_ARGUMENTS:
            self.assertNotIn(ignored_arg, training_config)
