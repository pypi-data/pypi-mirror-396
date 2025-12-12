# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for training Pytorch Models"""
from typing import Tuple
from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer
from transformers.trainer import Trainer

import logging
import numpy as np
import os

from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.core.shared.utilities import _convert_memory_exceptions
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import MultilabelDatasetWrapper
from azureml.automl.dnn.nlp.classification.multilabel.utils import compute_constant_metrics
from azureml.automl.dnn.nlp.common._utils import calc_inter_eval_freq, is_main_process, get_trainer_arg
from azureml.automl.dnn.nlp.common.automl_callback import AutoMLCallback
from azureml.automl.dnn.nlp.common.constants import TrainingInputLiterals, OutputLiterals, SystemSettings
from azureml.automl.dnn.nlp.common.distributed_trainer import DistributedTrainer
from azureml.automl.dnn.nlp.common.ort_deepspeed_trainer import ORTDeepspeedTrainer
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration

_logger = logging.getLogger(__name__)


class PytorchTrainer:
    """Class to perform training on a model given a dataset"""
    def __init__(self,
                 training_configuration: TrainingConfiguration,
                 num_label_cols: int,
                 enable_distributed: bool = False,
                 enable_distributed_ort_ds: bool = False) -> None:
        """
        Function to initialize pytorch trainer.

        :param training_configuration: a collection of parameters to dictate the training procedure.
        :param num_label_cols: Number of unique classes in label column.
        :param enable_distributed: Enable multi-gpu and/or multi-node distributed training.
        :param enable_distributed_ort_ds: is distributed enabled (onnxruntime/deepspeed).
        :return: None.
        """
        self.training_configuration = training_configuration

        self.tokenizer = \
            AutoTokenizer.from_pretrained(training_configuration[TrainingInputLiterals.TOKENIZER_NAME_OR_PATH],
                                          use_fast=True)
        self.config = AutoConfig.from_pretrained(
            self.tokenizer.name_or_path,
            problem_type='multi_label_classification',
            num_labels=num_label_cols,
            use_mems_eval=self.training_configuration[TrainingInputLiterals.USE_MEMS_EVAL]
        )

        self.model = AutoModelForSequenceClassification.from_pretrained(
            training_configuration[TrainingInputLiterals.MODEL_NAME_OR_PATH],
            from_tf=False,
            config=self.config
        )

        self.enable_distributed = enable_distributed
        self.enable_distributed_ort_ds = enable_distributed_ort_ds
        self.trainer = None

    @_convert_memory_exceptions
    def train(self,
              train_dataset: MultilabelDatasetWrapper,
              validation_dataset: MultilabelDatasetWrapper) -> None:
        """
        Function to perform training on the model given a training dataset.

        :param train_dataset: Training dataset wrapped in object adhering to HF interface.
        :param validation_dataset: Validation dataset wrapped in object adhering to HF interface.
        :return: None.
        """
        with log_utils.log_activity(
            _logger,
            activity_name=constants.TelemetryConstants.TRAINING
        ):
            deepspeed_config = None
            if os.path.exists(SystemSettings.DEEP_SPEED_CONFIG):
                _logger.info("Found DeepSpeed configuration. Enabling fp16 training.")
                deepspeed_config = SystemSettings.DEEP_SPEED_CONFIG

            intermediary_eval_freq = calc_inter_eval_freq(len(train_dataset), self.training_configuration)

            trainer_arg_cls = get_trainer_arg(self.enable_distributed_ort_ds)

            self.training_args = trainer_arg_cls(
                output_dir=OutputLiterals.OUTPUT_DIR,
                per_device_train_batch_size=self.training_configuration[TrainingInputLiterals.TRAIN_BATCH_SIZE],
                per_device_eval_batch_size=self.training_configuration[TrainingInputLiterals.VALID_BATCH_SIZE],
                num_train_epochs=self.training_configuration[TrainingInputLiterals.NUM_TRAIN_EPOCHS],
                save_strategy=self.training_configuration[TrainingInputLiterals.SAVE_STRATEGY],
                gradient_accumulation_steps=self.training_configuration[
                    TrainingInputLiterals.GRADIENT_ACCUMULATION_STEPS],
                learning_rate=self.training_configuration[TrainingInputLiterals.LEARNING_RATE],
                weight_decay=self.training_configuration[TrainingInputLiterals.WEIGHT_DECAY],
                warmup_ratio=self.training_configuration[TrainingInputLiterals.WARMUP_RATIO],
                lr_scheduler_type=self.training_configuration[TrainingInputLiterals.LR_SCHEDULER_TYPE],
                logging_strategy=self.training_configuration[TrainingInputLiterals.LOGGING_STRATEGY],
                logging_steps=intermediary_eval_freq,
                report_to=self.training_configuration[TrainingInputLiterals.REPORT_TO],
                eval_strategy=self.training_configuration[TrainingInputLiterals.EVAL_STRATEGY],
                eval_steps=intermediary_eval_freq,
                deepspeed=deepspeed_config,
                fp16=deepspeed_config is not None
            )

            if self.enable_distributed or self.enable_distributed_ort_ds:
                distributed_trainer_class = DistributedTrainer if self.enable_distributed else ORTDeepspeedTrainer
                self.trainer = distributed_trainer_class(
                    model=self.model,
                    args=self.training_args,
                    train_dataset=train_dataset,
                    eval_dataset=validation_dataset,
                    processing_class=self.tokenizer,
                    callbacks=[AutoMLCallback()],
                    compute_metrics=lambda eval_result: compute_constant_metrics(eval_result.predictions,
                                                                                 validation_dataset.labels,
                                                                                 validation_dataset.y_transformer)
                )
            else:
                self.trainer = Trainer(
                    model=self.model,
                    args=self.training_args,
                    train_dataset=train_dataset,
                    eval_dataset=validation_dataset,
                    processing_class=self.tokenizer,
                    callbacks=[AutoMLCallback()],
                    compute_metrics=lambda eval_result: compute_constant_metrics(eval_result.predictions,
                                                                                 validation_dataset.labels,
                                                                                 validation_dataset.y_transformer)
                )

            train_result = self.trainer.train()
            if is_main_process():
                metrics = train_result.metrics
                self.trainer.save_model()  # Saves the tokenizer too for easy upload
                self.trainer.save_metrics("train", metrics)
                self.trainer.save_state()
                if self.enable_distributed_ort_ds:
                    # Update model for reference later; also can be updated to use state dict
                    # This is added for now due to ORTTrainer.model returning ORTModule
                    import torch
                    torch.save(self.trainer.model.state_dict(),
                               os.path.join(OutputLiterals.OUTPUT_DIR, OutputLiterals.PT_MODEL_BIN_FILE_NAME))
                    self.model = AutoModelForSequenceClassification.from_pretrained(
                        os.path.join(OutputLiterals.OUTPUT_DIR, OutputLiterals.PT_MODEL_BIN_FILE_NAME),
                        from_tf=False,
                        config=self.config
                    )

    @_convert_memory_exceptions
    def validate(self, eval_dataset: MultilabelDatasetWrapper) -> Tuple[np.ndarray, np.ndarray]:
        """
        Function to perform evaluate on the model given the trainer object and validation dataset

        :param eval_dataset: PyTorchDataset object containing labeled validation data
        :return: Tuple of (n_rows x n_labels) prediction matrix for the val dataset (from the cross entropy loss),
        ground truth label ids (one hot encoded).
        """
        with log_utils.log_activity(
                _logger,
                activity_name=constants.TelemetryConstants.VALIDATION
        ):
            predict = self.trainer.predict(test_dataset=eval_dataset)
            return predict.predictions, predict.label_ids
