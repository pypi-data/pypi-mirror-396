# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Error Definitions for the package."""

from azureml._common._error_definition.user_error import ArgumentInvalid, BadData, InvalidData
from azureml.automl.core.shared._diagnostics.automl_error_definitions import AutoMLInternal, ExecutionFailure
from azureml.automl.core.shared._diagnostics.error_strings import AutoMLErrorStrings


# region ArgumentInvalid
class ArgumentParsingError(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_ARGUMENT_PARSING_ERROR


class InvalidSweepArgument(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_INVALID_SWEEP_ARGUMENT


class MalformedNerInferenceInput(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_MALFORMED_NER_INFERENCE_INPUT
# endregion


# region BadData
class ColumnOrderingMismatch(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_COLUMN_ORDERING_MISMATCH


class ColumnTypeMismatch(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_COLUMN_TYPE_MISMATCH


class ColumnSetMismatch(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_COLUMN_SET_MISMATCH


class ConsecutiveBlankNERLines(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_CONSECUTIVE_BLANK_LINES


class DuplicateColumnNames(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_DUPLICATE_COLUMN_NAMES


class DuplicateLabelTypeMismatch(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_DUPLICATE_LABEL_TYPE_MISMATCH


class EmptyFileBeginning(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_EMPTY_NER_FILE_BEGINNING


class EmptyFileEnding(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_EMPTY_NER_FILE_ENDING


class IncorrectClassificationDatasetType(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_INCORRECT_CLASSIFICATION_DATASET


class InsufficientClassificationExamples(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_CLASSIFICATION_INSUFFICIENT_EXAMPLES


class InsufficientNERExamples(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_NER_INSUFFICIENT_EXAMPLES


class InsufficientNumberOfColumns(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_CLASSIFICATION_INSUFFICIENT_COLUMNS


class InsufficientUniqueLabels(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_INSUFFICIENT_UNIQUE_LABELS


class LabelingDataConversionFailed(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_LABELING_DATA_CONVERSION_FAILED


class MalformedLabelColumn(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_MALFORMED_LABEL_COLUMN


class MalformedNERLine(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_MALFORMED_NER_LINE


class MissingDataset(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_MISSING_DATASET


class MissingLabelColumn(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_MISSING_LABEL_COLUMN


class MixedMulticlassTypes(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_MIXED_MULTICLASS_TYPES


class MixedMultilabelTypes(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_MIXED_MULTILABEL_TYPES


class NerInferenceTypeMismatch(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_NER_INFERENCE_TYPE_MISMATCH


class UnexpectedLabelFormat(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_UNEXPECTED_LABEL_FORMAT
# endregion


# region ClientError
class AutoNLPInternal(AutoMLInternal):
    """Top level unknown system error."""
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.AUTOML_NLP_INTERNAL
# endregion


# region UserError
class DetectedVnetIssue(ExecutionFailure):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_NETWORK_VNET_MISCONFIG
# endregion


# region InvalidData
class LabelingDataDownloadFailed(InvalidData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_LABELING_DATA_DOWNLOAD_FAILED


class UnexpectedNERDataFormat(InvalidData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_INVALID_NER_DATASET
# endregion
