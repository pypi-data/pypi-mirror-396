# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Objects and related constants for model training."""
from transformers.trainer_utils import IntervalStrategy, SchedulerType
from typing import Any, Dict

from .constants import ModelNames, TrainingInputLiterals, TrainingDefaultSettings
from azureml.automl.core.shared.constants import Tasks

# Default training parameters for all NLP training. To be overridden by task- and model-specific values.
# NLP defaults are based on defaults recommended in the BERT paper.
DEFAULT_NLP_PARAMETERS = {
    TrainingInputLiterals.LOGGING_STRATEGY: IntervalStrategy.STEPS,
    TrainingInputLiterals.REPORT_TO: TrainingDefaultSettings.NO_REPORTING,
    TrainingInputLiterals.SAVE_STRATEGY: IntervalStrategy.NO,
    TrainingInputLiterals.EVAL_STRATEGY: IntervalStrategy.STEPS,
    TrainingInputLiterals.PADDING_STRATEGY: TrainingDefaultSettings.MAX_LENGTH,
    TrainingInputLiterals.MAX_SEQ_LENGTH: TrainingDefaultSettings.DEFAULT_SEQ_LEN,
    # Long range is not supported by all tasks yet, so the default is the same.
    TrainingInputLiterals.LONG_RANGE_LENGTH: TrainingDefaultSettings.DEFAULT_SEQ_LEN,
    TrainingInputLiterals.LONG_RANGE_THRESHOLD: TrainingDefaultSettings.MIN_PROPORTION_LONG_RANGE,
    TrainingInputLiterals.USE_SEQ_LEN_MULTIPLIER: True,
    TrainingInputLiterals.NUM_TRAIN_EPOCHS: 3,
    TrainingInputLiterals.TRAIN_BATCH_SIZE: 32,
    TrainingInputLiterals.VALID_BATCH_SIZE: 32,
    TrainingInputLiterals.GRADIENT_ACCUMULATION_STEPS: 1,
    TrainingInputLiterals.LEARNING_RATE: 5e-5,
    TrainingInputLiterals.WEIGHT_DECAY: 0.0,
    TrainingInputLiterals.WARMUP_RATIO: 0.0,
    TrainingInputLiterals.LR_SCHEDULER_TYPE: SchedulerType.LINEAR,
    # Set USE_MEMS_EVAL to False everywhere. This is only used for XLNet to avoid conflicts with DataParallel and
    # gpu-indivisible batch sizes, causing failures on the gathering of the mem-states. Other models' configs
    # will just ignore extraneous parameters, though, so we'll set it universally to avoid having construction forks
    # (or loose parameter dicts and do some sort of kwarg expansion).
    TrainingInputLiterals.USE_MEMS_EVAL: False
}

# Multiclass-related parameters
DEFAULT_MULTICLASS_PARAMETERS = {
    TrainingInputLiterals.LONG_RANGE_LENGTH: TrainingDefaultSettings.LONG_RANGE_MAX
}

# Multilabel-related parameters
DEFAULT_MULTILABEL_PARAMETERS = {}  # No multilabel-specific parameters at this time.

# NER-related parameters
DEFAULT_NER_PARAMETERS = {
    TrainingInputLiterals.ADD_PREFIX_SPACE: False,
    TrainingInputLiterals.FINETUNING_TASK: TrainingDefaultSettings.NER
}

DEFAULT_NER_ROBERTA_PARAMETERS = {
    TrainingInputLiterals.ADD_PREFIX_SPACE: True
}

# Model-specific parameters
DEFAULT_ROBERTA_PARAMETERS = {
    TrainingInputLiterals.LEARNING_RATE: 2e-5,
    TrainingInputLiterals.LR_SCHEDULER_TYPE: SchedulerType.LINEAR,
    TrainingInputLiterals.WARMUP_RATIO: 0.06,
    TrainingInputLiterals.WEIGHT_DECAY: 0.1
}

DEFAULT_XLNET_PARAMETERS = {
    TrainingInputLiterals.LEARNING_RATE: 1e-5,
    TrainingInputLiterals.LR_SCHEDULER_TYPE: SchedulerType.LINEAR,
    TrainingInputLiterals.MAX_SEQ_LENGTH: 128,
    TrainingInputLiterals.WEIGHT_DECAY: 0.01
}


class DefaultParameterFactory:
    """Object for retrieving the set of parameters corresponding to the given training scenario."""

    TASK_TO_PARAM_MAPPING = {
        Tasks.TEXT_CLASSIFICATION: DEFAULT_MULTICLASS_PARAMETERS,
        Tasks.TEXT_CLASSIFICATION_MULTILABEL: DEFAULT_MULTILABEL_PARAMETERS,
        Tasks.TEXT_NER: DEFAULT_NER_PARAMETERS
    }

    MODEL_TO_PARAM_MAPPING = {
        ModelNames.DISTILROBERTA_BASE: DEFAULT_ROBERTA_PARAMETERS,
        ModelNames.ROBERTA_BASE: DEFAULT_ROBERTA_PARAMETERS,
        ModelNames.ROBERTA_LARGE: DEFAULT_ROBERTA_PARAMETERS,
        ModelNames.XLM_ROBERTA_BASE: DEFAULT_ROBERTA_PARAMETERS,
        ModelNames.XLM_ROBERTA_LARGE: DEFAULT_ROBERTA_PARAMETERS,
        ModelNames.XLNET_BASE_CASED: DEFAULT_XLNET_PARAMETERS,
        ModelNames.XLNET_LARGE_CASED: DEFAULT_XLNET_PARAMETERS
    }

    TASK_MODEL_TO_PARAM_MAPPING = {
        (Tasks.TEXT_NER, ModelNames.DISTILROBERTA_BASE): DEFAULT_NER_ROBERTA_PARAMETERS,
        (Tasks.TEXT_NER, ModelNames.ROBERTA_BASE): DEFAULT_NER_ROBERTA_PARAMETERS,
        (Tasks.TEXT_NER, ModelNames.ROBERTA_LARGE): DEFAULT_NER_ROBERTA_PARAMETERS
    }

    @classmethod
    def get(cls, task_type: str, model_name: str) -> Dict[str, Any]:
        """
        Given N supported models and K supported tasks, we have NK possible unique parameter sets. Rather than
        having NK individual objects or a complicated inheritance tree in an attempt to reduce shared parameter
        repetition, we have a few different default sets and update those bases with fragments of parameters unique
        to the scenario at hand. Some parameters are task-agnostic, some are model-agnostic, and some are both. This
        class builds and returns the parameter base set for the given training scenario.

        :param task_type: the training scenario type, e.g. text-classification, text-ner.
        :param model_name: the name of the underlying model, e.g. bert-base-cased, roberta-base.
        :return: dictionary of default settings specific to the training task and model.
        """
        settings = DEFAULT_NLP_PARAMETERS.copy()
        settings.update(cls.TASK_TO_PARAM_MAPPING[task_type])
        settings.update(cls.MODEL_TO_PARAM_MAPPING.get(model_name, {}))
        settings.update(cls.TASK_MODEL_TO_PARAM_MAPPING.get((task_type, model_name), {}))
        return settings
