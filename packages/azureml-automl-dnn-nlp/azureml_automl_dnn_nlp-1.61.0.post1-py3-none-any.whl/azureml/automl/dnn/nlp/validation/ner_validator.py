# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Validation logic specific to NER AutoNLP scenario."""
import os
import re

from typing import Optional

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import (
    ConsecutiveBlankNERLines,
    EmptyFileBeginning,
    EmptyFileEnding,
    InsufficientNERExamples,
    MalformedNERLine
)
from azureml.automl.dnn.nlp.common.constants import DataLiterals, ValidationLiterals, Split

from .validators import AbstractNERDataValidator


class NLPNERDataValidator(AbstractNERDataValidator):
    """Validator object specific to NER scenario."""

    def validate(self, dir: str, train_file: str, valid_file: Optional[str] = None) -> None:
        """
        Data validation for NER scenario only.

        :param dir: directory where ner data should be downloaded
        :param train_file: name of downloaded training file.
        :param valid_file: name of downloaded validation file, if present.
        :return: None
        """
        self._check_file_format(dir, train_file, Split.train.value, True)
        if valid_file is not None:
            self._check_file_format(dir, valid_file, Split.valid.value, False)

    def _check_file_format(
            self,
            dir: str,
            file: str,
            split: str,
            check_size: Optional[bool] = False
    ) -> None:
        """
        Validate format of an input NER txt file.

        :param dir: directory containing input file.
        :param file: input file name.
        :param split: the dataset split the file corresponds to, for logging purposes.
        :param check_size: whether to check how many samples are available in the dataset.
        :return: None
        """
        file_path = os.path.join(dir, file)
        with open(file_path, encoding=DataLiterals.ENCODING, errors=DataLiterals.ERRORS) as f:
            line_no = 0
            line, line_no = f.readline(), line_no + 1
            if re.fullmatch(DataLiterals.NER_IGNORE_TOKENS_REGEX, line) is not None:
                raise DataException._with_error(
                    AzureMLError.create(
                        EmptyFileBeginning,
                        target=ValidationLiterals.DATA_EXCEPTION_TARGET
                    )
                )
            if line.startswith('-DOCSTART-'):  # optional beginning of a file, ignored with the following line
                line, line_no = f.readline(), line_no + 1
                line, line_no = f.readline(), line_no + 1

            num_examples = 0
            prev_line = None
            while line:  # not the end of file
                self._check_line_format(line, split, line_no)
                if re.fullmatch(DataLiterals.NER_IGNORE_TOKENS_REGEX, line) is not None:  # empty line
                    if re.fullmatch(DataLiterals.NER_IGNORE_TOKENS_REGEX, prev_line) is not None:
                        raise DataException._with_error(
                            AzureMLError.create(
                                ConsecutiveBlankNERLines,
                                split_type=split.capitalize(),
                                target=ValidationLiterals.DATA_EXCEPTION_TARGET
                            )
                        )
                    num_examples += 1
                prev_line = line
                line, line_no = f.readline(), line_no + 1

            if re.fullmatch(DataLiterals.NER_IGNORE_TOKENS_REGEX, prev_line) is None:
                num_examples += 1
            if re.fullmatch(DataLiterals.NER_IGNORE_TOKENS_REGEX, prev_line) is not None or prev_line[-1] != '\n':
                raise DataException._with_error(
                    AzureMLError.create(
                        EmptyFileEnding,
                        split_type=split,
                        target=ValidationLiterals.DATA_EXCEPTION_TARGET
                    )
                )
            if check_size and num_examples < ValidationLiterals.MIN_TRAINING_SAMPLE:
                raise DataException._with_error(
                    AzureMLError.create(
                        InsufficientNERExamples,
                        exp_cnt=ValidationLiterals.MIN_TRAINING_SAMPLE,
                        act_cnt=num_examples,
                        split_type=split,
                        target=ValidationLiterals.DATA_EXCEPTION_TARGET
                    )
                )

    def _check_line_format(self, line: str, split: str, line_no: int) -> None:
        """
        Check if one line follows the correct format. To be specific:
            1. Check if this line is empty line ('\n') or has exactly one white space
            2. If the line is not empty, check if the label starts with 'B-' or 'I-'

        :param line: string data for this line.
        :param split: the dataset split type, for logging purposes.
        :param line_no: Line number in file
        :return: None
        """

        if re.fullmatch(DataLiterals.NER_IGNORE_TOKENS_REGEX, line) is None:
            match_groups = re.fullmatch(DataLiterals.NER_LINE_FORMAT, line)
            if match_groups is None:
                raise DataException._with_error(
                    AzureMLError.create(
                        MalformedNERLine,
                        split_type=split,
                        info_link=ValidationLiterals.NER_FORMAT_DOC_LINK,
                        target=ValidationLiterals.DATA_EXCEPTION_TARGET,
                        malformed_line=line,
                        line_no=str(line_no)
                    )
                )
