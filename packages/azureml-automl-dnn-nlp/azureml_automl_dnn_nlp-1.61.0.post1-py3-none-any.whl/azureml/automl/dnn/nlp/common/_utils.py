# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Common utilities across tasks."""
from typing import Any, Callable, Dict, List, Optional, Union, TYPE_CHECKING
from functools import wraps

import json
import logging
import math
import os
import pickle
import sys
import uuid
import torch
import pandas as pd

from azureml._common._error_definition import AzureMLError, UserError
from azureml._common.exceptions import AzureMLException
from azureml.automl.core.inference import inference
from azureml.automl.core.shared import log_server
from azureml.automl.core.shared.constants import CONDA_ENV_FILE_PATH, SCORING_FILE_PATH
from azureml.automl.core.shared.exceptions import ClientException, UserException
from azureml.automl.core.shared.logging_fields import TELEMETRY_AUTOML_COMPONENT_KEY
from azureml.automl.core.shared.logging_utilities import _CustomStackSummary, _get_pii_free_message
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import AutoNLPInternal, DetectedVnetIssue
from azureml.automl.dnn.nlp.common.constants import LoggingLiterals, \
    OutputLiterals, TrainingDefaultSettings, TrainingInputLiterals, SystemSettings, ValidationLiterals
from azureml.automl.runtime import data_transformation, network_compute_utils
from azureml.core.experiment import Experiment
from azureml.core.run import Run, _OfflineRun
from azureml.telemetry import INSTRUMENTATION_KEY, get_diagnostics_collection_info
from azureml.train.automl._logging import set_run_custom_dimensions
from azureml.train.automl.constants import ComputeTargets, Tasks
from azureml.train.automl.runtime._azureautomlruncontext import AzureAutoMLRunContext

from transformers import TrainingArguments

if TYPE_CHECKING:
    from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration
    from ._types import MODEL_WRAPPER_TYPE  # noqa: F401

logger = logging.getLogger(__name__)


class Singleton(type):
    """Singleton metaclass."""
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.__instance = None

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.__instance


class AzureAutoMLSettingsStub:
    """Stub for AzureAutoMLSettings class to configure logging."""
    is_timeseries = False
    task_type = None
    compute_target = None
    name = None
    subscription_id = None
    region = None
    verbosity = None
    telemetry_verbosity = None
    send_telemetry = None
    azure_service = None


class RootLoggingFilter:
    """Small utility class for suppressing unwanted warnings to the root logger in-context."""
    def __init__(self, prefixes_to_suppress):
        self.logger = logging.getLogger()
        self.filter = lambda record: not any([record.msg.startswith(prefix) for prefix in prefixes_to_suppress])

    def __enter__(self):
        self.logger.addFilter(self.filter)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.removeFilter(self.filter)


def create_unique_dir(name: str) -> str:
    """
    Creates a directory with a unique id attached.
    :param name: name of the unique dir. The final name will be of format name_{some unique id}
    """
    unique_id = uuid.uuid1().fields[0]
    dir_name = "{}_{}".format(name, unique_id)
    os.makedirs(dir_name, exist_ok=True)
    return dir_name


def set_logging_parameters(task_type: Tasks,
                           settings: Dict,
                           output_dir: Optional[str] = None,
                           azureml_run: Optional[Run] = None):
    """Sets the logging parameters so that we can track all the training runs from
    a given project.

    :param task_type: The task type for the run.
    :type task_type: Tasks
    :param settings: All the settings for this run.
    :type settings: Dict
    :param output_dir: The output directory.
    :type Optional[str]
    :param azureml_run: The run object.
    :type Optional[Run]
    """
    log_server.update_custom_dimensions({LoggingLiterals.TASK_TYPE: task_type})

    if LoggingLiterals.PROJECT_ID in settings:
        project_id = settings[LoggingLiterals.PROJECT_ID]
        log_server.update_custom_dimensions({LoggingLiterals.PROJECT_ID: project_id})

    if LoggingLiterals.VERSION_NUMBER in settings:
        version_number = settings[LoggingLiterals.VERSION_NUMBER]
        log_server.update_custom_dimensions({LoggingLiterals.VERSION_NUMBER: version_number})

    _set_automl_run_custom_dimensions(task_type, output_dir, azureml_run)


