from unittest.mock import MagicMock, Mock, patch

import ast
import numpy as np
import pandas as pd
import pytest
import unittest

from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import MultilabelDatasetWrapper
from azureml.automl.dnn.nlp.classification.io.read.dataloader import load_and_validate_multilabel_dataset
from azureml.automl.dnn.nlp.classification.io.read.read_utils import get_y_transformer
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import MissingDataset
from azureml.automl.dnn.nlp.common.constants import DataLiterals, Split, \
    TrainingDefaultSettings, TrainingInputLiterals
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration
from ...mocks import aml_dataset_mock, aml_label_dataset_mock, get_multilabel_labeling_df, open_classification_file

try:
    import torch
    has_torch = True
except ImportError:
    has_torch = False


@pytest.mark.usefixtures('MultilabelDatasetTester')
@pytest.mark.usefixtures('MultilabelTokenizer')
@pytest.mark.parametrize('multiple_text_column', [False])
class TestMultilabelDatasetWrapper:
    @pytest.fixture(autouse=True)
    def _before_each(self):
        self.training_configuration = TrainingConfiguration(
            {TrainingInputLiterals.MAX_SEQ_LENGTH: TrainingDefaultSettings.DEFAULT_SEQ_LEN,
             TrainingInputLiterals.PADDING_STRATEGY: TrainingDefaultSettings.MAX_LENGTH,
             TrainingInputLiterals.LONG_RANGE_LENGTH: TrainingDefaultSettings.LONG_RANGE_MAX,
             TrainingInputLiterals.LONG_RANGE_THRESHOLD: TrainingDefaultSettings.MIN_PROPORTION_LONG_RANGE},
            _internal=True)
        yield

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_pytorch_dataset_wrapper(self, MultilabelDatasetTester, MultilabelTokenizer):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        y_transformer = get_y_transformer(input_df, input_df, label_column_name)
        num_label_cols = len(y_transformer.classes_)
        assert num_label_cols == 6
        training_set = MultilabelDatasetWrapper(
            dataframe=input_df,
            tokenizer=MultilabelTokenizer,
            training_configuration=self.training_configuration,
            label_column_name=label_column_name, y_transformer=y_transformer)
        assert len(training_set) == 50
        assert set(training_set[1].keys()) == {'input_ids', 'attention_mask', 'token_type_ids', 'label'}
        assert all(torch.is_tensor(value) for key, value in training_set[1].items())

        expected_targets = y_transformer.transform([ast.literal_eval(input_df["labels_col"][1])])
        expected_targets = expected_targets.toarray().astype(np.float32)[0]
        actual_targets = training_set[1]['label'].detach().numpy()
        assert np.array_equal(actual_targets, expected_targets)
        assert np.issubdtype(actual_targets.dtype, np.float32) and np.issubdtype(expected_targets.dtype, np.float32)

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_pytorch_dataset_wrapper_for_inference(self, MultilabelDatasetTester, MultilabelTokenizer):
        input_df = MultilabelDatasetTester.get_data().copy()
        input_df = input_df.drop(columns=["labels_col"]).reset_index(drop=True)
        training_set = MultilabelDatasetWrapper(dataframe=input_df,
                                                tokenizer=MultilabelTokenizer,
                                                training_configuration=self.training_configuration)
        assert len(training_set) == 50
        assert set(training_set[1].keys()) == {'input_ids', 'attention_mask', 'token_type_ids'}
        assert all(torch.is_tensor(value) for key, value in training_set[1].items())

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_column_concatenation(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        y_transformer = get_y_transformer(input_df, input_df, label_column_name)
        num_label_cols = len(y_transformer.classes_)
        assert num_label_cols == 6

        tokenizer_mock = Mock()
        # We don't really care about this input; just set something that won't error.
        tokenizer_mock.return_value = {"input_ids": np.array([1, 2, 3]),
                                       "attention_mask": np.array([1, 2, 3]),
                                       "token_type_ids": np.array([1, 2, 3])}
        training_set = MultilabelDatasetWrapper(
            dataframe=input_df,
            tokenizer=tokenizer_mock,
            training_configuration=self.training_configuration,
            label_column_name=label_column_name,
            y_transformer=y_transformer)
        _ = training_set[0]  # noqa: F841
        assert tokenizer_mock.call_args[0][0] == "This is a small sample dataset containing cleaned text data."

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_column_concatenation_inference(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        input_df = input_df.drop(columns=["labels_col"]).reset_index(drop=True)
        tokenizer_mock = Mock()
        # We don't really care about this input; just set something that won't error.
        tokenizer_mock.return_value = {"input_ids": np.array([1, 2, 3]),
                                       "attention_mask": np.array([1, 2, 3]),
                                       "token_type_ids": np.array([1, 2, 3])}
        training_set = MultilabelDatasetWrapper(
            dataframe=input_df,
            tokenizer=tokenizer_mock,
            training_configuration=self.training_configuration)
        _ = training_set[0]  # noqa: F841
        assert tokenizer_mock.call_args[0][0] == "This is a small sample dataset containing cleaned text data."

    def test_get_y_transformer(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        # Test both cases, with and without validation data
        for valid_df in [input_df, None]:
            y_transformer = get_y_transformer(input_df, valid_df, label_column_name)
            num_label_cols = len(y_transformer.classes_)
            assert num_label_cols == 6
            assert set(y_transformer.classes_) == {'A', 'a', '1', '2', 'label5', 'label6'}

    @unittest.skipIf(not has_torch, "torch not installed")
    @patch("azureml.core.Dataset.get_by_id")
    def test_load_multilabel_dataset(self, get_by_id_mock, MultilabelDatasetTester, MultilabelTokenizer):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        mock_aml_dataset = aml_dataset_mock(input_df)
        get_by_id_mock.return_value = mock_aml_dataset
        automl_settings = dict()
        automl_settings['dataset_id'] = 'mock_id'
        automl_settings['validation_dataset_id'] = 'mock_validation_id'
        aml_workspace_mock = MagicMock()
        training_set, validation_set, num_label_cols, train_label_list, label_list, y_val, _ = \
            load_and_validate_multilabel_dataset(
                workspace=aml_workspace_mock,
                data_dir=DataLiterals.DATA_DIR,
                label_column_name=label_column_name,
                tokenizer=MultilabelTokenizer,
                automl_settings=automl_settings,
                training_configuration=self.training_configuration
            )
        assert num_label_cols == 6
        expected_train_label_list = np.array(['1', '2', 'A', 'a', 'label5', 'label6'])
        assert np.array_equal(train_label_list, expected_train_label_list)
        assert len(train_label_list) == 6
        assert all(np.array(input_df[label_column_name]) == y_val)
        for output_set in [training_set, validation_set]:
            assert type(output_set) == MultilabelDatasetWrapper
            assert len(output_set) == 50
            assert all(set(output_set[i].keys())
                       == {'input_ids', 'attention_mask', 'token_type_ids', 'label'} for i in range(len(output_set)))

    @unittest.skipIf(not has_torch, "torch not installed")
    @patch('azureml.automl.dnn.nlp.classification.io.read.dataloader.NLPMultilabelDataValidator')
    @patch('azureml.core.Dataset.get_by_id')
    def test_load_multilabel_dataset_with_unseen_labels(self, get_by_id_mock, mock_validator, MultilabelTokenizer):
        train_df = pd.DataFrame({"input": np.array(["Example 1", "Example 2", "Example 3"]),
                                 "labels": np.array(["[1]", "[1, 2]", "[2]"])})
        valid_df = pd.DataFrame({"input": np.array(["Example 1", "Example 2", "Example 3"]),
                                 "labels": np.array(["[1]", "[1, 3]", "[2, 3]"])})
        mock_train_dataset = aml_dataset_mock(train_df)
        mock_valid_dataset = aml_dataset_mock(valid_df)
        get_by_id_mock.side_effect = (mock_train_dataset, mock_valid_dataset)
        automl_settings = {"dataset_id": "mock_id",
                           "validation_dataset_id": "mock_validation_id"}
        _, _, num_label_cols, train_label_list, label_list, _, _ = \
            load_and_validate_multilabel_dataset(
                workspace=MagicMock(),
                data_dir=DataLiterals.DATA_DIR,
                label_column_name="labels",
                tokenizer=MultilabelTokenizer,
                automl_settings=automl_settings,
                training_configuration=self.training_configuration
            )

        assert num_label_cols == 3
        expected_labels = {'1', '2', '3'}
        # For now, unseen valid labels are included in train set so model is aware of them for training.
        assert set(train_label_list) == expected_labels
        assert set(label_list) == expected_labels

    @unittest.skipIf(not has_torch, "torch not installed")
    @pytest.mark.parametrize(
        'mltable_data_json', [
            None,
            '{"TrainData": {"Uri": "azuremluri", "ResolvedUri": "resolved_uri"}, '
            '"ValidData": null}'
        ]
    )
    @patch("azureml.data.abstract_dataset.AbstractDataset._load")
    @patch("azureml.core.Dataset.get_by_id")
    def test_load_multilabel_dataset_no_val_set(self, get_by_id_mock, dataset_load_mock,
                                                mltable_data_json, MultilabelDatasetTester, MultilabelTokenizer):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        mock_aml_dataset = aml_dataset_mock(input_df)
        get_by_id_mock.return_value = mock_aml_dataset
        dataset_load_mock.return_value = mock_aml_dataset
        automl_settings = dict()
        if mltable_data_json is None:
            automl_settings['dataset_id'] = 'mock_id'
        aml_workspace_mock = MagicMock()

        with pytest.raises(DataException) as exc:
            load_and_validate_multilabel_dataset(
                workspace=aml_workspace_mock,
                data_dir=DataLiterals.DATA_DIR,
                label_column_name=label_column_name,
                tokenizer=MultilabelTokenizer,
                automl_settings=automl_settings,
                training_configuration=Mock(),
                mltable_data_json=mltable_data_json)
        assert exc.value.error_code == MissingDataset.__name__
        assert Split.valid.value.capitalize() in exc.value.message_format

    @unittest.skipIf(not has_torch, "torch not installed")
    @patch("azureml.core.Dataset.get_by_id")
    def test_load_multilabel_dataset_labeling_service(self, get_by_id_mock, MultilabelTokenizer):
        label_column_name = "label"
        mock_aml_dataset = aml_label_dataset_mock('TextClassificationMultiLabel', get_multilabel_labeling_df())
        get_by_id_mock.return_value = mock_aml_dataset
        automl_settings = dict()
        automl_settings['dataset_id'] = 'mock_id'
        automl_settings['validation_dataset_id'] = 'mock_validation_id'
        aml_workspace_mock = MagicMock()
        with patch("azureml.automl.dnn.nlp.classification.io.read._labeling_data_helper.open",
                   new=open_classification_file):
            training_set, validation_set, num_label_cols, train_label_list, label_list, y_val, _ = \
                load_and_validate_multilabel_dataset(
                    workspace=aml_workspace_mock,
                    data_dir=DataLiterals.DATA_DIR,
                    label_column_name=label_column_name,
                    tokenizer=MultilabelTokenizer,
                    automl_settings=automl_settings,
                    training_configuration=self.training_configuration,
                    mltable_data_json=None,
                    is_labeling_run=True
                )
        assert num_label_cols == 2
        expected_train_label_list = np.array(['label_1', 'label_2'])
        assert np.array_equal(expected_train_label_list, train_label_list)
        assert len(train_label_list) == 2
        for output_set in [training_set, validation_set]:
            assert type(output_set) == MultilabelDatasetWrapper
            assert len(output_set) == 60
            assert all(set(output_set[i].keys())
                       == {'input_ids', 'attention_mask', 'token_type_ids', 'label'} for i in range(len(output_set)))

    @unittest.skipIf(not has_torch, "torch not installed")
    @patch("azureml.data.abstract_dataset.AbstractDataset._load")
    def test_load_multilabel_dataset_mlflow_data_json(self, dataset_load_mock, MultilabelDatasetTester,
                                                      MultilabelTokenizer):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        mock_aml_dataset = aml_dataset_mock(input_df)
        dataset_load_mock.return_value = mock_aml_dataset
        automl_settings = dict()
        mltable_data_json = '{"TrainData": {"Uri": "azuremluri", "ResolvedUri": "resolved_uri"}, ' \
                            '"ValidData": {"Uri": "azuremluri2", "ResolvedUri": "resolved_uri2"}}'
        aml_workspace_mock = MagicMock()
        training_set, validation_set, num_label_cols, train_label_list, label_list, y_val, _ = \
            load_and_validate_multilabel_dataset(
                workspace=aml_workspace_mock,
                data_dir=DataLiterals.DATA_DIR,
                label_column_name=label_column_name,
                tokenizer=MultilabelTokenizer,
                automl_settings=automl_settings,
                training_configuration=self.training_configuration,
                mltable_data_json=mltable_data_json
            )
        assert num_label_cols == 6
        expected_train_label_list = np.array(['1', '2', 'A', 'a', 'label5', 'label6'])
        assert np.array_equal(train_label_list, expected_train_label_list)
        assert len(train_label_list) == 6
        assert all(np.array(input_df[label_column_name]) == y_val)
        for output_set in [training_set, validation_set]:
            assert type(output_set) == MultilabelDatasetWrapper
            assert len(output_set) == 50
            assert all(set(output_set[i].keys())
                       == {'input_ids', 'attention_mask', 'token_type_ids', 'label'} for i in range(len(output_set)))

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_multilabel_wrapped_dataset_non_standard_indexed_dataframes(self, MultilabelTokenizer):
        train_data = pd.DataFrame({"input_text_col": np.array(["I should eat some lunch.",
                                                               "Do I order out?",
                                                               "Or do I make something here?",
                                                               "Oh the many decisions faced by the average person."]),
                                   "labels": np.array(["['yes']", "['no']", "['yes']", "['tragic']"])})
        train_data.index = np.array([0, 1, 3, 4])
        y_transformer = get_y_transformer(train_data, None, "labels")
        wrapped_train = MultilabelDatasetWrapper(dataframe=train_data,
                                                 tokenizer=MultilabelTokenizer,
                                                 training_configuration=self.training_configuration,
                                                 label_column_name="labels",
                                                 y_transformer=y_transformer)
        assert torch.equal(wrapped_train[2]["label"], torch.tensor(np.array([0, 0, 1]), dtype=torch.float))

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_multilabel_wrapped_dataset_returns_labels_correctly(self, MultilabelTokenizer):
        train_data = pd.DataFrame({"input_text_col":
                                   np.array(["Sentence one", "Sentence two", "Sentence three", "Sentence four"]),
                                   "labels": np.array(["[1]", "[1, 2]", "[2]", "[]"])})
        y_transformer = get_y_transformer(train_data, None, "labels")
        wrapped_train = MultilabelDatasetWrapper(dataframe=train_data,
                                                 tokenizer=MultilabelTokenizer,
                                                 training_configuration=self.training_configuration,
                                                 label_column_name="labels",
                                                 y_transformer=y_transformer)
        expected_labels = np.array([[1, 0], [1, 1], [0, 1], [0, 0]])
        assert (wrapped_train.labels == expected_labels).all()


@pytest.mark.usefixtures('MultilabelDatasetTester')
@pytest.mark.usefixtures('MultilabelTokenizer')
@pytest.mark.parametrize('multiple_text_column', [True])
class TestMultilabelDatasetWrapperMultipleColumns:
    @pytest.fixture(autouse=True)
    def _before_each(self):
        self.training_configuration = TrainingConfiguration(
            {TrainingInputLiterals.MAX_SEQ_LENGTH: TrainingDefaultSettings.DEFAULT_SEQ_LEN,
             TrainingInputLiterals.PADDING_STRATEGY: TrainingDefaultSettings.MAX_LENGTH,
             TrainingInputLiterals.LONG_RANGE_LENGTH: TrainingDefaultSettings.LONG_RANGE_MAX,
             TrainingInputLiterals.LONG_RANGE_THRESHOLD: TrainingDefaultSettings.MIN_PROPORTION_LONG_RANGE},
            _internal=True)
        yield

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_pytorch_dataset_wrapper(self, MultilabelDatasetTester, MultilabelTokenizer):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        y_transformer = get_y_transformer(input_df, input_df, label_column_name)
        num_label_cols = len(y_transformer.classes_)
        assert num_label_cols == 6
        training_set = MultilabelDatasetWrapper(dataframe=input_df,
                                                tokenizer=MultilabelTokenizer,
                                                training_configuration=self.training_configuration,
                                                label_column_name=label_column_name,
                                                y_transformer=y_transformer)
        assert len(training_set) == 50
        assert all(item in ['input_ids', 'attention_mask', 'token_type_ids', 'label'] for item in training_set[1])
        assert all(torch.is_tensor(value) for key, value in training_set[1].items())

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_column_concatenation(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        y_transformer = get_y_transformer(input_df, input_df, label_column_name)
        num_label_cols = len(y_transformer.classes_)
        assert num_label_cols == 6

        tokenizer_mock = Mock()
        # We don't really care about this input; just set something that won't error.
        tokenizer_mock.return_value = {"input_ids": np.array([1, 2, 3]),
                                       "attention_mask": np.array([1, 2, 3]),
                                       "token_type_ids": np.array([1, 2, 3])}
        training_set = MultilabelDatasetWrapper(dataframe=input_df,
                                                tokenizer=tokenizer_mock,
                                                training_configuration=self.training_configuration,
                                                label_column_name=label_column_name,
                                                y_transformer=y_transformer)
        expected = 'This is a small sample dataset containing cleaned text data.. This is an additional column.'
        _ = training_set[0]  # noqa: F841
        assert tokenizer_mock.call_args[0][0] == expected

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_get_y_transformer(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        # Test both cases, with and without validation data
        for valid_df in [input_df, None]:
            y_transformer = get_y_transformer(input_df, valid_df, label_column_name)
            num_label_cols = len(y_transformer.classes_)
            assert num_label_cols == 6
            assert set(y_transformer.classes_) == {'A', 'a', '1', '2', 'label5', 'label6'}

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_column_concatenation_with_null_col_vals(self):
        input_df = pd.DataFrame({
            "column1": np.array(["This is a sentence", "Is this a question?", "Exclamatory remark, wow!",
                                 "a sentence fragment", None]),
            "column2": np.array(["This is a second sentence", "Is this a second question?",
                                 "Second exclamatory remark, double wow!", "second sentence fragment", "Word."]),
            "label": np.array(["['sentence']", "['question']", "['exclamatory', 'sentence']",
                               "['fragment']", "['fragment']"])
        })
        input_df = pd.concat((input_df for _ in range(10)), axis=0, ignore_index=True)
        y_transformer = get_y_transformer(input_df, None, "label")

        tokenizer_mock = Mock()
        # We don't really care about this input; just set something that won't error.
        tokenizer_mock.return_value = {"input_ids": np.array([1, 2, 3]),
                                       "attention_mask": np.array([1, 2, 3]),
                                       "token_type_ids": np.array([1, 2, 3])}
        wrapped_train = MultilabelDatasetWrapper(dataframe=input_df,
                                                 tokenizer=tokenizer_mock,
                                                 training_configuration=self.training_configuration,
                                                 label_column_name="label",
                                                 y_transformer=y_transformer)
        # trigger __getitem__, which concatenates text
        _ = wrapped_train[0]  # noqa: F841
        assert tokenizer_mock.call_args[0][0] == "This is a sentence. This is a second sentence"

        # trigger concatenation with none value
        _ = wrapped_train[4]  # noqa: F841
        assert tokenizer_mock.call_args[0][0] == "None. Word."


@pytest.mark.usefixtures("MultilabelNoisyLabelsTester")
class TestMultilabelLabelParser:
    @pytest.mark.parametrize("special_token", ['.', '-', '_', '+', ''])
    def test_noise_label(self, special_token, MultilabelNoisyLabelsTester):
        input_df = MultilabelNoisyLabelsTester.get_data().copy()
        y_transformer = get_y_transformer(input_df, None, "labels")
        print(y_transformer.classes_)
        assert len(y_transformer.classes_) == 5
        expected = ['1', '2', f'A{special_token}B', f'C{special_token}D', f'E{special_token}F']
        assert set(y_transformer.classes_) == set(expected)
