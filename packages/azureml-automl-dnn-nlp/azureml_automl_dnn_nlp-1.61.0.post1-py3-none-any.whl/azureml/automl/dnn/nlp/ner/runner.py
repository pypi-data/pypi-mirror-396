# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Entry script that is invoked by the driver script from automl."""

from typing import Any, Dict, Optional
from transformers import AutoTokenizer

import importlib
import logging
import numpy as np
import os
import torch

from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.shared.constants import Tasks
from azureml.automl.dnn.nlp.common._utils import (
    _get_language_code,
    create_unique_dir,
    is_data_labeling_run,
    prepare_run_properties,
    prepare_post_run_properties,
    save_script,
    save_conda_yml,
    scrub_system_exception,
    set_env_vars,
    is_main_process,
    save_deploy_script,
    RootLoggingFilter
)
from azureml.automl.dnn.nlp.common.constants import DataLiterals, OutputLiterals, \
    ScoringLiterals, TrainingInputLiterals, SuppressedWarningPrefixes
from azureml.automl.dnn.nlp.common.io.utils import save_model_wrapper
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration
from azureml.automl.dnn.nlp.ner._utils import log_metrics
from azureml.automl.dnn.nlp.ner.io.read.dataloader import load_and_validate_dataset
from azureml.automl.dnn.nlp.ner.model_wrapper import ModelWrapper
from azureml.automl.dnn.nlp.ner.trainer import NERPytorchTrainer
from azureml.core.run import Run
from azureml.train.automl.runtime._code_generation.utilities import generate_nlp_code_and_notebook
from azureml.train.automl.runtime._entrypoints.utils.common import initialize_log_server

_logger = logging.getLogger(__name__)

horovod_spec = importlib.util.find_spec("horovod")
has_horovod = horovod_spec is not None


def run(
        automl_settings: Dict[str, Any],
        mltable_data_json: Optional[str] = None,
        **kwargs: Any
):
    """
    Invoke training by passing settings and write the output model.

    :param automl_settings: dictionary with automl settings
    :param mltable_data_json: mltable data json containing location of data
    """
    # Get Run Info
    current_run = Run.get_context()

    try:
        workspace = current_run.experiment.workspace

        # Parse settings
        with RootLoggingFilter(SuppressedWarningPrefixes.ALL):
            automl_settings_obj = initialize_log_server(current_run, automl_settings)
        # checking if run is from data labeling project; data labeling run has different input dataset format
        is_labeling_run = is_data_labeling_run(current_run)
        # Get primary metric
        primary_metric = automl_settings_obj.primary_metric
        # Get dataset language
        dataset_language = _get_language_code(automl_settings_obj.featurization)
        # Get enable distributed dnn training
        distributed = hasattr(automl_settings_obj, "enable_distributed_dnn_training") and \
            ((automl_settings_obj.enable_distributed_dnn_training is True)
             or (automl_settings_obj.enable_distributed_dnn_training == 'True')) and has_horovod
        # Get enable distributed dnn training for ORT and DeepSpeed
        distributed_ort_ds = hasattr(automl_settings_obj, "enable_distributed_dnn_training_ort_ds") and \
            ((automl_settings_obj.enable_distributed_dnn_training_ort_ds is True)
             or (automl_settings_obj.enable_distributed_dnn_training_ort_ds == 'True'))
        if distributed:
            _logger.info("horovod enabled: {}".format(distributed))
        elif distributed_ort_ds:
            _logger.info("ORT DS enabled: {}".format(distributed_ort_ds))

        # Set Defaults
        ner_dir = create_unique_dir(DataLiterals.NER_DATA_DIR)
        output_dir = OutputLiterals.OUTPUT_DIR
        labels_filename = OutputLiterals.LABELS_FILE
        set_env_vars()

        # Get training configuration
        training_configuration = TrainingConfiguration.populate_from_scope(task_type=Tasks.TEXT_NER,
                                                                           dataset_language=dataset_language,
                                                                           automl_settings=automl_settings)

        # Set run properties
        prepare_run_properties(current_run, training_configuration[TrainingInputLiterals.MODEL_NAME])

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            training_configuration[TrainingInputLiterals.TOKENIZER_NAME_OR_PATH],
            add_prefix_space=training_configuration[TrainingInputLiterals.ADD_PREFIX_SPACE])

        # Save and load dataset
        train_dataset, eval_dataset, label_list = load_and_validate_dataset(
            workspace,
            ner_dir,
            output_dir,
            labels_filename,
            tokenizer,
            automl_settings,
            training_configuration,
            mltable_data_json,
            is_labeling_run
        )

        # Train model
        trainer = NERPytorchTrainer(
            training_configuration,
            label_list,
            output_dir,
            enable_distributed=distributed,
            enable_distributed_ort_ds=distributed_ort_ds
        )
        # Choose device
        if distributed and "LOCAL_RANK" in os.environ:
            local_rank = int(os.environ.get("LOCAL_RANK", 0))
            device = torch.device(f'cuda:{local_rank}' if torch.cuda.is_available() else 'cpu')
        else:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        trainer.model.to(device)
        # Log model device
        model_device = next(trainer.model.parameters()).device
        _logger.debug(f"[DEBUG]Model is on device: {model_device}")

        trainer.train(train_dataset, eval_dataset)

        primary_metric_score = np.nan
        # Validate model if validation dataset is provided
        if eval_dataset is not None:
            results = trainer.validate(eval_dataset)
            if is_main_process():
                log_metrics(current_run, results)
                primary_metric_score = results[primary_metric]

        # Save model artifacts
        if is_main_process():
            tokenizer.save_pretrained(output_dir)
            input_sample_str = "\"This\\nis\\nan\\nexample\""
            output_sample_str = "\"This O\\nis O\\nan O\\n example B-OBJ\""

            # Convert sample strings to np array (every item in conll file is one sample) to meet mlflow contract
            input_mlflow_str = 'np.array([None])'
            output_mlflow_str = 'np.array([None])'
            inf_model = trainer.trainer.model
            # Save for inference
            if distributed_ort_ds:
                inf_model = trainer.model
            model_wrapper = ModelWrapper(inf_model, label_list, tokenizer, training_configuration)
            model_path = save_model_wrapper(run=current_run, model=model_wrapper,
                                            save_mlflow=automl_settings_obj.save_mlflow,
                                            input_sample_str=input_mlflow_str,
                                            output_sample_str=output_mlflow_str)

            # Save scoring script
            ner_write_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "io", "write")
            save_script(OutputLiterals.SCORE_SCRIPT, ner_write_dir)

            deploy_script_path = save_deploy_script(ScoringLiterals.NER_SCORE_FILE,
                                                    input_sample_str,
                                                    output_sample_str,
                                                    "StandardPythonParameterType")
            conda_file_path = save_conda_yml()

            prepare_post_run_properties(current_run,
                                        model_path,
                                        2147483648,
                                        conda_file_path,
                                        deploy_script_path,
                                        primary_metric,
                                        primary_metric_score)

            _logger.info("Code generation enabled: {}".format(automl_settings_obj.enable_code_generation))
            if automl_settings_obj.enable_code_generation:
                generate_nlp_code_and_notebook(current_run)
    except Exception as e:
        _logger.error("NER runner script terminated with an exception of type: {}".format(type(e)))
        run_lifecycle_utilities.fail_run(current_run, scrub_system_exception(e), update_run_properties=True)
        raise
