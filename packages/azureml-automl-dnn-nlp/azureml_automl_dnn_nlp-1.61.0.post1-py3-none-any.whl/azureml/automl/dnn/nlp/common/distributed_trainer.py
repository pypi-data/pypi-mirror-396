# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Distributed extension of HF Trainer using Horovod"""
from functools import cached_property
from torch.utils.data import DistributedSampler
from transformers import Trainer, TrainingArguments

import logging
import torch

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import \
    RuntimeModuleDependencyMissing
from azureml.automl.core.shared.exceptions import ConfigException

_logger = logging.getLogger(__name__)


try:
    import horovod.torch as hvd
    from horovod.common.util import gpu_available
    has_horovod = True
except Exception as e:
    _logger.warning("Horovod unavailable in environment. Distributed training will be disabled")
    has_horovod = False
    _logger.info(str(e))


class DistributedTrainingArguments(TrainingArguments):
    """Class to extend HF Training Arguments to support distributed cuda setup with Horovod"""

    def __init__(self, training_args):
        """
        Function to initialize DistributedTrainingArguments similar to the TrainingArguments
        param training_args: HF training args to be used
        """
        super().__init__(output_dir=training_args.output_dir,
                         per_device_train_batch_size=training_args.per_device_train_batch_size,
                         per_device_eval_batch_size=training_args.per_device_eval_batch_size,
                         num_train_epochs=training_args.num_train_epochs,
                         save_strategy=training_args.save_strategy,
                         gradient_accumulation_steps=training_args.gradient_accumulation_steps,
                         learning_rate=training_args.learning_rate,
                         weight_decay=training_args.weight_decay,
                         warmup_ratio=training_args.warmup_ratio,
                         lr_scheduler_type=training_args.lr_scheduler_type,
                         logging_strategy=training_args.logging_strategy,
                         logging_steps=training_args.logging_steps,
                         eval_strategy=training_args.eval_strategy,
                         eval_steps=training_args.eval_steps,
                         report_to=training_args.report_to)

    @cached_property
    def _setup_devices(self) -> "torch.device":
        """
        Function sets cuda device using horovod's local rank (same as mpi local rank) and returns current device
        :return current cuda device
        """
        self._n_gpu = 1
        self.distributed_state = None
        torch.cuda.set_device(hvd.local_rank())
        return torch.device("cuda", hvd.local_rank())

    @property
    def n_gpu(self):
        """
        Function to override n_gpu value for distributed horovod training, which is always 1
        :return n_gpu value, which is 1 for horovod training
        """
        return self._n_gpu


class DistributedTrainer(Trainer):
    """Class to extend HF trainer to distributed mode using Horovod"""

    def __init__(self, model, args, train_dataset, **kwargs):
        """
        Function to initialize DistributedTrainer ready horovod for distributed training

        :param model: text classification model to be trained
        :param args: HF training args to be used
        :param train_dataset: classification text dataset with labels
        """
        if not has_horovod:
            raise ConfigException._with_error(
                AzureMLError.create(RuntimeModuleDependencyMissing, target="horovod", module_name="horovod")
            )
        if not gpu_available('torch'):
            _logger.warning("Horovod could not find GPUs")

        hvd.init()
        args = DistributedTrainingArguments(args)
        args.learning_rate = hvd.local_size() * args.learning_rate

        super().__init__(model=model,
                         args=args,
                         train_dataset=train_dataset,
                         **kwargs)
        hvd.broadcast_parameters(self.model.state_dict(), root_rank=0)

    def create_optimizer(self):
        """
        Function to override optimizer initializaiton in HF trainer to use distributed optimizer
        This function also broadcasts the initial optimizer state to all nodes to keep it consistent
        """
        super().create_optimizer()
        self.optimizer = hvd.DistributedOptimizer(
            self.optimizer,
            backward_passes_per_step=(
                self.args.gradient_accumulation_steps + 1
                if self.args.gradient_accumulation_steps > 1 else 1),
            named_parameters=self.model.named_parameters(),
            compression=hvd.Compression.fp16, op=hvd.Adasum)
        hvd.broadcast_optimizer_state(self.optimizer, root_rank=0)

    def _get_train_sampler(self, train_dataset):
        """
        Function to update sampler used for distributed training
        :return sampler for the local partition of the dataset
        """
        return DistributedSampler(train_dataset, num_replicas=hvd.size(), rank=hvd.rank())
