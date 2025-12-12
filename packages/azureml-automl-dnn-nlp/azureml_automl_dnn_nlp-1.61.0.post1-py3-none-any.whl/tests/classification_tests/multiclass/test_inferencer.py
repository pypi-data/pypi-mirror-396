from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import torch
import unittest

from azureml.automl.dnn.nlp.classification.common.constants import DatasetLiterals
from azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer import MulticlassInferencer
from azureml.automl.dnn.nlp.common.constants import DataLiterals, SystemSettings
from ...mocks import (
    aml_dataset_mock, aml_label_dataset_mock, get_multiclass_labeling_df, open_classification_file, MockRun
)


class TestMulticlassInferencer(unittest.TestCase):
    def test_predict(self):
        mock_wrapped_model = MagicMock()
        pred_probas = [[0.10, 0.20, 0.40, 0.10, 0.20],
                       [0.99, 0.01, 0.00, 0.00, 0.00],
                       [0.00, 0.01, 0.60, 0.35, 0.04],
                       [0.25, 0.25, 0.01, 0.40, 0.09],
                       [0.00, 0.00, 0.11, 0.00, 0.89]]
        mock_wrapped_model.predict_proba.return_value = pred_probas
        mock_wrapped_model.classes_ = {idx: str(idx) for idx in range(5)}

        run = MockRun()
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        inferencer = MulticlassInferencer(run, device)

        input_data = pd.DataFrame({"input": np.array(["First", "Second", "Third", "Fourth", "Fifth"])})
        preds_df = inferencer.predict(wrapped_model=mock_wrapped_model,
                                      test_df=input_data,
                                      label_column_name="labels")
        self.assertIn("labels", preds_df.columns)
        self.assertIn(DataLiterals.LABEL_CONFIDENCE, preds_df.columns)
        self.assertTrue((np.array(['2', '0', '2', '3', '4']) == preds_df["labels"].values).all())
        self.assertTrue((np.amax(pred_probas, axis=1) == preds_df[DataLiterals.LABEL_CONFIDENCE].values).all())
        self.assertTrue((preds_df["input"] == input_data["input"]).all())

    @patch('azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer.save_predicted_results')
    @patch('azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer.load_model_wrapper')
    @patch("azureml.core.Dataset.get_by_id")
    def test_score(self,
                   get_by_id_mock, mock_load_model_wrapper, mock_save_preds):
        input_df = pd.DataFrame({"text": np.array(["First", "Second", "Third", "Fourth", "Fifth"]),
                                 DataLiterals.LABEL_COLUMN: np.array(['1', '3', '2', '3', '5'])})
        mock_aml_dataset = aml_dataset_mock(input_df)
        get_by_id_mock.return_value = mock_aml_dataset

        run = MockRun(label_column_name=DataLiterals.LABEL_COLUMN)
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        inferencer = MulticlassInferencer(run, device)

        model_predictions = input_df.copy()
        model_predictions[DataLiterals.LABEL_CONFIDENCE] = np.array([0.84, 0.76, 0.99, 0.87, 0.95])
        model_predictions[DataLiterals.LABEL_COLUMN] = np.array(['1', '3', '2', '3', '5'])
        with patch.object(inferencer, 'predict', return_value=model_predictions):
            pred_df = inferencer.score(input_dataset_id="some dataset id")

        self.assertEqual(2, pred_df.shape[1])
        self.assertTrue(all([col in pred_df.columns for col in [DataLiterals.LABEL_COLUMN,
                                                                DataLiterals.LABEL_CONFIDENCE]]))
        self.assertEqual(5, pred_df.shape[0])
        self.assertTrue((model_predictions[DataLiterals.LABEL_COLUMN] == pred_df[DataLiterals.LABEL_COLUMN]).all())
        self.assertTrue((model_predictions[DataLiterals.LABEL_CONFIDENCE]
                         == pred_df[DataLiterals.LABEL_CONFIDENCE]).all())
        self.assertEqual(1, mock_save_preds.call_count)

    @patch("azureml.automl.dnn.nlp.classification.io.read._labeling_data_helper.open",
           new=open_classification_file)
    @patch('azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer.'
           'generate_predictions_output_for_labeling_service_multiclass')
    @patch('azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer.load_model_wrapper')
    @patch('azureml.core.Dataset.get_by_id')
    def test_score_labeling(self,
                            get_by_id_mock, mock_load_model_wrapper, mock_generate_preds):
        model_predictions = get_multiclass_labeling_df().head(3)
        mock_dataset = aml_label_dataset_mock(
            'TextClassificationMultiClass', data_df=model_predictions
        )
        get_by_id_mock.return_value = mock_dataset

        run = MockRun(run_source=SystemSettings.LABELING_RUNSOURCE,
                      label_column_name=DataLiterals.LABEL_COLUMN,
                      labeling_dataset_type="FileDataset")

        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        inferencer = MulticlassInferencer(run, device)

        with patch.object(inferencer, "predict", return_value=model_predictions):
            inferencer.score(input_dataset_id="some dataset id")

        #  Labeling code path doesn't mutate prediction dataframe passed by `predict`,
        #  so no need to check it when we set that value ourselves.
        self.assertTrue(mock_generate_preds.call_args[0][0].equals(model_predictions))
        self.assertEqual(1, mock_generate_preds.call_count)

    @patch('azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer.save_predicted_results')
    @patch('azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer.load_model_wrapper')
    @patch('azureml.core.Dataset.get_by_id')
    def test_score_labeling_enable_datapoint_id_output(self,
                                                       get_by_id_mock, mock_load_model_wrapper, mock_save_preds):
        input_df = pd.DataFrame({"input": np.array(["First", "Second", "Third", "Fourth", "Fifth"]),
                                 DatasetLiterals.DATAPOINT_ID: np.array([f"id_{idx}" for idx in range(5)]),
                                 DataLiterals.LABEL_COLUMN: np.array(['2', '4', '5', '2', '3'])})
        mock_aml_dataset = aml_dataset_mock(input_df)
        get_by_id_mock.return_value = mock_aml_dataset

        run = MockRun(run_source=SystemSettings.LABELING_RUNSOURCE,
                      label_column_name=DataLiterals.LABEL_COLUMN,
                      labeling_dataset_type="TabularDataset")
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        inferencer = MulticlassInferencer(run, device)

        model_predictions = input_df.copy()
        model_predictions[DataLiterals.LABEL_COLUMN] = np.array(['2', '4', '5', '2', '3'])
        model_predictions[DataLiterals.LABEL_CONFIDENCE] = np.array([0.87, 0.99, 0.84, 0.98, 0.93])
        with patch.object(inferencer, 'predict', return_value=model_predictions):
            pred_df = inferencer.score(input_dataset_id="some dataset id",
                                       enable_datapoint_id_output=True)
        self.assertEqual(3, pred_df.shape[1])
        self.assertTrue(all([col in pred_df.columns for col in [DataLiterals.LABEL_COLUMN,
                                                                DataLiterals.LABEL_CONFIDENCE,
                                                                DatasetLiterals.DATAPOINT_ID]]))
        self.assertEqual(5, pred_df.shape[0])
        self.assertTrue((model_predictions[DataLiterals.LABEL_COLUMN] == pred_df[DataLiterals.LABEL_COLUMN]).all())
        self.assertTrue((model_predictions[DataLiterals.LABEL_CONFIDENCE]
                         == pred_df[DataLiterals.LABEL_CONFIDENCE]).all())
        self.assertTrue((model_predictions[DatasetLiterals.DATAPOINT_ID]
                         == pred_df[DatasetLiterals.DATAPOINT_ID]).all())
        self.assertEqual(1, mock_save_preds.call_count)

    @patch('azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer.save_predicted_results')
    @patch('azureml.automl.dnn.nlp.classification.inference.multiclass_inferencer.load_model_wrapper')
    @patch('azureml.data.abstract_dataset.AbstractDataset._load')
    def test_score_mltable_uri(self, mock_load_dataset, mock_load_model_wrapper, mock_save_preds):
        input_df = pd.DataFrame({"text": np.array(["First", "Second", "Third", "Fourth", "Fifth"]),
                                 DataLiterals.LABEL_COLUMN: np.array(['1', '3', '2', '3', '5'])})
        mock_aml_dataset = aml_dataset_mock(input_df)
        mock_load_dataset.return_value = mock_aml_dataset

        run = MockRun(label_column_name=DataLiterals.LABEL_COLUMN)
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        inferencer = MulticlassInferencer(run, device)

        model_predictions = input_df.copy()
        model_predictions[DataLiterals.LABEL_CONFIDENCE] = np.array([0.84, 0.76, 0.99, 0.87, 0.95])
        model_predictions[DataLiterals.LABEL_COLUMN] = np.array(['1', '3', '2', '3', '5'])
        with patch.object(inferencer, "predict", return_value=model_predictions):
            pred_df = inferencer.score(input_mltable_uri="some mltable uri")

        self.assertEqual(2, pred_df.shape[1])
        self.assertTrue(all([col in pred_df.columns for col in [DataLiterals.LABEL_COLUMN,
                                                                DataLiterals.LABEL_CONFIDENCE]]))
        self.assertEqual(5, pred_df.shape[0])
        self.assertTrue((model_predictions[DataLiterals.LABEL_COLUMN] == pred_df[DataLiterals.LABEL_COLUMN]).all())
        self.assertTrue((model_predictions[DataLiterals.LABEL_CONFIDENCE]
                         == pred_df[DataLiterals.LABEL_CONFIDENCE]).all())
        self.assertEqual(1, mock_save_preds.call_count)
