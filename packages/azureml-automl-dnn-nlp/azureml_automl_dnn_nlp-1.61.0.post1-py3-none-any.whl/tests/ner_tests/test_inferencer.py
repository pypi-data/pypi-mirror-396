from unittest.mock import MagicMock, mock_open, patch

import os
import torch
import unittest

from azureml.automl.dnn.nlp.common.constants import SystemSettings
from azureml.automl.dnn.nlp.ner.inference.ner_inferencer import NerInferencer
from ..mocks import MockRun


class TestNerInferencer(unittest.TestCase):
    """Tests for NER scorer."""
    @patch('azureml.automl.dnn.nlp.ner.inference.ner_inferencer.load_model_wrapper')
    @patch('azureml.automl.dnn.nlp.ner.inference.ner_inferencer.download_file_dataset')
    @patch('azureml.automl.dnn.nlp.ner.inference.ner_inferencer.get_dataset')
    def test_score(self, mock_get_dataset, mock_download_file, mock_load_model_wrapper):
        prediction_string = "-DOCSTART-\n\nMicrosoft B-ORG 0.99\nis O 0.99\na O 0.98\ncompany B-TYP 0.97.\n"
        mock_wrapped_model = MagicMock()
        mock_wrapped_model.predict_proba.return_value = prediction_string
        mock_load_model_wrapper.return_value = mock_wrapped_model
        mock_download_file.return_value = "input.txt"

        run = MockRun()
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        inferencer = NerInferencer(run, device)

        file_objects = []
        open_mock = mock_open()

        def tracked_ner_io(*args, **kwargs):
            ret = open_mock(*args, **kwargs)
            file_objects.append(ret)
            return ret

        with patch('builtins.open', new=MagicMock(side_effect=tracked_ner_io)):
            inferencer.score(input_dataset_id="some dataset id")

        # Read from right input file
        self.assertEqual(os.path.join("ner_data", "input.txt"), open_mock.call_args_list[0][0][0])
        # Wrote to right output file
        self.assertEqual(os.path.join("outputs", "predictions.txt"), open_mock.call_args_list[1][0][0])
        self.assertEqual("w", open_mock.call_args_list[1][0][1])
        # Saved prediction content is what we expect
        self.assertEqual(prediction_string, file_objects[1].write.call_args[0][0])

    @patch('azureml.automl.dnn.nlp.ner.inference.ner_inferencer.load_model_wrapper')
    @patch('azureml.automl.dnn.nlp.ner.inference.ner_inferencer.generate_results_for_labeling_service')
    @patch('azureml.automl.dnn.nlp.ner.inference.ner_inferencer.load_dataset_for_labeling_service')
    @patch('azureml.automl.dnn.nlp.ner.inference.ner_inferencer.get_dataset')
    def test_score_labeling(self,
                            mock_get_dataset, mock_load_labeling_data,
                            mock_generate_labeling_results, mock_load_model_wrapper):
        prediction_string = "-DOCSTART-\n\nMicrosoft B-ORG 0.99\nis O 0.99\na O 0.98\ncompany B-TYP 0.97.\n"
        mock_wrapped_model = MagicMock()
        mock_wrapped_model.predict_proba.return_value = prediction_string
        mock_load_model_wrapper.return_value = mock_wrapped_model
        mock_load_labeling_data.return_value = ("input.txt", ["file1", "file2"])

        run = MockRun(run_source=SystemSettings.LABELING_RUNSOURCE,
                      labeling_dataset_type="FileDataset")
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        inferencer = NerInferencer(run, device)

        file_objects = []
        open_mock = mock_open()

        def tracked_ner_io(*args, **kwargs):
            ret = open_mock(*args, **kwargs)
            file_objects.append(ret)
            return ret

        with patch('builtins.open', new=MagicMock(side_effect=tracked_ner_io)):
            inferencer.score(input_dataset_id="some dataset id")

        # Read from right input file
        self.assertEqual(os.path.join("ner_data", "input.txt"), open_mock.call_args_list[0][0][0])
        # Wrote to right output file
        self.assertEqual(os.path.join("outputs", "predictions.txt"), open_mock.call_args_list[1][0][0])
        self.assertEqual("w", open_mock.call_args_list[1][0][1])
        # Saved prediction content is what we expect
        self.assertEqual(prediction_string, file_objects[1].write.call_args[0][0])
        # And we called the conversion function that will format the predictions for labeling
        self.assertEqual(1, mock_generate_labeling_results.call_count)
        self.assertEqual(os.path.join("outputs", "predictions.txt"), mock_generate_labeling_results.call_args[0][0])
        self.assertEqual(["file1", "file2"], mock_generate_labeling_results.call_args[0][1])


if __name__ == "__main__":
    unittest.main()
