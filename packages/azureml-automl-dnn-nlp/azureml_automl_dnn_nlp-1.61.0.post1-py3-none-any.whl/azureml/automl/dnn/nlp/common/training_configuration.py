# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Object and related constants for storing and manipulating training settings/hyperparameters; task-agnostic."""
from typing import Any, Dict, NoReturn, Optional

import argparse
import logging

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.constants import Tasks
from azureml.automl.core.shared.exceptions import UserException
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import ArgumentParsingError
from azureml.automl.dnn.nlp.common._resource_path_resolver import ResourcePathResolver
from azureml.automl.dnn.nlp.common.constants import ModelNames, ValidationLiterals
from azureml.automl.dnn.nlp.validation.settings_validator import NLPSettingsValidator
from ._utils import make_arg
from .constants import TrainingInputLiterals, LoggingLiterals
from .model_parameters import DefaultParameterFactory

_logger = logging.getLogger(__name__)


class _NLPSettingParser(argparse.ArgumentParser):
    """
    Subclass argparse library's ArgumentParser object, overriding error-handling logic to integrate with
    our exception system. In our current versions of Python, e.g. 3.7 and 3.8, the default parser will throw a
    SystemExit exception regardless of the error source, which should bubble up as a SystemError in our monitoring
    systems. We override this greedy-exit behavior with one that will throw UserErrors as necessary.
    """
    def error(self, message: str) -> NoReturn:
        """
        Function that defines ArgumentParser object's exception-handling behavior.

        :param message: the error message.
        :return: NoReturn -- this method never terminates normally.
        """
        raise UserException._with_error(
            AzureMLError.create(
                ArgumentParsingError,
                details=message,
                target=ValidationLiterals.DATA_EXCEPTION_TARGET
            )
        )