def prepare_run_properties(run: Run,
                           model_name: str):
    """
    Add the run properties needed to display the run in UI

    :param run: Run object to add properties to
    :param model_name: Model being trained on this run
    """
    properties_to_add = {
        "runTemplate": "automl_child",
        "run_algorithm": model_name
    }
    run.add_properties(properties_to_add)


def prepare_post_run_properties(run: Run,
                                model_file: str,
                                model_size: int,
                                environment_file: str,
                                deploy_file: str,
                                primary_metric: str,
                                score: float):
    """Save model and weights to artifacts, conda environment yml,
       and save run properties needed for model export

    :param run: The current azureml run object
    :type run: azureml.core.Run
    :param model_file: The pytorch model saved after training
    :type model_file: str
    :type model_size: int
    :param model_size: size of the model in bytes
    :param environment_file: The environment file that can be used in inferencing environments
    :type environment_file: str
    :param deploy_file: Score script used in deployment
    :type deploy_file: str
    :param primary_metric: The primary metric used for the task
    :type primary_metric: str
    :param score: The score of the primary metric used for the task
    :type score: float
    """
    automl_run_context = AzureAutoMLRunContext(run)
    run_id = automl_run_context.run_id
    artifact_id = "aml://artifact/ExperimentRun/dcid.{}/".format(run_id)

    # Get model artifacts file paths
    conda_env_data_loc = os.path.join(artifact_id, environment_file)
    scoring_data_loc = os.path.join(artifact_id, deploy_file)
    model_artifacts_file = os.path.join(artifact_id, model_file)
    model_id = inference._get_model_name(run_id)

    # Add paths to run properties for model deployment
    properties_to_add = {
        inference.AutoMLInferenceArtifactIDs.ScoringDataLocation: scoring_data_loc,
        inference.AutoMLInferenceArtifactIDs.ScoringDataLocationV2: scoring_data_loc,
        inference.AutoMLInferenceArtifactIDs.CondaEnvDataLocation: conda_env_data_loc,
        inference.AutoMLInferenceArtifactIDs.ModelDataLocation: model_artifacts_file,
        inference.AutoMLInferenceArtifactIDs.ModelName: model_id,
        inference.AutoMLInferenceArtifactIDs.ModelSizeOnDisk: model_size,
        "score": score,
        "primary_metric": primary_metric
    }
    run.add_properties(properties_to_add)


def _set_automl_run_custom_dimensions(task_type: Tasks,
                                      output_dir: Optional[str] = None,
                                      azureml_run: Optional[Run] = None):
    if output_dir is None:
        output_dir = SystemSettings.LOG_FOLDER
    os.makedirs(output_dir, exist_ok=True)

    if azureml_run is None:
        azureml_run = Run.get_context()

    name = "not_available_offline"
    subscription_id = "not_available_offline"
    region = "not_available_offline"
    parent_run_id = "not_available_offline"
    child_run_id = "not_available_offline"
    if not isinstance(azureml_run, _OfflineRun):
        # If needed in the future, we can replace with a uuid5 based off the experiment name
        # name = azureml_run.experiment.name
        name = "online_scrubbed_for_compliance"
        subscription_id = azureml_run.experiment.workspace.subscription_id
        region = azureml_run.experiment.workspace.location
        parent_run_id = azureml_run.parent.id if azureml_run.parent is not None else None
        child_run_id = azureml_run.id

    # Build the automl settings expected by the logger
    send_telemetry, level = get_diagnostics_collection_info(component_name=TELEMETRY_AUTOML_COMPONENT_KEY)
    automl_settings = AzureAutoMLSettingsStub
    automl_settings.is_timeseries = False
    automl_settings.task_type = task_type
    automl_settings.compute_target = ComputeTargets.AMLCOMPUTE
    automl_settings.name = name
    automl_settings.subscription_id = subscription_id
    automl_settings.region = region
    automl_settings.telemetry_verbosity = level
    automl_settings.send_telemetry = send_telemetry

    log_server.set_log_file(os.path.join(output_dir, SystemSettings.LOG_FILENAME))
    if send_telemetry:
        log_server.enable_telemetry(INSTRUMENTATION_KEY)
    log_server.set_verbosity(level)

    set_run_custom_dimensions(
        automl_settings=automl_settings,
        parent_run_id=parent_run_id,
        child_run_id=child_run_id)

    # Add console handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    log_server.add_handler('stdout', stdout_handler)


