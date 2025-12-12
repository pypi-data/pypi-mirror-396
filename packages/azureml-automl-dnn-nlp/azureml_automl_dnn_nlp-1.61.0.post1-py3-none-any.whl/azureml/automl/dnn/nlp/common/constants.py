# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Constants for the package."""

from enum import Enum


class SystemSettings:
    """System settings."""
    DEEP_SPEED_CONFIG = "ds_config.json"
    NAMESPACE = "azureml.automl.dnn.nlp"
    LABELING_RUNSOURCE = "Labeling"
    LABELING_DATASET_TYPE = "labeling_dataset_type"
    LABELING_DATASET_TYPE_FILEDATSET = "FileDataset"
    LOG_FILENAME = "azureml_automl_nlp.log"
    LOG_FOLDER = "logs"


class OutputLiterals:
    """Directory and file names for artifacts."""
    PT_MODEL_BIN_FILE_NAME = "pytorch_model.bin"
    MODEL_FILE_NAME = "model.pkl"
    VECTORIZER_FILE_NAME = "vectorizer.pkl"
    CHECKPOINT_FILE_NAME = "checkpoint"
    TOKENIZER_FILE_NAME = "tokenizer_config.json"
    CONFIG_FILE_NAME = "config.json"
    OUTPUT_DIR = "outputs"
    SCORE_SCRIPT = "score_script.py"
    TRAINING_ARGS = "training_args.bin"
    LABELS_FILE = "labels.txt"
    LABEL_LIST_FILE_NAME = "label_list.npy"
    PREDICTIONS_TXT_FILE_NAME = "predictions.txt"
    PREDICTIONS_CSV_FILE_NAME = "predictions.csv"
    ARTIFACT_TYPE_CONFIG = "CONFIG"
    ARTIFACT_TYPE_LABELS = "LABELS"
    ARTIFACT_TYPE_MODEL = "MODEL"
    ARTIFACT_TYPE_TOKENIZER = "TOKENIZER"
    ARTIFACT_TYPE_TRAINING_ARGS = "TRAINING_ARGS"


class DataLiterals:
    """Directory and file names for artifacts."""
    DATASET_ID = "dataset_id"
    VALIDATION_DATASET_ID = "validation_dataset_id"
    DATA_DIR = "data"
    NER_DATA_DIR = "ner_data"
    TRAIN_TEXT_FILENAME = "train.txt"
    VALIDATION_TEXT_FILENAME = "validation.txt"
    TEST_TEXT_FILENAME = "test.txt"
    DATASTORE_PREFIX = "AmlDatastore://"
    NER_IGNORE_TOKENS_REGEX = r"\s*"
    NER_LINE_FORMAT = r"^\s*(\S+)\s+((B-|I-)\S(\S| )*?|O)\s*$"
    NER_UNLABELED_LINE_FORMAT = r"^\s*(\S+)\s*"
    LABEL_COLUMN = "label"
    LABEL_CONFIDENCE = "label_confidence"
    TEXT_COLUMN = "text"
    ENCODING = 'utf-8'
    ERRORS = "replace"


class ScoringLiterals:
    """String names for scoring settings"""
    RUN_ID = "run_id"
    EXPERIMENT_NAME = "experiment_name"
    OUTPUT_FILE = "output_file"
    ROOT_DIR = "root_dir"
    BATCH_SIZE = "batch_size"
    INPUT_DATASET_ID = "input_dataset_id"
    INPUT_MLTABLE_URI = "input_mltable_uri"
    LABEL_COLUMN_NAME = "label_column_name"
    LOG_OUTPUT_FILE_INFO = "log_output_file_info"
    ENABLE_DATAPOINT_ID_OUTPUT = "enable_datapoint_id_output"
    AZUREML_MODEL_DIR_ENV = "AZUREML_MODEL_DIR"
    MULTICLASS_SCORE_FILE = "score_nlp_multiclass_v2.txt"
    MULTILABEL_SCORE_FILE = "score_nlp_multilabel_v2.txt"
    NER_SCORE_FILE = "score_nlp_ner_v2.txt"


class LoggingLiterals:
    """Literals that help logging and correlating different training runs."""
    PROJECT_ID = "project_id"
    VERSION_NUMBER = "version_number"
    TASK_TYPE = "task_type"
    EVAL_PREFIX = "eval_"
    TEST_PREFIX = "test_"
    MODEL_RETRIEVAL = "Model_Retrieval"


class Warnings:
    """Warning strings."""
    CPU_DEVICE_WARNING = "The device being used for training is 'cpu'. Training can be slow and may lead to " \
                         "out of memory errors. Please switch to a compute with gpu devices. " \
                         "If you are already running on a compute with gpu devices, please check to make sure " \
                         "your nvidia drivers are compatible with torch version {}."


class Split(Enum):
    """Split Enum Class."""
    train = "train"
    valid = "valid"
    test = "test"


class TaskNames:
    """Names for NLP DNN tasks"""
    MULTILABEL = "multilabel"
    MULTICLASS = "multiclass"


