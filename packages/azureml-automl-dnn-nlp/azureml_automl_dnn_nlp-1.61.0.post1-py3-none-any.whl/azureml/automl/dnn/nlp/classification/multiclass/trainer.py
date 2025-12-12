# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2020 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------
"""Finetuning the library models for multi-class classification."""
from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer
from transformers.data.data_collator import default_data_collator
from transformers.trainer import Trainer

import logging
import numpy as np
import os

from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.core.shared.utilities import _convert_memory_exceptions
from azureml.automl.dnn.nlp.classification.multiclass.utils import compute_metrics
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import MulticlassDatasetWrapper
from azureml.automl.dnn.nlp.common._utils import calc_inter_eval_freq, is_main_process, get_trainer_arg
from azureml.automl.dnn.nlp.common.automl_callback import AutoMLCallback
from azureml.automl.dnn.nlp.common.constants import \
    OutputLiterals, TrainingDefaultSettings, TrainingInputLiterals, SystemSettings
from azureml.automl.dnn.nlp.common.distributed_trainer import DistributedTrainer
from azureml.automl.dnn.nlp.common.ort_deepspeed_trainer import ORTDeepspeedTrainer
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration

_logger = logging.getLogger(__name__)


class TextClassificationTrainer:
    """Class to perform training on a text classification model given a dataset"""

    def __init__(self,
                 train_label_list: np.ndarray,
                 label_list: np.ndarray,
                 training_configuration: TrainingConfiguration,
                 enable_distributed: bool = False,
                 enable_distributed_ort_ds: bool = False) -> None:
        """
        Function to initialize text-classification trainer.

        :param train_label_list: List of labels coming from the training data.
        :param label_list: List of labels across both training and validation sets.
        :param training_configuration: A collection of parameters to dictate the training procedure.
        :param enable_distributed: Enable distributed training on multiple gpus and machines.
        :param enable_distributed_ort_ds: Enable distributed training using ORT and DeepSpeed on multiple gpus/machines
        :return: None.
        """
        self.train_label_list = train_label_list
        self.class_label_list = label_list
        self.num_labels = len(train_label_list)
        self.enable_distributed = enable_distributed
        self.enable_distributed_ort_ds = enable_distributed_ort_ds
        self.training_configuration = training_configuration

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.training_configuration[TrainingInputLiterals.TOKENIZER_NAME_OR_PATH], use_fast=True)
        # Config JSON lives in same directory as tokenizer.
        self.config = AutoConfig.from_pretrained(
            self.tokenizer.name_or_path,
            num_labels=self.num_labels,
            use_mems_eval=self.training_configuration[TrainingInputLiterals.USE_MEMS_EVAL])

        # Load model
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.training_configuration[TrainingInputLiterals.MODEL_NAME_OR_PATH],
            from_tf=False,
            config=self.config,
        )
        self.trainer = None

        # Padding strategy
        self.data_collator = None
        if training_configuration[TrainingInputLiterals.PADDING_STRATEGY]:
            self.data_collator = default_data_collator

    @_convert_memory_exceptions
    def train(self,
              train_dataset: MulticlassDatasetWrapper,
              validation_dataset: MulticlassDatasetWrapper) -> None:
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

            # max_seq_length_multiplier is the ratio of current max seq len to the default max seq len
            max_seq_length_multiplier = \
                int(train_dataset.max_seq_length) / TrainingDefaultSettings.DEFAULT_SEQ_LEN
            # Higher max seq len requires larger GPU memory to fit the larger model, and hence we reduce
            # train batch size by the same ratio (by which max seq len increased). Increasing the gradient accum.
            # steps by this ratio allows us to preserve the effective train batch size compared to the defaults.

            if self.training_configuration[TrainingInputLiterals.USE_SEQ_LEN_MULTIPLIER]:
                self.training_configuration[TrainingInputLiterals.TRAIN_BATCH_SIZE] = \
                    int(self.training_configuration[TrainingInputLiterals.TRAIN_BATCH_SIZE]
                        / max_seq_length_multiplier)
                self.training_configuration[TrainingInputLiterals.GRADIENT_ACCUMULATION_STEPS] = \
                    int(self.training_configuration[TrainingInputLiterals.GRADIENT_ACCUMULATION_STEPS]
                        * max_seq_length_multiplier)
            _logger.info("Train Batch Size = {}\nGradient Accumulation Steps = {}".format(
                self.training_configuration[TrainingInputLiterals.TRAIN_BATCH_SIZE],
                self.training_configuration[TrainingInputLiterals.GRADIENT_ACCUMULATION_STEPS]))

            deepspeed_config = None
            if os.path.exists(SystemSettings.DEEP_SPEED_CONFIG):
                _logger.info("Found DeepSpeed configuration. Enabling fp16 training.")
                deepspeed_config = SystemSettings.DEEP_SPEED_CONFIG

            intermediary_eval_freq = calc_inter_eval_freq(len(train_dataset), self.training_configuration)

            trainer_arg_cls = get_trainer_arg(self.enable_distributed_ort_ds)

            # TODO: Investigate fp16 training for non-ORT/DS scenarios.
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
                    data_collator=self.data_collator,
                    callbacks=[AutoMLCallback()],
                    compute_metrics=lambda eval_result: compute_metrics(validation_dataset.labels,
                                                                        eval_result.predictions,
                                                                        self.class_label_list,
                                                                        self.train_label_list)
                )
            else:
                self.trainer = Trainer(
                    model=self.model,
                    args=self.training_args,
                    train_dataset=train_dataset,
                    eval_dataset=validation_dataset,
                    processing_class=self.tokenizer,
                    data_collator=self.data_collator,
                    callbacks=[AutoMLCallback()],
                    compute_metrics=lambda eval_result: compute_metrics(validation_dataset.labels,
                                                                        eval_result.predictions,
                                                                        self.class_label_list,
                                                                        self.train_label_list)
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
                if not os.path.exists(OutputLiterals.OUTPUT_DIR):
                    os.mkdir(OutputLiterals.OUTPUT_DIR)
                np.save(OutputLiterals.OUTPUT_DIR + '/' + OutputLiterals.LABEL_LIST_FILE_NAME, self.class_label_list)

    @_convert_memory_exceptions
    def validate(self, eval_dataset: MulticlassDatasetWrapper) -> np.ndarray:
        """
        Function to perform evaluate on the model given the trainer object and validation dataset

        :param eval_dataset: PyTorchDataset object containing validation data
        :return resulting predictions for the val dataset (from the cross entropy loss)
        """
        with log_utils.log_activity(
            _logger,
            activity_name=constants.TelemetryConstants.VALIDATION
        ):
            return self.trainer.predict(test_dataset=eval_dataset).predictions