class TrainingConfiguration:
    """
    Object meant to house all configurations that directly control the training procedure. All hyperparameter values,
    for instance, should be stored in this object. A TrainingConfiguration differs from the AutoML settings in that
    the latter is a broader object that can house run- and job-level properties (e.g. save_mlflow, log_level).
    """
    def __init__(self, settings: Dict[str, Any], _internal=False):
        """
        Initializer for TrainingConfiguration object. This is not meant to be used directly except in testing
        scenarios. One of the static constructor methods from this class should be used, such as populate_from_scope.

        :param settings: the dictionary of user settings that this TrainingConfiguration object is meant to store.
        :param _internal: whether instantiation is invoked through a supported internal code path or not.
        :return: None.
        """
        assert _internal, "Please call one of the static methods to instantiate a TrainingConfiguration object " \
                          "rather than using the constructor directly."
        self._settings_dict = settings

    @staticmethod
    def populate_from_scope(task_type: str,
                            dataset_language: str,
                            automl_settings: Dict[str, Any]) -> "TrainingConfiguration":
        """
        Instantiate an instance of the training configuration, using values passed in from the command line
        as necessary.

        :param task_type: The string representing the training task type.
        :param dataset_language: The dataset language to use for training. Defaults to 'eng' upstream.
        :param automl_settings: All automl-related settings, not just constrained to training.
        :return: An instance of the TrainingConfiguration class.
        """
        parser = _NLPSettingParser()

        # Model selection parameters
        exclusive_param_group = parser.add_mutually_exclusive_group()
        exclusive_param_group.add_argument(make_arg(TrainingInputLiterals.MODEL_NAME))
        exclusive_param_group.add_argument(make_arg(TrainingInputLiterals.MODEL))

        parser.add_argument(make_arg(TrainingInputLiterals.TRAIN_BATCH_SIZE))
        parser.add_argument(make_arg(TrainingInputLiterals.VALID_BATCH_SIZE))
        parser.add_argument(make_arg(TrainingInputLiterals.GRADIENT_ACCUMULATION_STEPS))
        parser.add_argument(make_arg(TrainingInputLiterals.NUM_TRAIN_EPOCHS))
        parser.add_argument(make_arg(TrainingInputLiterals.LEARNING_RATE))
        parser.add_argument(make_arg(TrainingInputLiterals.WEIGHT_DECAY))
        parser.add_argument(make_arg(TrainingInputLiterals.WARMUP_RATIO))
        parser.add_argument(make_arg(TrainingInputLiterals.LR_SCHEDULER_TYPE))

        # Add arguments that will be passed to this script as part of system requirements, but should otherwise be
        # ignored. These are added so they don't add to the unknown count, but they will be discarded.
        parser.add_argument(make_arg(TrainingInputLiterals.DATA_FOLDER), nargs="?")
        parser.add_argument(make_arg(TrainingInputLiterals.LABELS_FILE_ROOT), nargs="?")
        parser.add_argument(make_arg(TrainingInputLiterals.IGNORED_ARGUMENT), nargs="?")

        # Parse and process arguments
        user_settings, unknown = parser.parse_known_args()
        user_settings = vars(user_settings)
        unknown_cnt = len(unknown)

        for ignored_param in TrainingInputLiterals.IGNORED_ARGUMENTS:
            user_settings.pop(ignored_param, None)

        validator = NLPSettingsValidator()
        validator.validate(settings=user_settings, unknown_cnt=unknown_cnt)

        # Account for fixed training parameters specified by the user. The services write them to the automl_settings
        # dict for the SDK to use. If a fixed param conflicts with a swept param, the fixed value takes priority.
        fixed_settings = {}
        fixable_parameter_keys = TrainingInputLiterals.SUPPORTED_PUBLIC_SETTINGS - {TrainingInputLiterals.MODEL}
        for param in fixable_parameter_keys:
            if automl_settings.get(param, None) is not None:
                # String-cast since we do type conversion and validation in the validator.
                fixed_settings[param] = str(automl_settings[param])
        if fixed_settings:
            _logger.info(f"Detected {len(fixed_settings)} fixed training parameters. Validating input values.")
            validator.validate(settings=fixed_settings, unknown_cnt=0)
            user_settings.update(fixed_settings)

        if user_settings:
            log_str = "The following settings were specified by the user for training:\n" + \
                      '\n'.join([f"{k}: {v}" for k, v in user_settings.items()])
            _logger.info(log_str)

        model_name = user_settings.get(TrainingInputLiterals.MODEL_NAME, None)  # type: Optional[str]
        resource_path_resolver = \
            ResourcePathResolver(model_name=model_name,
                                 dataset_language=dataset_language,
                                 is_multilabel_training=task_type == Tasks.TEXT_CLASSIFICATION_MULTILABEL)
        model_name = resource_path_resolver.model_name  # type: str
        user_settings[TrainingInputLiterals.MODEL_NAME] = model_name
        # to be used for logging in mlflow metadata
        user_settings[LoggingLiterals.TASK_TYPE] = task_type
        user_settings[TrainingInputLiterals.MODEL_NAME_OR_PATH] = resource_path_resolver.model_path or model_name
        user_settings[TrainingInputLiterals.TOKENIZER_NAME_OR_PATH] = \
            resource_path_resolver.tokenizer_path or model_name
        if (TrainingInputLiterals.TRAIN_BATCH_SIZE in user_settings
                or TrainingInputLiterals.GRADIENT_ACCUMULATION_STEPS in user_settings
                or model_name in [ModelNames.DISTILBERT_BASE_CASED, ModelNames.DISTILROBERTA_BASE]):
            # The user has explicitly specified the batch size or the gradient accumulation, so we won't
            # override them during dynamic sequence length calculation. Alternatively, we're using a distilled model,
            # so there's less of a memory burden and no need for the adjustment.
            user_settings[TrainingInputLiterals.USE_SEQ_LEN_MULTIPLIER] = False
        settings = DefaultParameterFactory.get(task_type=task_type, model_name=model_name)
        settings.update(user_settings)
        if settings:
            log_str = "The default and user-specified model and hyperparameter settings are as follows:\n" + \
                      '\n'.join([f"{k}: {settings[k]}" for k in fixable_parameter_keys])
            _logger.info(log_str)

        return TrainingConfiguration(settings=settings, _internal=True)

    def __getitem__(self, item) -> Any:
        """
        Override on the object's __getitem__ method to access from the underlying settings dictionary.

        :param item: the key to retrieve the value for.
        :return: whatever value was stored under the specified key.
        """
        return self._settings_dict.__getitem__(item)

    def __setitem__(self, key, value):
        """
        Override on the object's __setitem__ method to save to the underlying settings dictionary.

        :param key: the key to save the value under.
        :param value: the value to save.
        :return: None.
        """
        self._settings_dict[key] = value

    def __contains__(self, item):
        """
        Implement contains method so membership checks behave as expected for this custom object.

        :param item: the item we're checking membership for in this configuration instance.
        :return: None.
        """
        return item in self._settings_dict

    def __getstate__(self):
        """
        Override on the object's __getstate__ method, to be used during serialization.

        :return: None.
        """
        state = self._settings_dict
        # Remove paths which may be stale downstream, after deserialization (e.g. in a scenario like inference).
        if TrainingInputLiterals.MODEL_NAME_OR_PATH in state:
            del state[TrainingInputLiterals.MODEL_NAME_OR_PATH]
        if TrainingInputLiterals.TOKENIZER_NAME_OR_PATH in state:
            del state[TrainingInputLiterals.TOKENIZER_NAME_OR_PATH]
        return state

    def __setstate__(self, state):
        """
        Override on the object's __setstate__ method, to be used during deserialization.

        :param state: the state from which we'll recreate the training configuration object.
        :return: None.
        """
        self._settings_dict = state