def _get_language_code(featurization: Union[str, Dict]) -> str:
    """Return user language code if provided, else return 'eng'

    :param featurization: FeaturizationConfig of run
    :return 3 letter language code
    """
    if isinstance(featurization, dict) and featurization.get("_dataset_language", "eng") is not None:
        return featurization.get("_dataset_language", "eng")
    else:
        return "eng"


def get_run_by_id(run_id: str, experiment_name: Optional[str] = None):
    """Get a Run object.

    :param run_id: run id of the run that produced the model
    :param experiment_name: name of experiment that contained the run id
    :return: Run object
    :rtype: Run
    """
    experiment = Run.get_context().experiment
    if experiment_name is not None:
        workspace = experiment.workspace
        experiment = Experiment(workspace, experiment_name)
    return Run(experiment=experiment, run_id=run_id)


def save_script(script, score_script_dir=None):
    """Save a script file to outputs directory.

    :param script: The script to be saved
    :param score_script_dir: Path to save location
    :type score_script_dir: string
    """
    if score_script_dir is None:
        score_script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(score_script_dir, script)) as source_file:
        save_location = os.path.join(OutputLiterals.OUTPUT_DIR, script)
        with open(save_location, "w") as output_file:
            output_file.write(source_file.read())
    return save_location


def save_conda_yml() -> str:
    """Save environment YAML file to outputs directory.

    :return: The conda YAML file name.
    """
    conda_deps_str = inference._create_conda_env_file(
        pip_packages_list_override=inference.AutoMLNLPPipPackagesList,
        conda_packages_list_override=inference.AutoMLNLPCondaPackagesList
    )
    conda_file_path = CONDA_ENV_FILE_PATH
    with open(conda_file_path, "w") as output_file:
        output_file.write(conda_deps_str)

    return conda_file_path


def is_main_process():
    """
    Function for determining whether the current process is master.
    :return: Boolean for whether this process is master.
    """
    return os.environ.get('AZUREML_PROCESS_NAME', 'main') in {'main', 'rank_0'}


def get_grand_parent_properties(current_run: Run):
    """
    Function for returns the properties set at grand parent level if found.
    :param current_run: current run context
    :return: properties of grand parent or empty dict.
    """
    gp_properties = {}
    if current_run and current_run.parent and current_run.parent.parent and current_run.parent.parent.properties:
        gp_properties = current_run.parent.parent.properties
    return gp_properties


def is_data_labeling_run(current_run: Run):
    """
    Check whether the run is for labeling service.

    If the run is submitted through data labeling service, the runsource will be marked as "Labeling"
    :param current_run: current run context
    :return: whether run is from data labeling
    """
    # current run id: AutoML_<guid>_HD_0
    # parent HD run id: run.parent AutoML_<guid>_HD
    # original parent AutoML run: run.parent.parent AutoML_<guid>
    run_source = get_grand_parent_properties(current_run).get(Run._RUNSOURCE_PROPERTY, None)
    return run_source == SystemSettings.LABELING_RUNSOURCE


def is_data_labeling_run_with_file_dataset(current_run: Run):
    """
    Check whether the run is for labeling service.

    If the run is from labeling service and input is from file dataset, it needs extra input data conversion.
    :param current_run: current run context
    :return: whether run is from data labeling
    """
    # current run id: AutoML_<guid>_HD_0
    # parent HD run id: run.parent AutoML_<guid>_HD
    # original parent AutoML run: run.parent.parent AutoML_<guid>
    data_type = None
    is_labeling_run = is_data_labeling_run(current_run)
    if is_labeling_run:
        automl_settings = get_grand_parent_properties(current_run).get("AMLSettingsJsonString", None)
        if automl_settings:
            data_type = json.loads(automl_settings).get(SystemSettings.LABELING_DATASET_TYPE, None)

    return is_labeling_run and data_type == SystemSettings.LABELING_DATASET_TYPE_FILEDATSET


