from unittest.mock import patch, Mock

import json
import unittest

from azureml.automl.core.shared.exceptions import ValidationException
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import InvalidSweepArgument
from azureml.automl.dnn.nlp.common.constants import ModelNames, TrainingInputLiterals
from azureml.automl.dnn.nlp.validation.settings_validator import NLPSettingsValidator


class TestNLPSettingsValidator(unittest.TestCase):
    def test_validate_valid_lr_scheduler_type(self):
        validator = NLPSettingsValidator()
        scheduler_types = ["linear", "cosine", "cosine_with_restarts", "polynomial",
                           "constant", "constant_with_warmup"]
        for scheduler_type in scheduler_types:
            settings = {TrainingInputLiterals.LR_SCHEDULER_TYPE: str(scheduler_type)}
            validator._validate_lr_scheduler_type(settings)
        # No validation exceptions are raised for any of the expected schedulers.

    def test_validate_invalid_lr_scheduler_type(self):
        validator = NLPSettingsValidator()
        settings = {TrainingInputLiterals.LR_SCHEDULER_TYPE: "arbitrary value"}
        with self.assertRaises(ValidationException) as ve:
            validator._validate_lr_scheduler_type(settings)
        self.assertEqual(InvalidSweepArgument.__name__, ve.exception.error_code)

    def test_prop_delegation(self):
        validator = NLPSettingsValidator()
        for property in validator.PROPERTY_TO_VALIDATION_MAPPING.keys():
            mock_delegate = Mock()
            with patch.dict(validator.PROPERTY_TO_VALIDATION_MAPPING, {property: mock_delegate}):
                settings = {property: "some value"}
                validator.validate(settings, 0)
            self.assertEqual(1, mock_delegate.call_count)

    def test_non_negative_float_valued_raises_on_type_mismatch(self):
        validator = NLPSettingsValidator()
        for bad_val in ["hello", "None", "True", "0b101"]:
            with self.assertRaises(ValidationException) as ve:
                validator._non_negative_float_valued(bad_val, "")
            self.assertEqual(InvalidSweepArgument.__name__, ve.exception.error_code)

    def test_non_negative_float_valued_raises_on_non_finite(self):
        validator = NLPSettingsValidator()
        for bad_val in ["nan", "inf"]:
            with self.assertRaises(ValidationException) as ve:
                validator._non_negative_float_valued(bad_val, "")
            self.assertEqual(InvalidSweepArgument.__name__, ve.exception.error_code)

    def test_non_negative_float_valued_raises_on_negative(self):
        validator = NLPSettingsValidator()
        for bad_val in ["-0.5", "-1e-5", "1.07j"]:
            with self.assertRaises(ValidationException) as ve:
                validator._non_negative_float_valued(bad_val, "")
            self.assertEqual(InvalidSweepArgument.__name__, ve.exception.error_code)

    def test_non_negative_float_valued_returns_valid(self):
        validator = NLPSettingsValidator()
        self.assertEqual(0.1, validator._non_negative_float_valued("0.1", ""))
        self.assertEqual(1e-5, validator._non_negative_float_valued("1e-5", ""))

    @patch('azureml.automl.dnn.nlp.validation.settings_validator.NLPSettingsValidator._non_negative_float_valued')
    def test_validate_warmup_ratio_calls_non_negative(self, mock_non_negative):
        validator = NLPSettingsValidator()
        mock_non_negative.return_value = 0.5
        settings = {TrainingInputLiterals.WARMUP_RATIO: "0.5"}
        validator._validate_warmup_ratio(settings)
        mock_non_negative.assert_called_once()
        self.assertEqual(settings[TrainingInputLiterals.WARMUP_RATIO], mock_non_negative.return_value)

    @patch('azureml.automl.dnn.nlp.validation.settings_validator.NLPSettingsValidator._non_negative_float_valued')
    def test_validate_weight_decay_calls_non_negative(self, mock_non_negative):
        validator = NLPSettingsValidator()
        mock_non_negative.return_value = 0.5
        settings = {TrainingInputLiterals.WEIGHT_DECAY: "0.5"}
        validator._validate_weight_decay(settings)
        mock_non_negative.assert_called_once()
        self.assertEqual(settings[TrainingInputLiterals.WEIGHT_DECAY], mock_non_negative.return_value)

    @patch('azureml.automl.dnn.nlp.validation.settings_validator.NLPSettingsValidator._non_negative_float_valued')
    def test_validate_learning_rate_calls_non_negative(self, mock_non_negative):
        validator = NLPSettingsValidator()
        mock_non_negative.return_value = 0.5
        settings = {TrainingInputLiterals.LEARNING_RATE: "5e-5"}
        validator._validate_learning_rate(settings)
        mock_non_negative.assert_called_once()
        self.assertEqual(settings[TrainingInputLiterals.LEARNING_RATE], mock_non_negative.return_value)

    def test_validate_learning_rate_nonconvergent_case_raises(self):
        validator = NLPSettingsValidator()
        for bad_val in ['0', '1', '10']:
            with self.assertRaises(ValidationException) as ve:
                validator._validate_learning_rate({TrainingInputLiterals.LEARNING_RATE: bad_val})
            self.assertEqual(InvalidSweepArgument.__name__, ve.exception.error_code)

    def test_validate_weight_decay_too_large(self):
        validator = NLPSettingsValidator()
        with self.assertRaises(ValidationException) as ve:
            validator._validate_weight_decay({TrainingInputLiterals.WEIGHT_DECAY: '1.1'})
        self.assertEqual(InvalidSweepArgument.__name__, ve.exception.error_code)

    def test_validate_warmup_ratio_too_large(self):
        validator = NLPSettingsValidator()
        with self.assertRaises(ValidationException) as ve:
            validator._validate_warmup_ratio({TrainingInputLiterals.WARMUP_RATIO: '1.1'})
        self.assertEqual(InvalidSweepArgument.__name__, ve.exception.error_code)

    def test_positive_integer_valued_raises_on_type_mismatch(self):
        validator = NLPSettingsValidator()
        for bad_val in ["non-numeric", "None", "True", "0.5", "nan", "inf"]:
            with self.assertRaises(ValidationException) as ve:
                validator._positive_integer_valued(bad_val, "")
            self.assertEqual(InvalidSweepArgument.__name__, ve.exception.error_code)

    def test_positive_integer_valued_raises_on_non_decimal_base(self):
        validator = NLPSettingsValidator()
        for bad_val in ["0b10", "0x1a"]:
            with self.assertRaises(ValidationException) as ve:
                validator._positive_integer_valued(bad_val, "")
            self.assertEqual(InvalidSweepArgument.__name__, ve.exception.error_code)

    def test_positive_integer_valued_raises_on_non_positive(self):
        validator = NLPSettingsValidator()
        for bad_val in ["0", "-1"]:
            with self.assertRaises(ValidationException) as ve:
                validator._positive_integer_valued(bad_val, "")
            self.assertEqual(InvalidSweepArgument.__name__, ve.exception.error_code)

    def test_positive_integer_valued_returns_valid(self):
        validator = NLPSettingsValidator()
        for value in ["1_000", "712"]:
            self.assertEqual(int(value), validator._positive_integer_valued(value, ""))

    @patch('azureml.automl.dnn.nlp.validation.settings_validator.NLPSettingsValidator._positive_integer_valued')
    def test_validate_num_train_epochs_calls_positive_int(self, mock_positive_int):
        validator = NLPSettingsValidator()
        mock_positive_int.return_value = 712
        settings = {TrainingInputLiterals.NUM_TRAIN_EPOCHS: "712"}
        validator._validate_num_train_epochs(settings)
        mock_positive_int.assert_called_once()
        self.assertEqual(settings[TrainingInputLiterals.NUM_TRAIN_EPOCHS], mock_positive_int.return_value)

    @patch('azureml.automl.dnn.nlp.validation.settings_validator.NLPSettingsValidator._positive_integer_valued')
    def test_validate_gradient_accumulation_steps(self, mock_positive_int):
        validator = NLPSettingsValidator()
        settings = {TrainingInputLiterals.GRADIENT_ACCUMULATION_STEPS: "2"}
        validator._validate_gradient_accumulation_steps(settings)
        mock_positive_int.assert_called_once()
        self.assertEqual(settings[TrainingInputLiterals.GRADIENT_ACCUMULATION_STEPS], mock_positive_int.return_value)

    @patch('azureml.automl.dnn.nlp.validation.settings_validator.NLPSettingsValidator._positive_integer_valued')
    def test_validate_valid_batch_size(self, mock_positive_int):
        validator = NLPSettingsValidator()
        settings = {TrainingInputLiterals.VALID_BATCH_SIZE: "64"}
        validator._validate_valid_batch_size(settings)
        mock_positive_int.assert_called_once()
        self.assertEqual(settings[TrainingInputLiterals.VALID_BATCH_SIZE], mock_positive_int.return_value)

    @patch('azureml.automl.dnn.nlp.validation.settings_validator.NLPSettingsValidator._positive_integer_valued')
    def test_validate_train_batch_size(self, mock_positive_int):
        validator = NLPSettingsValidator()
        mock_positive_int.return_value = 3
        settings = {TrainingInputLiterals.TRAIN_BATCH_SIZE: "32"}
        validator._validate_train_batch_size(settings)
        mock_positive_int.assert_called_once()
        self.assertEqual(settings[TrainingInputLiterals.TRAIN_BATCH_SIZE], mock_positive_int.return_value)

    def test_non_empty_model_string_raises_on_empty(self):
        validator = NLPSettingsValidator()
        for bad_val in ["", None, "arbitrary model"]:
            with self.assertRaises(ValidationException) as ve:
                validator._non_empty_model_string({TrainingInputLiterals.MODEL_NAME: bad_val})
            self.assertEqual(InvalidSweepArgument.__name__, ve.exception.error_code)

    def test_non_empty_model_string_passes_on_supported_models(self):
        validator = NLPSettingsValidator()
        for model_name in ModelNames.SUPPORTED_MODELS:
            validator._non_empty_model_string({TrainingInputLiterals.MODEL_NAME: model_name})

    def test_validate_model_subspace_raises_on_malformed_json_input(self):
        validator = NLPSettingsValidator()
        settings = {TrainingInputLiterals.MODEL: "<Some malformed input>"}
        with self.assertRaises(ValidationException) as ve:
            validator._validate_model_subspace(settings)
        self.assertEqual(InvalidSweepArgument.__name__, ve.exception.error_code)

    def test_validate_model_subspace_raises_on_recursive_subspace(self):
        validator = NLPSettingsValidator()
        settings = {TrainingInputLiterals.MODEL: "{\"model\": {\"model_name\": \"bert-base-cased\"}}"}
        with self.assertRaises(ValidationException) as ve:
            validator._validate_model_subspace(settings)
        self.assertEqual(InvalidSweepArgument.__name__, ve.exception.error_code)

    def test_validate_model_subspace_counts_and_removes_unknown_nested_props(self):
        validator = NLPSettingsValidator()
        settings = {TrainingInputLiterals.MODEL: "{\"model_name\": \"bert-base-cased\", \"unknown\": \"value\"}"}
        # Simple JSON decode produces dict with unknown property
        self.assertIn("unknown", json.loads(settings[TrainingInputLiterals.MODEL]))
        # But after validation, it is counted and removed
        unknown_cnt = validator._validate_model_subspace(settings)
        self.assertEqual(1, unknown_cnt)
        self.assertNotIn("unknown", settings)
        # But the valid nested parameter is bubbled up to the top level.
        self.assertIn(TrainingInputLiterals.MODEL_NAME, settings)
        self.assertNotIn(TrainingInputLiterals.MODEL, settings)

    def test_validate_model_subspace_prioritizes_subspace_values_in_param_conflict(self):
        validator = NLPSettingsValidator()
        settings = \
            {TrainingInputLiterals.MODEL: "{\"number_of_epochs\": \"32\", \"model_name\": \"xlnet-large-cased\"}",
             TrainingInputLiterals.NUM_TRAIN_EPOCHS: 64}
        unknown_cnt = validator._validate_model_subspace(settings)
        self.assertEqual(0, unknown_cnt)
        self.assertEqual(32, settings[TrainingInputLiterals.NUM_TRAIN_EPOCHS])
        self.assertNotIn(TrainingInputLiterals.MODEL, settings)

    def test_validate_model_subspace_recursively_validates(self):
        validator = NLPSettingsValidator()
        settings = {TrainingInputLiterals.MODEL:
                    "{\"gradient_accumulation_steps\": \"2\", \"model_name\": \"distilbert-base-cased\"}"}
        with patch.object(validator, "validate") as mock_validate:
            validator._validate_model_subspace(settings)
        self.assertEqual(1, mock_validate.call_count)

        settings = {TrainingInputLiterals.MODEL:
                    "{\"validation_batch_size\": \"nan\", \"model_name\": \"xlm-roberta-large\"}"}
        with self.assertRaises(ValidationException) as ve:
            # One of the nested settings is invalid, namely the valid_batch_size.
            validator._validate_model_subspace(settings)
        self.assertEqual(InvalidSweepArgument.__name__, ve.exception.error_code)

    @patch('azureml.automl.dnn.nlp.validation.settings_validator.NLPSettingsValidator._validate_model_subspace')
    def test_overall_validate_delegates_subspace_validation(self, mock_validate_subspace):
        validator = NLPSettingsValidator()
        mock_validate_subspace.return_value = 0
        settings = {TrainingInputLiterals.MODEL: "{\"model_name\": \"roberta-large\"}"}
        validator.validate(settings, 0)
        mock_validate_subspace.assert_called_once_with(settings)

    def test_overall_validate_deletes_null_valued_parameters(self):
        validator = NLPSettingsValidator()
        settings = {TrainingInputLiterals.MODEL: None,
                    TrainingInputLiterals.TRAIN_BATCH_SIZE: None,
                    TrainingInputLiterals.NUM_TRAIN_EPOCHS: "32"}
        validator.validate(settings, 0)
        self.assertEqual(1, len(settings))
        self.assertIn(TrainingInputLiterals.NUM_TRAIN_EPOCHS, settings)
        self.assertEqual(32, settings[TrainingInputLiterals.NUM_TRAIN_EPOCHS])
