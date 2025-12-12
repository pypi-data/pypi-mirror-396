# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""I/O utility functions that are common to all tasks."""
from typing import TYPE_CHECKING, Optional

import logging
import numpy as np  # noqa: F401
import os
import platform
import pandas as pd  # noqa: F401
import pickle

from azureml.automl.core.shared import logging_utilities as log_utils
from azureml.automl.core.shared.constants import MLFlowLiterals, RUN_ID_OUTPUT_PATH, INFERENCE_DEPENDENCIES, MLFlowMetaLiterals
from azureml.automl.dnn.nlp.common._utils import intercept_vnet_failures
from azureml.automl.dnn.nlp.common.constants import LoggingLiterals, OutputLiterals, SystemSettings
from azureml.core.run import Run
from azureml.train.automl.runtime._azureautomlruncontext import AzureAutoMLRunContext
import azureml.automl.core.inference as inference
from azureml.core.conda_dependencies import CondaDependencies
from ..constants import TrainingInputLiterals, LoggingLiterals

if TYPE_CHECKING:
    from .._types import MODEL_WRAPPER_TYPE  # noqa: F401

_logger = logging.getLogger(__name__)

try:
    import mlflow
    has_mlflow = True
except ImportError:
    has_mlflow = False

try:
    import optimum
    has_optimum = True
except ImportError:
    has_optimum = False


def load_model_wrapper(run_object: Run,
                       artifacts_dir: str = OutputLiterals.OUTPUT_DIR) -> "MODEL_WRAPPER_TYPE":
    """
    Function to load wrapped model saved during training procedure.

    :param run_object: the training run.
    :param artifacts_dir: the directory from which to load the training artifacts. Usually 'outputs'.
    :return: model wrapper containing the pytorch model, tokenizer, etc.
    """
    with log_utils.log_activity(
        _logger,
        activity_name=LoggingLiterals.MODEL_RETRIEVAL
    ):
        run_object.download_file(os.path.join(artifacts_dir, OutputLiterals.MODEL_FILE_NAME),
                                 output_file_path=OutputLiterals.MODEL_FILE_NAME)

    _logger.info("Deserializing trained model.")
    with open(OutputLiterals.MODEL_FILE_NAME, "rb") as f:
        model = pickle.load(f)

    return model


@intercept_vnet_failures()
def save_model_wrapper(run: Run,
                       model: "MODEL_WRAPPER_TYPE",
                       save_mlflow: bool = True,
                       input_sample_str: Optional[str] = None,
                       output_sample_str: Optional[str] = None) -> str:
    """
    Save a model to outputs directory.

    :param run: The current run.
    :param model: Trained model.
    :param save_mlflow: Whether to save using mlflow.
    :param input_sample_str: input string for signature
    :param output_sample_str: output string for signature
    :return: The model path.
    """
    os.makedirs(OutputLiterals.OUTPUT_DIR, exist_ok=True)
    model_path = os.path.join(OutputLiterals.OUTPUT_DIR, OutputLiterals.MODEL_FILE_NAME)

    # Save the model
    run_ctx = AzureAutoMLRunContext(run)
    mlflow_options = {MLFlowLiterals.LOADER: SystemSettings.NAMESPACE}
    strs_to_save = {RUN_ID_OUTPUT_PATH: run.id}
    python_version = platform.python_version()
    inference_deps = CondaDependencies.create(conda_packages=inference.AutoMLNLPCondaPackagesList,
                                              python_version=python_version,
                                              pip_packages=inference.AutoMLNLPPipPackagesList,
                                              pin_sdk_version=True)
    strs_to_save[INFERENCE_DEPENDENCIES] = inference_deps
    models_to_save = {model_path: model}
    if has_mlflow and input_sample_str is not None and output_sample_str is not None:
        input_sample = eval(input_sample_str)       # type: Optional[pd.DataFrame, np.ndarray]
        output_sample = eval(output_sample_str)     # type: Optional[np.ndarray]
        signature = mlflow.models.signature.infer_signature(input_sample, output_sample)
        mlflow_options[MLFlowLiterals.SCHEMA_SIGNATURE] = signature
        mlflow_options[MLFlowLiterals.INPUT_EXAMPLE] = input_sample
    # metadata to be dumped to mlflow MLmodel file
    metadata = {
        MLFlowMetaLiterals.BASE_MODEL_NAME: model.training_configuration[TrainingInputLiterals.MODEL_NAME],
        MLFlowMetaLiterals.FINETUNING_TASK: model.training_configuration[LoggingLiterals.TASK_TYPE],
        MLFlowMetaLiterals.IS_AUTOML_MODEL: True,
        MLFlowMetaLiterals.TRAINING_RUN_ID: run.id
    }
    run_ctx.batch_save_artifacts(os.getcwd(),
                                 input_strs=strs_to_save,
                                 model_outputs=models_to_save,
                                 save_as_mlflow=save_mlflow,
                                 mlflow_options=mlflow_options,
                                 metadata=metadata)
    return model_path