class ModelNames:
    """Model names."""
    BERT_BASE_UNCASED = "bert-base-uncased"
    BERT_BASE_CASED = "bert-base-cased"
    BERT_BASE_MULTILINGUAL_CASED = "bert-base-multilingual-cased"
    BERT_BASE_GERMAN_CASED = "bert-base-german-cased"
    BERT_LARGE_CASED = "bert-large-cased"
    BERT_LARGE_UNCASED = "bert-large-uncased"
    DISTILBERT_BASE_CASED = "distilbert-base-cased"
    DISTILBERT_BASE_UNCASED = "distilbert-base-uncased"

    ROBERTA_BASE = "roberta-base"
    ROBERTA_LARGE = "roberta-large"
    DISTILROBERTA_BASE = "distilroberta-base"
    XLM_ROBERTA_BASE = "xlm-roberta-base"
    XLM_ROBERTA_LARGE = "xlm-roberta-large"

    XLNET_BASE_CASED = "xlnet-base-cased"
    XLNET_LARGE_CASED = "xlnet-large-cased"

    SUPPORTED_MODELS = {BERT_BASE_CASED, BERT_BASE_UNCASED, BERT_BASE_MULTILINGUAL_CASED, BERT_BASE_GERMAN_CASED,
                        BERT_LARGE_CASED, BERT_LARGE_UNCASED, DISTILBERT_BASE_CASED, DISTILBERT_BASE_UNCASED,
                        ROBERTA_BASE, ROBERTA_LARGE, DISTILROBERTA_BASE, XLM_ROBERTA_BASE, XLM_ROBERTA_LARGE,
                        XLNET_BASE_CASED, XLNET_LARGE_CASED}


class DataLabelingLiterals:
    """Constants for Data Labeling specific records"""
    ARGUMENTS = "arguments"
    DATASTORENAME = "datastoreName"
    IMAGE_URL = "image_url"
    IMAGE_COLUMN_PROPERTY = '_Image_Column:Image_'
    LABEL_COLUMN_PROPERTY = '_Label_Column:Label_'
    RESOURCE_IDENTIFIER = "resource_identifier"
    PORTABLE_PATH_COLUMN_NAME = 'PortablePath'


class ValidationLiterals:
    """All constants related to data validation."""
    DATA_EXCEPTION_TARGET = "AutoNLP Data Validation"
    DATA_PREPARATION_DOC_LINK = \
        "https://docs.microsoft.com/en-us/azure/machine-learning/how-to-auto-train-nlp-models#preparing-data"
    NER_FORMAT_DOC_LINK = "https://docs.microsoft.com/en-us/azure/machine-learning/" \
                          "how-to-auto-train-nlp-models#named-entity-recognition-ner"
    VNET_CONFIG_LINK = "https://learn.microsoft.com/en-us/azure/machine-learning/" \
                       "how-to-troubleshoot-auto-ml#vnet-firewall-setting-download-failure"
    MIN_LABEL_CLASSES = 2
    MIN_TRAINING_SAMPLE = 50
    MIN_VALIDATION_SAMPLE = 1


class TrainingInputLiterals:
    """Training setting names."""
    # Related to logging.
    LOGGING_STRATEGY = "logging_strategy"
    REPORT_TO = "report_to"
    SAVE_STRATEGY = "save_strategy"
    EVAL_STRATEGY = "eval_strategy"

    # For model selection
    MODEL = "model"
    MODEL_NAME = "model_name"
    MODEL_NAME_OR_PATH = "model_name_or_path"

    # For config
    USE_MEMS_EVAL = "use_mems_eval"

    # For tokenizer
    TOKENIZER_NAME_OR_PATH = "tokenizer_name_or_path"
    FINETUNING_TASK = "finetuning_task"
    LONG_RANGE_LENGTH = "long_range_length"
    LONG_RANGE_THRESHOLD = "long_range_threshold"
    USE_SEQ_LEN_MULTIPLIER = "use_seq_len_multiplier"
    MAX_SEQ_LENGTH = "max_seq_length"
    PADDING_STRATEGY = "padding_strategy"
    ADD_PREFIX_SPACE = "add_prefix_space"

    # Hyperparameter names
    TRAIN_BATCH_SIZE = "training_batch_size"
    VALID_BATCH_SIZE = "validation_batch_size"
    NUM_TRAIN_EPOCHS = "number_of_epochs"
    GRADIENT_ACCUMULATION_STEPS = "gradient_accumulation_steps"
    LEARNING_RATE = "learning_rate"
    WEIGHT_DECAY = "weight_decay"
    WARMUP_RATIO = "warmup_ratio"
    LR_SCHEDULER_TYPE = "learning_rate_scheduler"

    SUPPORTED_PUBLIC_SETTINGS = {MODEL, MODEL_NAME, TRAIN_BATCH_SIZE, VALID_BATCH_SIZE, GRADIENT_ACCUMULATION_STEPS,
                                 NUM_TRAIN_EPOCHS, LEARNING_RATE, WEIGHT_DECAY, WARMUP_RATIO, LR_SCHEDULER_TYPE}

    # Ignored arguments
    DATA_FOLDER = "data-folder"
    LABELS_FILE_ROOT = "labels-file-root"
    IGNORED_ARGUMENT = "ignored_argument"
    IGNORED_ARGUMENTS = {"data_folder", "labels_file_root", "ignored_argument"}


class TrainingDefaultSettings:
    """Default values for different training settings."""
    NO_REPORTING = "none"
    MAX_LENGTH = "max_length"
    NER = "ner"

    # Sequence length defaults
    DEFAULT_SEQ_LEN = 128
    LONG_RANGE_MAX = 256
    MIN_PROPORTION_LONG_RANGE = 0.1

    # Intermediary eval defaults
    MIN_EVAL_STEPS = 2000
    FRACTIONAL_EVAL_INTERVAL = 0.1


class SuppressedWarningPrefixes:
    """Prefixes for warnings we should suppress."""
    UNKNOWN_PARAM = "Received unrecognized parameter"
    ALL = [UNKNOWN_PARAM]
