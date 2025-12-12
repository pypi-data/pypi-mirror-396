from unittest.mock import MagicMock, Mock, patch

import os
import pytest
import unittest

from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import MissingDataset
from azureml.automl.dnn.nlp.common.constants import DataLiterals, OutputLiterals, Split, \
    TrainingInputLiterals, TrainingDefaultSettings
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration
from azureml.automl.dnn.nlp.ner.io.read.dataloader import load_and_validate_dataset
from ..mocks import file_dataset_mock, get_local_tokenizer, MockValidator


@pytest.mark.usefixtures('new_clean_dir')
class DataLoaderTest(unittest.TestCase):
    """Tests for NER data loader."""
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.ner.io.read.dataloader.NLPNERDataValidator")
    def test_load_dataset(self, validator_mock, get_by_id_mock):
        mock_file_dataset = file_dataset_mock()
        get_by_id_mock.return_value = mock_file_dataset
        automl_settings = dict()
        automl_settings['dataset_id'] = 'mock_id'
        automl_settings['validation_dataset_id'] = 'mock_validation_id'
        workspace_mock = Mock()
        ner_dir = DataLiterals.NER_DATA_DIR
        output_dir = OutputLiterals.OUTPUT_DIR
        labels_file = "test_load_dataset_labels.txt"
        tokenizer = get_local_tokenizer()

        # data validation mock
        validator_mock.return_value = MockValidator()

        training_configuration = TrainingConfiguration(
            {TrainingInputLiterals.MAX_SEQ_LENGTH: TrainingDefaultSettings.DEFAULT_SEQ_LEN,
             TrainingInputLiterals.PADDING_STRATEGY: TrainingDefaultSettings.MAX_LENGTH},
            _internal=True)
        train_dataset, eval_dataset, label_list = load_and_validate_dataset(
            workspace=workspace_mock,
            data_dir=ner_dir,
            output_dir=output_dir,
            labels_filename=labels_file,
            tokenizer=tokenizer,
            automl_settings=automl_settings,
            training_configuration=training_configuration
        )

        self.assertEqual(get_by_id_mock.call_count, 2)
        self.assertEqual(mock_file_dataset.download.call_count, 2)
        self.assertEqual(mock_file_dataset.to_path.call_count, 2)
        self.assertEqual(len(train_dataset.data), 3)
        self.assertEqual(len(eval_dataset.data), 2)
        self.assertEqual(
            set(label_list),
            set(['I-PER', 'I-ORG', 'B-LOC', 'B-PER', 'B-ORG', 'I-MISC', 'B-MISC', 'O'])
        )
        labels_output_path = os.path.join(output_dir, labels_file)
        with open(labels_output_path, 'r') as f:
            labels = [line.rstrip() for line in f]
        self.assertIsNotNone(labels)
        self.assertEqual(
            set(labels),
            set(['I-PER', 'I-ORG', 'B-LOC', 'B-PER', 'B-ORG', 'I-MISC', 'B-MISC', 'O'])
        )

    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.ner.io.read.dataloader._save_labels")
    @patch("azureml.automl.dnn.nlp.ner.io.read.dataloader.NLPNERDataValidator")
    def test_load_dataset_unseen_valid_labels(self, skip_validation, skip_save_labels, get_by_id_mock):
        mock_file_dataset = file_dataset_mock(side_effect=[["/train.txt"], ["/unseen_dev.txt"]])
        get_by_id_mock.return_value = mock_file_dataset
        automl_settings = {"dataset_id": "mock_id",
                           "validation_dataset_id": "mock_validation_id"}
        training_configuration = TrainingConfiguration({TrainingInputLiterals.MAX_SEQ_LENGTH:
                                                        TrainingDefaultSettings.DEFAULT_SEQ_LEN,
                                                        TrainingInputLiterals.PADDING_STRATEGY:
                                                            TrainingDefaultSettings.MAX_LENGTH},
                                                       _internal=True)
        _, _, label_list = load_and_validate_dataset(
            workspace=Mock(),
            data_dir=DataLiterals.NER_DATA_DIR,
            output_dir=OutputLiterals.OUTPUT_DIR,
            labels_filename="some filename",
            tokenizer=get_local_tokenizer(),
            automl_settings=automl_settings,
            training_configuration=training_configuration
        )

        # Label list picks up unseen validation label, "B-FOOD."
        self.assertEqual(set(label_list),
                         {"B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "B-MISC", "I-MISC", "B-FOOD", "O"})

    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.data.abstract_dataset.AbstractDataset._load")
    @patch("azureml.automl.dnn.nlp.ner.io.read.dataloader.NLPNERDataValidator")
    def test_load_dataset_no_val_data(self, validator_mock, dataset_load_mock, get_by_id_mock):
        mock_file_dataset = file_dataset_mock()
        get_by_id_mock.return_value = mock_file_dataset
        dataset_load_mock.return_value = mock_file_dataset
        mltable_data_json_list = [None,
                                  '{"TrainData": {"Uri": "azuremluri", "ResolvedUri": "resolved_uri"}, '
                                  '"ValidData": null}']
        automl_settings = dict()
        workspace_mock = Mock()
        ner_dir = DataLiterals.NER_DATA_DIR
        output_dir = "ner_data/output_dir"
        labels_file = "test_load_dataset_labels.txt"
        tokenizer = Mock()
        # data validation mock
        validator_mock.return_value = MockValidator()

        training_configuration = TrainingConfiguration(
            {TrainingInputLiterals.MAX_SEQ_LENGTH: TrainingDefaultSettings.DEFAULT_SEQ_LEN,
             TrainingInputLiterals.PADDING_STRATEGY: TrainingDefaultSettings.MAX_LENGTH},
            _internal=True)
        for mltable_data_json in mltable_data_json_list:
            if mltable_data_json is None:
                automl_settings['dataset_id'] = 'mock_id'
            with pytest.raises(DataException) as exc:
                load_and_validate_dataset(
                    workspace=workspace_mock,
                    data_dir=ner_dir,
                    output_dir=output_dir,
                    labels_filename=labels_file,
                    tokenizer=tokenizer,
                    automl_settings=automl_settings,
                    training_configuration=training_configuration,
                    mltable_data_json=mltable_data_json
                )
            assert exc.value.error_code == MissingDataset.__name__
            assert Split.valid.value.capitalize() in exc.value.message_format

    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.ner.io.read.dataloader.NLPNERDataValidator")
    def test_load_dataset_same_ids(self, validator_mock, get_by_id_mock):
        mock_file_dataset = file_dataset_mock([["/train.txt"], ["/train.txt"]])
        get_by_id_mock.return_value = mock_file_dataset
        automl_settings = dict()
        automl_settings['dataset_id'] = 'mock_id'
        automl_settings['validation_dataset_id'] = 'mock_id'
        workspace_mock = Mock()
        ner_dir = DataLiterals.NER_DATA_DIR
        output_dir = OutputLiterals.OUTPUT_DIR
        labels_file = "test_load_dataset_labels.txt"
        tokenizer = MagicMock()

        # data validation mock
        validator_mock.return_value = MockValidator()

        training_configuration = TrainingConfiguration(
            {TrainingInputLiterals.MAX_SEQ_LENGTH: TrainingDefaultSettings.DEFAULT_SEQ_LEN,
             TrainingInputLiterals.PADDING_STRATEGY: TrainingDefaultSettings.MAX_LENGTH},
            _internal=True)
        train_dataset, eval_dataset, label_list = load_and_validate_dataset(
            workspace=workspace_mock,
            data_dir=ner_dir,
            output_dir=output_dir,
            labels_filename=labels_file,
            tokenizer=tokenizer,
            automl_settings=automl_settings,
            training_configuration=training_configuration
        )

        self.assertEqual(get_by_id_mock.call_count, 2)
        self.assertEqual(mock_file_dataset.download.call_count, 2)
        self.assertEqual(mock_file_dataset.to_path.call_count, 2)
        self.assertEqual(len(train_dataset.data), 3)
        self.assertEqual(len(eval_dataset.data), 3)

    @patch("azureml.data.abstract_dataset.AbstractDataset._load")
    @patch("azureml.automl.dnn.nlp.ner.io.read.dataloader.NLPNERDataValidator")
    def test_load_dataset_mltable_data_json(self, validator_mock, dataset_load_mock):
        mock_file_dataset = file_dataset_mock()
        dataset_load_mock.return_value = mock_file_dataset
        automl_settings = dict()
        mltable_data_json = '{"TrainData": {"Uri": "azuremluri", "ResolvedUri": "resolved_uri"}, ' \
                            '"ValidData": {"Uri": "azuremluri2", "ResolvedUri": "resolved_uri2"}}'
        workspace_mock = Mock()
        ner_dir = DataLiterals.NER_DATA_DIR
        output_dir = OutputLiterals.OUTPUT_DIR
        labels_file = "test_load_dataset_labels.txt"
        tokenizer = get_local_tokenizer()

        # data validation mock
        validator_mock.return_value = MockValidator()

        training_configuration = TrainingConfiguration(
            {TrainingInputLiterals.MAX_SEQ_LENGTH: TrainingDefaultSettings.DEFAULT_SEQ_LEN,
             TrainingInputLiterals.PADDING_STRATEGY: TrainingDefaultSettings.MAX_LENGTH},
            _internal=True)
        train_dataset, eval_dataset, label_list = load_and_validate_dataset(
            workspace=workspace_mock,
            data_dir=ner_dir,
            output_dir=output_dir,
            labels_filename=labels_file,
            tokenizer=tokenizer,
            automl_settings=automl_settings,
            training_configuration=training_configuration,
            mltable_data_json=mltable_data_json
        )

        self.assertEqual(dataset_load_mock.call_count, 2)
        self.assertEqual(mock_file_dataset.download.call_count, 2)
        self.assertEqual(mock_file_dataset.to_path.call_count, 2)
        self.assertEqual(len(train_dataset.data), 3)
        self.assertEqual(len(eval_dataset.data), 2)
        self.assertEqual(
            set(label_list),
            set(['I-PER', 'I-ORG', 'B-LOC', 'B-PER', 'B-ORG', 'I-MISC', 'B-MISC', 'O'])
        )
        labels_output_path = os.path.join(output_dir, labels_file)
        with open(labels_output_path, 'r') as f:
            labels = [line.rstrip() for line in f]
        self.assertIsNotNone(labels)
        self.assertEqual(
            set(labels),
            set(['I-PER', 'I-ORG', 'B-LOC', 'B-PER', 'B-ORG', 'I-MISC', 'B-MISC', 'O'])
        )


if __name__ == "__main__":
    unittest.main()
