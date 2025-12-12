# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Distributed extension of ONNXRuntime Trainer for HF training."""
from torch.utils.data import Dataset
from typing import Dict, List, Optional

import logging

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import \
    RuntimeModuleDependencyMissing
from azureml.automl.core.shared.exceptions import ConfigException

_logger = logging.getLogger(__name__)

try:
    from optimum.onnxruntime import ORTTrainer
    has_ort = True
except ImportError as ie:
    _logger.warning("ONNXRuntime unavailable in environment. Distributed training will be disabled.")
    has_ort = False
    _logger.info(str(ie))

    class ORTTrainer:
        """Skeleton class definition to avoid complaints when ORT/optimum modules not present."""
        def __init__(self, model, args, train_dataset, **kwargs):
            """Empty initializer."""
            pass

        def evaluate(self, eval_dataset):
            """Empty eval method."""
            pass

        def predict(self, test_dataset):
            """Empty predict method."""
            pass


class ORTDeepspeedTrainer(ORTTrainer):
    """Class to extend ONNX Runtime trainer. Leverage ORT + DeepSpeed for distributed training."""

    def __init__(self, model, args, train_dataset, **kwargs):
        """
        Initializer for ONNX Runtime / DeepSpeed distributed trainer.

        :param model: model to be trained.
        :param args: HF training args to be used.
        :param train_dataset: dataset to train on.
        :return: None.
        """
        if not has_ort:
            raise ConfigException._with_error(
                AzureMLError.create(RuntimeModuleDependencyMissing, target="optimum", module_name="optimum")
            )
        super().__init__(model=model,
                         args=args,
                         train_dataset=train_dataset,
                         **kwargs)

    def evaluate(self,
                 eval_dataset: Optional[Dataset] = None,
                 ignore_keys: Optional[List[str]] = None,
                 metric_key_prefix: str = "eval",) -> Dict[str, float]:
        """
        Override of HF trainer so only the main process executes it.
        :param eval_dataset: dataset to use for evaluation.
        :param ignore_keys: A list of keys in the output of your model (if it is a dictionary) that should
                            be ignored when gathering predictions.
        :param metric_key_prefix: An optional prefix to be used as the metrics key prefix. For example the
                                  metrics "bleu" will be named "eval_bleu" if the prefix is "eval" (default)
        :return: eval result (predictions)
        """
        return super().evaluate(eval_dataset=eval_dataset,
                                ignore_keys=ignore_keys,
                                metric_key_prefix=metric_key_prefix)

    def predict(self,
                test_dataset,
                ignore_keys: Optional[List[str]] = None,
                metric_key_prefix: str = "test",):
        """
        Override of HF trainer's predict so only the main process executes it.
        :param test_dataset: dataset to use for prediction.
        :param ignore_keys: A list of keys in the output of your model (if it is a dictionary) that should
                            be ignored when gathering predictions.
        :param metric_key_prefix: An optional prefix to be used as the metrics key prefix. For example the
                                  metrics "bleu" will be named "test_bleu" if the prefix is "test" (default)
        :return: eval result (predictions)
        """
        return super().predict(test_dataset=test_dataset,
                               ignore_keys=ignore_keys,
                               metric_key_prefix=metric_key_prefix)