def _load_pyfunc(model_path: str) -> "MODEL_WRAPPER_TYPE":
    """
    Function used by MLflow to load Azure AutoNLP models via the pyfunc/custom model flavor.
    Note the serialization will be manually done by us; this function is to tell MLflow how
    to deserialize it into an object that follows the MLflow interface, which our AutoNLP
    ModelWrappers adhere to already.

    :param model_path: The path to the MLflow model directory.
    :return: An AutoNLP model wrapper, specific to the task type.
    """
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model


def make_arg(arg_name: str) -> str:
    return "--{}".format(arg_name)


def get_default_device():
    return torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def save_deploy_script(script_name: str,
                       input_sample_str: str,
                       output_sample_str: str,
                       inference_data_type: Optional[str] = inference.PandasParameterType,
                       save_location: str = SCORING_FILE_PATH) -> str:
    """
    Save the deployment script for inferencing

    :param script_name: name of the scoring file
    :param input_sample_str: schema for input data
    :param output_sample_str: schema for output data
    :param inference_data_type: type of input data
    :param save_location: path for saving the deploy script
    :return: The path of the saved scoring file.
    """
    file_content = inference._format_scoring_file(script_name,
                                                  inference_data_type,
                                                  input_sample_str,
                                                  output_sample_str)
    with open(save_location, "w") as output_file:
        output_file.write(file_content)
    return save_location


def _get_input_example_dictionary(training_df: pd.DataFrame,
                                  label_column: str):
    """
    Function to create an input example using pandas dataframe.
    This can be used as example schema for deployment
    :param training_df: Input pandas dataframe
    :param label_column: The label column which should be ignored for inferencing
    """
    data_example = data_transformation._get_data_snapshot(
        data=training_df.head(0).drop(columns=label_column)
    )
    return data_example


def _get_output_example(training_df: pd.DataFrame,
                        label_column: str):
    """
    Function to create an output example using label column and pandas dataframe.
    This can be used as example schema for deployment
    :param training_df: Input pandas dataframe
    :param label_column: the label column which should be output for inferencing
    """
    output_example = data_transformation._get_output_snapshot(
        y=training_df.head(1)[label_column].values
    )
    return output_example


def is_known_user_error(e: Exception) -> bool:
    """
    Determine whether the provided exception is a UserError derivative or not.

    :param e: the exception to analyze.
    :return: boolean for is user error.
    """
    return isinstance(e, AzureMLException) and e._azureml_error is not None and \
        isinstance(e._azureml_error.error_definition, UserError)


def scrub_system_exception(e: Exception) -> ClientException:
    """
    Handle missing logs scenario by scrubbing exception of PII and explicitly including the traceback and
    error details in the message before logging it to jasmine.

    :param e: The raw exception.
    :return: The scrubbed exception.
    """
    scrubbed_exception = e
    if not is_known_user_error(e):
        # Scrub all unknown, non-user errors.
        error_message_without_pii = _get_pii_free_message(e)
        traceback_obj = e.__traceback__ if hasattr(e, "__traceback__") else None or sys.exc_info()[2]
        traceback_msg_without_pii = _CustomStackSummary.get_traceback_message(traceback_obj)
        scrubbed_exception = ClientException._with_error(
            AzureMLError.create(AutoNLPInternal,
                                error_details=str(e),
                                traceback=traceback_msg_without_pii,
                                pii_safe_message=error_message_without_pii)
        ).with_traceback(traceback_obj)
    return scrubbed_exception


def concat_text_columns(row: pd.Series, df_columns: pd.Index, label_column_name: Optional[str]) -> str:
    """
    Concatenate all text columns present in a single training example.

    :param row: One row from the dataframe represented as a column-like series with column names now as indices.
    :param df_columns: Collection of columns present in the dataset.
    :param label_column_name: Name of the label column.
    :return: concatenated text data from a row of the dataframe.
    """
    cols_to_exclude = [label_column_name] if label_column_name is not None\
        and label_column_name in df_columns else []
    return row.drop(index=cols_to_exclude).astype(str).str.cat(sep=". ")


