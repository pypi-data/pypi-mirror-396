# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Callback for AutoNLP that leverages the HF trainer to perform training."""
from typing import Any, Dict, Optional
from transformers import TrainingArguments, TrainerControl, TrainerState
from transformers.integrations import AzureMLCallback

from azureml.automl.dnn.nlp.common.constants import LoggingLiterals


class AutoMLCallback(AzureMLCallback):
    """
    Leverage the AzureMLCallback object to log training metrics to the backing AML run.
    Override the on_log method to strip metrics of their metric_key_prefix (e.g. "eval_")
    to maintain parity with the rest of AML metrics.

    Documentation for the metric_key_prefix can be found:
    https://huggingface.co/docs/transformers/main_classes/trainer#transformers.Trainer.evaluate.metric_key_prefix
    """
    def on_log(self,
               args: TrainingArguments,
               state: TrainerState,
               control: TrainerControl,
               logs: Optional[Dict[str, float]] = None,
               **kwargs: Any) -> None:
        """
        Before logging metrics to the backing AML run, strip them of their HF prefixes. That is, go from
        'eval_accuracy' to 'accuracy,' maintaining parity with the rest of AutoML training.

        :param args: the training settings, stored in a HF TrainingArguments object.
        :param state: the state of the HF trainer.
        :param control: the control object for the HF trainer.
        :param logs: the key-value pairs to be logged to the AML run; what we're actually logging.
        :params kwargs: extra keyword arguments.
        :return: None.
        """
        if self.azureml_run and state.is_world_process_zero and logs is not None:
            cleaned_logs = {}
            for k, v in logs.items():
                if k.startswith(LoggingLiterals.EVAL_PREFIX) or k.startswith(LoggingLiterals.TEST_PREFIX):
                    k = k.split("_", 1)[1]
                    cleaned_logs[k] = v
            super(AutoMLCallback, self).on_log(args, state, control, cleaned_logs, **kwargs)
