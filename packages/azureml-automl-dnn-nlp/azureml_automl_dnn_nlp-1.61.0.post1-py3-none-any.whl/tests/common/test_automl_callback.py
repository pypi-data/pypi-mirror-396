from unittest.mock import Mock, patch
from transformers import TrainingArguments

import os
import unittest

from azureml.automl.dnn.nlp.common.automl_callback import AutoMLCallback


class TestAutoMLCallback(unittest.TestCase):
    def _check_callback_logs(self, prefix, logs):
        callback = AutoMLCallback()
        callback.azureml_run = True
        prefixed_logs = {prefix + key: val for key, val in logs.items()}
        with patch("azureml.automl.dnn.nlp.common.automl_callback.AzureMLCallback.on_log") as mock_azure_log:
            callback.on_log(args=TrainingArguments(output_dir=os.getcwd()),
                            state=Mock(is_world_process_zero=True),
                            control=None,
                            logs=prefixed_logs)
        self.assertEqual(logs, mock_azure_log.call_args[0][3])

    def test_on_log_strips_eval_prefixes(self):
        logs = {"accuracy": 0.97,
                "AUC_weighted": 0.99,
                "train_duration": 712}
        self._check_callback_logs("eval_", logs)

    def test_on_log_strips_test_prefixes(self):
        logs = {"accuracy": 0.97,
                "AUC_weighted": 0.99,
                "train_duration": 712}
        self._check_callback_logs("test_", logs)