def get_unique_download_path(download_file: str) -> str:
    """
    Create paths unique to node

    :param download_file: the download path we want to make unique
    :return: String for path appended with current rank
    """

    rank = os.environ.get("AZUREML_PROCESS_NAME", "main")
    path = os.path.join(rank, download_file)
    return path


def calc_inter_eval_freq(num_examples: int, training_configuration: "TrainingConfiguration") -> int:
    """
    Calculate the frequency (in steps) with which we should perform intermediary evaluation.

    :param num_examples: the number of examples in the training dataset.
    :param training_configuration: a collection of parameters to dictate the training procedure.
    :return: the intermediary evaluation frequency
    """
    num_batches = math.ceil(num_examples / float(training_configuration[TrainingInputLiterals.TRAIN_BATCH_SIZE]))
    num_update_steps_per_epoch = \
        max(num_batches // training_configuration[TrainingInputLiterals.GRADIENT_ACCUMULATION_STEPS], 1)
    total_training_steps = num_update_steps_per_epoch * training_configuration[TrainingInputLiterals.NUM_TRAIN_EPOCHS]

    # The above formula technically doesn't account for distributed scenarios where the number of steps scales
    # inversely with the degree of distribution, but that's okay -- let's err on the side of infrequency rather
    # than frequency for this. Evaluation can take a while.
    return int(max(TrainingDefaultSettings.MIN_EVAL_STEPS, total_training_steps
                   * TrainingDefaultSettings.FRACTIONAL_EVAL_INTERVAL))


def intercept_vnet_failures(extra_errors: Optional[List[Any]] = None) -> Callable[..., Any]:
    """
    Decorator for intercepting any network connection failures due to
    improper vnet configuration and raising informative UserErrors instead.

    :param extra_errors: extra errors which are not general (like ConnectionError) that in the context of this
    particular application mean a network issue arose. An example would be the Downloader's ClientException.
    (ClientException => network problem does not generalize to the rest of the code.)
    :return: the wrapped function.
    """
    def inner_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Inner decorator. Nesting necessary to support above argument.

        :param func: the function to wrap.
        :return: the wrapped function.
        """
        @wraps(func)
        def _wrapped_func(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except (ConnectionError, *(extra_errors or [])):
                cluster_name = network_compute_utils.get_cluster_name()
                vnet_name = network_compute_utils.get_vnet_name(cluster_name)
                if vnet_name:
                    raise UserException._with_error(
                        AzureMLError.create(
                            DetectedVnetIssue,
                            vnet=vnet_name,
                            cluster_name=cluster_name,
                            info_link=ValidationLiterals.VNET_CONFIG_LINK,
                            target=ValidationLiterals.DATA_EXCEPTION_TARGET)
                    )
                else:
                    raise
        return _wrapped_func
    return inner_decorator


def get_trainer_arg(enable_distributed_ort_ds: bool):
    """
    Returns either TrainerArgs from Transformer or ORTTrainer from Optimum
    depending on the value of enable_distributed_ort_ds.

    :param enable_distributed_ort_ds: flag to enable ACPT training
    """
    if enable_distributed_ort_ds:
        try:
            from optimum.onnxruntime import ORTTrainingArguments
            trainer_arg_cls = ORTTrainingArguments
        except ImportError:
            trainer_arg_cls = TrainingArguments
    else:
        trainer_arg_cls = TrainingArguments
    return trainer_arg_cls


def set_env_vars():
    if "MASTER_ADDR" not in os.environ:
        if os.environ.get("AZUREML_CR_DISTRIBUTED_CONFIG"):
            host_addresses = json.loads(os.environ.get("AZUREML_CR_DISTRIBUTED_CONFIG")).get("host_list")
            os.environ["MASTER_ADDR"] = host_addresses[0]
        else:
            os.environ["MASTER_ADDR"] = "127.0.0.1"
