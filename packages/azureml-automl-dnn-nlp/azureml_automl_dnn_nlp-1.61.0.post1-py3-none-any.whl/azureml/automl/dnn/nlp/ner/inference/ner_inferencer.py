# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Scoring functions that can load a serialized model and generate predictions."""
import logging
import os
from typing import Optional, Union

import torch

from azureml.automl.dnn.nlp.common._data_utils import download_file_dataset, get_dataset
from azureml.automl.dnn.nlp.common._utils import is_data_labeling_run
from azureml.automl.dnn.nlp.common.constants import DataLiterals, OutputLiterals, Split, Warnings
from azureml.automl.dnn.nlp.common.io.utils import load_model_wrapper
from azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper import (
    load_dataset_for_labeling_service, generate_results_for_labeling_service
)
from azureml.core.run import Run

_logger = logging.getLogger(__name__)


class NerInferencer:
    """Class to perform inferencing on an unlabeled dataset using training run artifacts."""

    def __init__(self,
                 run: Run,
                 device: Union[str, torch.device]) -> None:
        """
        Function to initialize the inferencing object.

        :param run: the run object.
        :param device: device to be used for inferencing.
        """
        self.training_run = run
        self.device = device

        if self.device == "cpu":
            _logger.warning(Warnings.CPU_DEVICE_WARNING)

        self.workspace = self.training_run.experiment.workspace

    def score(self,
              input_dataset_id: Optional[str] = None,
              input_mltable_uri: Optional[str] = None) -> None:
        """
        Generate predictions from input files.

        :param input_dataset_id: the input dataset id.
        :param input_mltable_uri: the input mltable uri.
        :return: None.
        """
        model_wrapper = load_model_wrapper(self.training_run)

        is_labeling_run = is_data_labeling_run(self.training_run)
        test_dataset = get_dataset(self.workspace,
                                   Split.test,
                                   dataset_id=input_dataset_id,
                                   mltable_uri=input_mltable_uri)
        if is_labeling_run:
            test_file, labeling_input_file_paths = load_dataset_for_labeling_service(
                test_dataset,
                DataLiterals.NER_DATA_DIR,
                DataLiterals.TEST_TEXT_FILENAME,
                Split.test
            )
        else:
            test_file = download_file_dataset(test_dataset, Split.test, DataLiterals.NER_DATA_DIR)

        test_file_path = os.path.join(DataLiterals.NER_DATA_DIR, test_file)
        with open(test_file_path, encoding=DataLiterals.ENCODING, errors=DataLiterals.ERRORS) as f:
            test_data = f.read()

        prediction_string = model_wrapper.predict_proba(test_data)

        predictions_file_path = os.path.join(OutputLiterals.OUTPUT_DIR, OutputLiterals.PREDICTIONS_TXT_FILE_NAME)
        with open(predictions_file_path, "w") as dst:
            dst.write(prediction_string)

        if is_labeling_run:
            # For labeling service, extra conversion is needed to output
            generate_results_for_labeling_service(
                predictions_file_path, labeling_input_file_paths, DataLiterals.NER_DATA_DIR
            )
        return
