# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Collection of validation functions for settings read in from the command-line which have not yet been checked."""
from typing import Any, Callable, Dict
from transformers.trainer_utils import SchedulerType

import logging
import numpy as np
import json

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.exceptions import ValidationException
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import InvalidSweepArgument
from azureml.automl.dnn.nlp.common.constants import ModelNames, TrainingInputLiterals, ValidationLiterals

_logger = logging.getLogger(__name__)


class NLPSettingsValidator:
    """Object housing validation functions for command-line settings. Task-agnostic, for now."""

    def validate(self, settings: Dict[str, Any], unknown_cnt: int) -> None:
        """
        Main validation function. May mutate the input.

        :param settings: the settings to validate.
        :param unknown_cnt: the number of unknown arguments encountered during the top-level parsing.
        :return: None.
        """
        # The setting value will only be of NoneType if it was not specified by the user and instead auto-filled in by
        # argparse. Remove these values to ensure they won't override any defaults later in the settings configuration.
        null_settings = [k for k in settings if settings[k] is None]
        for null_setting in null_settings:
            del settings[null_setting]

        params_to_validate = settings.keys() - {TrainingInputLiterals.MODEL}
        for prop in params_to_validate:
            self.PROPERTY_TO_VALIDATION_MAPPING[prop](self, settings)

        if TrainingInputLiterals.MODEL in settings:
            unknown_cnt += self._validate_model_subspace(settings)

        if unknown_cnt > 0:
            # Actual parameters and values may contain PII, so do not log them.
            _logger.warning(
                f"Encountered {unknown_cnt} unknown parameter{'s' if unknown_cnt > 1 else ''} in specified user "
                "training settings. Currently, only the following parameters are "
                f"supported: {TrainingInputLiterals.SUPPORTED_PUBLIC_SETTINGS}.")

    def _validate_model_subspace(self, settings: Dict[str, Any]) -> int:
        """
        Validate properties in model subspace. This entails parsing the model subspace, removing unknown nested
        settings, validating the remaining settings, and merging the subspace arguments with the top-level settings
        dictionary.

        :param settings: the broader settings dictionary we're validating.
        :return: the number of unknown settings encountered while parsing the model subspace, if any. These would
        not have been discovered during the top-level parsing by the ArgumentParser object.
        """
        try:
            nested_model_settings = json.loads(settings.pop(TrainingInputLiterals.MODEL))
        except json.JSONDecodeError:
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidSweepArgument,
                    log_safe_description="Encountered JSON decoding error when reading model subspace arguments. "
                                         "Are the specified sweeping arguments properly formatted?",
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )

        if TrainingInputLiterals.MODEL in nested_model_settings:
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidSweepArgument,
                    log_safe_description="Unexpected property 'model' found in model subspace, suggesting another "
                                         "nested model subspace exists. Did you mean 'model_name'?",
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )

        unknown_params = [param for param in nested_model_settings
                          if param not in TrainingInputLiterals.SUPPORTED_PUBLIC_SETTINGS]
        unknown_cnt = len(unknown_params)
        for unknown_param in unknown_params:
            del nested_model_settings[unknown_param]

        # For the recursive validation, all parameters are known since we've explicitly filtered them.
        self.validate(settings=nested_model_settings, unknown_cnt=0)

        for param, val in nested_model_settings.items():
            top_level_value = settings.get(param, None)
            if top_level_value is not None and top_level_value != val:
                # Parameter known, so its name is log-safe.
                _logger.warning(f"Conflicting values detected for parameter {param}. "
                                f"Overwriting top-level value with that provided in model subspace.")
            settings[param] = val

        return unknown_cnt

    def _non_empty_model_string(self, settings: Dict[str, Any]) -> None:
        """
        Validate the model_name property.

        :param settings: the broader settings dictionary we're validating.
        :return: None.
        """
        model_name = settings[TrainingInputLiterals.MODEL_NAME]
        if not model_name or model_name not in ModelNames.SUPPORTED_MODELS:
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidSweepArgument,
                    log_safe_description="Specified model must be non-empty and present in supported models list: "
                                         f"{ModelNames.SUPPORTED_MODELS}",
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )

    def _positive_integer_valued(self, val: str, param: str) -> int:
        """
        Helper function to check if a string is a positive integer-type.

        :param val: the string value to validate.
        :param param: the name of the parameter we're validating, for logging purposes.
        :return: the final integer, if a validation error was not raised.
        """
        try:
            int_val = int(val)
        except ValueError:
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidSweepArgument,
                    log_safe_description=f"Expected integer value for {param} parameter, but string to "
                                         "int conversion failed.",
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )

        if int_val <= 0:
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidSweepArgument,
                    log_safe_description=f"Expected positive integer value for {param} parameter, but detected "
                                         "value was less than or equal to zero.",
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )

        return int_val

    def _non_negative_float_valued(self, val: str, param: str) -> float:
        """
        Helper function to check if a string is a finite non-negative float-type.

        :param val: the string value to validate.
        :param param: the name of the parameter we're validating, for logging purposes.
        :return: the final float, if a validation error was not raised.
        """
        try:
            float_val = float(val)
        except ValueError:
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidSweepArgument,
                    log_safe_description=f"Expected float value for {param} parameter, but string to "
                                         "float conversion failed.",
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )

        if not np.isfinite(float_val) or float_val < 0:
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidSweepArgument,
                    log_safe_description=f"Expected non-negative float value for {param} parameter, but detected "
                                         "value was less than zero.",
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )

        return float_val

    def _validate_train_batch_size(self, settings: Dict[str, Any]) -> None:
        """
        Validate the train batch size argument. Cast it to an integer since it was read in as a string.

        :param settings: the broader settings dictionary we're validating.
        :return: None.
        """
        val = self._positive_integer_valued(settings[TrainingInputLiterals.TRAIN_BATCH_SIZE],
                                            TrainingInputLiterals.TRAIN_BATCH_SIZE)
        if val > 32:
            _logger.info(f"High train batch size of {val} requested. Be advised that training may run into GPU memory "
                         "issues if a lower end VM and/or larger models are being used.")

        settings[TrainingInputLiterals.TRAIN_BATCH_SIZE] = val

    def _validate_valid_batch_size(self, settings: Dict[str, Any]) -> None:
        """
        Validate the valid batch size argument. Cast it to an integer since it was read in as a string.

        :param settings: the broader settings dictionary we're validating.
        :return: None.
        """
        settings[TrainingInputLiterals.VALID_BATCH_SIZE] = \
            self._positive_integer_valued(settings[TrainingInputLiterals.VALID_BATCH_SIZE],
                                          TrainingInputLiterals.VALID_BATCH_SIZE)

    def _validate_gradient_accumulation_steps(self, settings: Dict[str, Any]) -> None:
        """
        Validate the gradient accumulation steps argument. Cast it to an integer since it was read in as a string.

        :param settings: the broader settings dictionary we're validating.
        :return: None.
        """
        settings[TrainingInputLiterals.GRADIENT_ACCUMULATION_STEPS] = \
            self._positive_integer_valued(settings[TrainingInputLiterals.GRADIENT_ACCUMULATION_STEPS],
                                          TrainingInputLiterals.GRADIENT_ACCUMULATION_STEPS)

    def _validate_num_train_epochs(self, settings: Dict[str, Any]) -> None:
        """
        Validate the number of training epochs requested. Cast it to an integer since it was read in as a string.

        :param settings: the broader settings dictionary we're validating.
        :return: None.
        """
        val = self._positive_integer_valued(settings[TrainingInputLiterals.NUM_TRAIN_EPOCHS],
                                            TrainingInputLiterals.NUM_TRAIN_EPOCHS)

        if val > 5:
            _logger.info(f"High epoch count of {val} epochs requested for training. If large text DNNs are requested, "
                         "the data is large, and distributed training is not enabled, we recommend ensuring the "
                         "experiment timeout is sufficiently large to allow for training to complete.")

        settings[TrainingInputLiterals.NUM_TRAIN_EPOCHS] = val

    def _validate_learning_rate(self, settings: Dict[str, Any]) -> None:
        """
        Validate the learning rate. Cast it to a float since it was read in as a string.

        :param settings: the broader settings dictionary we're validating.
        :return: None.
        """
        val = self._non_negative_float_valued(settings[TrainingInputLiterals.LEARNING_RATE],
                                              TrainingInputLiterals.LEARNING_RATE)
        if val == 0 or val >= 1:
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidSweepArgument,
                    log_safe_description="Learning rate must be greater than zero and less than one. "
                                         f"Provided value of {val} lies outside this range.",
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )
        settings[TrainingInputLiterals.LEARNING_RATE] = val

    def _validate_weight_decay(self, settings: Dict[str, Any]) -> None:
        """
        Validate the weight decay. Cast it to a float since it was read in as a string.

        :param settings: the broader settings dictionary we're validating.
        :return: None.
        """
        val = self._non_negative_float_valued(settings[TrainingInputLiterals.WEIGHT_DECAY],
                                              TrainingInputLiterals.WEIGHT_DECAY)

        if val > 1:
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidSweepArgument,
                    log_safe_description=f"Invalid weight decay of {val} exceeds the maximum value 1.",
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )
        settings[TrainingInputLiterals.WEIGHT_DECAY] = val

    def _validate_warmup_ratio(self, settings: Dict[str, Any]) -> None:
        """
        Validate the warmup ratio. Cast it to a float since it was read in as a string.

        :param settings: the broader settings dictionary we're validating.
        :return: None.
        """
        val = self._non_negative_float_valued(settings[TrainingInputLiterals.WARMUP_RATIO],
                                              TrainingInputLiterals.WARMUP_RATIO)

        if val > 1:
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidSweepArgument,
                    log_safe_description=f"Invalid warmup ratio of {val} exceeds the maximum value 1.",
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )
        settings[TrainingInputLiterals.WARMUP_RATIO] = val

    def _validate_lr_scheduler_type(self, settings: Dict[str, Any]) -> None:
        """
        Validate the lr scheduler type. Convert it to a SchedulerType enum member from its string representation.

        :param settings: the broader settings dictionary we're validating.
        :return: None.
        """
        val = settings[TrainingInputLiterals.LR_SCHEDULER_TYPE]
        try:
            settings[TrainingInputLiterals.LR_SCHEDULER_TYPE] = SchedulerType(val)
        except ValueError:
            raise ValidationException._with_error(
                AzureMLError.create(
                    InvalidSweepArgument,
                    log_safe_description=f"Provided {TrainingInputLiterals.LR_SCHEDULER_TYPE} argument was not among "
                                         f"supported values: {[obj.value for obj in list(SchedulerType)]}.",
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )

        settings[TrainingInputLiterals.LR_SCHEDULER_TYPE] = val

    PROPERTY_TO_VALIDATION_MAPPING = {
        TrainingInputLiterals.MODEL_NAME: _non_empty_model_string,
        TrainingInputLiterals.TRAIN_BATCH_SIZE: _validate_train_batch_size,
        TrainingInputLiterals.VALID_BATCH_SIZE: _validate_valid_batch_size,
        TrainingInputLiterals.GRADIENT_ACCUMULATION_STEPS: _validate_gradient_accumulation_steps,
        TrainingInputLiterals.NUM_TRAIN_EPOCHS: _validate_num_train_epochs,
        TrainingInputLiterals.LEARNING_RATE: _validate_learning_rate,
        TrainingInputLiterals.WEIGHT_DECAY: _validate_weight_decay,
        TrainingInputLiterals.WARMUP_RATIO: _validate_warmup_ratio,
        TrainingInputLiterals.LR_SCHEDULER_TYPE: _validate_lr_scheduler_type
    }  # type: Dict[str, Callable[["NLPSettingsValidator", Dict[str, Any]], None]]
