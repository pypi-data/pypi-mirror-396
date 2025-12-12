# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Fine-tuning the library models for named entity recognition in CoNLL-2003 format."""
from typing import Any, Dict, List
from torch.utils.data import Dataset
from transformers import AutoConfig, AutoModelForTokenClassification
from transformers.trainer import Trainer

import logging
import os

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ExecutionFailure
from azureml.automl.core.shared.exceptions import ValidationException
from azureml.automl.core.shared.utilities import _convert_memory_exceptions
from azureml.automl.dnn.nlp.common._utils import calc_inter_eval_freq, is_main_process, get_trainer_arg
from azureml.automl.dnn.nlp.common.automl_callback import AutoMLCallback
from azureml.automl.dnn.nlp.common.constants import SystemSettings, TrainingInputLiterals, OutputLiterals
from azureml.automl.dnn.nlp.common.distributed_trainer import DistributedTrainer
from azureml.automl.dnn.nlp.common.ort_deepspeed_trainer import ORTDeepspeedTrainer
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration
from azureml.automl.dnn.nlp.ner._utils import remove_metric_prefix
from azureml.automl.dnn.nlp.ner.token_classification_metrics import TokenClassificationMetrics

logger = logging.getLogger(__name__)


class NERPytorchTrainer:
    """Class for training an NER model for a given dataset."""
    def __init__(
            self,
            training_configuration: TrainingConfiguration,
            label_list: List[str],
            output_dir: str,
            enable_distributed: bool = False,
            enable_distributed_ort_ds: bool = False
    ):
        """
        Function to initialize pytorch ner trainer

        :param training_configuration: a collection of parameters to dictate the training procedure.
        :param label_list: list of unique labels.
        :param output_dir: output directory to save results to.
        :param enable_distributed: whether distributed training is enabled.
        :param enable_distributed_ort_ds: is distributed enabled (onnxruntime/deepspeed)
        """
        self.training_configuration = training_configuration
        self.output_dir = output_dir
        self.enable_distributed = enable_distributed
        self.enable_distributed_ort_ds = enable_distributed_ort_ds

        self.label_list = label_list
        num_labels = len(label_list)

        # Load config
        self.config = AutoConfig.from_pretrained(
            training_configuration[TrainingInputLiterals.TOKENIZER_NAME_OR_PATH],
            num_labels=num_labels,
            finetuning_task=training_configuration[TrainingInputLiterals.FINETUNING_TASK],
            use_mems_eval=training_configuration[TrainingInputLiterals.USE_MEMS_EVAL]
        )

        # Load model
        self.model = AutoModelForTokenClassification.from_pretrained(
            training_configuration[TrainingInputLiterals.MODEL_NAME_OR_PATH],
            from_tf=False,
            config=self.config
        )

        self.trainer = None

    @_convert_memory_exceptions
    def train(
            self,
            train_dataset: Dataset,
            validation_dataset: Dataset
    ) -> None:
        """
        Function to perform training on the model given a training dataset.

        :param train_dataset: dataset to train with.
        :param validation_dataset: dataset for intermediary evaluation.
        :return: None.
        """
        with log_utils.log_activity(
                logger,
                activity_name=constants.TelemetryConstants.TRAINING
        ):
            # Create trainer
            token_classification_metrics = TokenClassificationMetrics(self.label_list)
            deepspeed_config = None
            if os.path.exists(SystemSettings.DEEP_SPEED_CONFIG):
                logger.info("Found DeepSpeed configuration. Enabling fp16 training.")
                deepspeed_config = SystemSettings.DEEP_SPEED_CONFIG

            intermediary_eval_freq = calc_inter_eval_freq(len(train_dataset), self.training_configuration)

            trainer_arg_cls = get_trainer_arg(self.enable_distributed_ort_ds)

            training_args = trainer_arg_cls(
                output_dir=self.output_dir,
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
                    args=training_args,
                    train_dataset=train_dataset,
                    eval_dataset=validation_dataset,
                    callbacks=[AutoMLCallback()],
                    compute_metrics=token_classification_metrics.compute_metrics
                )
            else:
                self.trainer = Trainer(
                    model=self.model,
                    args=training_args,
                    train_dataset=train_dataset,
                    eval_dataset=validation_dataset,
                    callbacks=[AutoMLCallback()],
                    compute_metrics=token_classification_metrics.compute_metrics
                )

            # Train
            self.trainer.train()

            # Save model
            if is_main_process():
                self.trainer.save_model()
                self.trainer.save_state()
                if self.enable_distributed_ort_ds:
                    # Update model for reference later; also can be updated to use state dict
                    # This is added for now due to ORTTrainer.model returning ORTModule
                    import torch
                    torch.save(self.trainer.model.state_dict(),
                               os.path.join(OutputLiterals.OUTPUT_DIR, OutputLiterals.PT_MODEL_BIN_FILE_NAME))
                    self.model = AutoModelForTokenClassification.from_pretrained(
                        os.path.join(OutputLiterals.OUTPUT_DIR, OutputLiterals.PT_MODEL_BIN_FILE_NAME),
                        from_tf=False,
                        config=self.config
                    )

    @_convert_memory_exceptions
    def validate(
            self,
            eval_dataset: Dataset
    ) -> Dict[str, Any]:
        """
        Function to perform evaluation on the trained model given a val dataset.
        :param eval_dataset: dataset to validate the model with
        :return:
        """
        if self.trainer is None:
            logger.error("Unable to validate when model has not been trained. Please train the model first.")
            raise ValidationException._with_error(
                AzureMLError.create(
                    ExecutionFailure,
                    operation_name="validate",
                    error_details="need to train before calling to validate"
                )
            )

        with log_utils.log_activity(
                logger,
                activity_name=constants.TelemetryConstants.VALIDATION
        ):
            metrics = self.trainer.evaluate(eval_dataset)
            metrics = remove_metric_prefix(metrics, "eval_")

        return metrics
