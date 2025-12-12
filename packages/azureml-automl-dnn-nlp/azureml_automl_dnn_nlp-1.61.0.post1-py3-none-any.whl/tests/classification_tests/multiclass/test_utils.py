from unittest.mock import patch, Mock

import numpy as np
import pandas as pd
import pytest

from azureml.automl.core.shared import constants
from azureml.automl.dnn.nlp.classification.multiclass.utils import compute_metrics, get_max_seq_length
from azureml.automl.dnn.nlp.common._utils import concat_text_columns, is_data_labeling_run_with_file_dataset
from azureml.automl.dnn.nlp.common.constants import TrainingDefaultSettings, TrainingInputLiterals
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration
from ...mocks import MockRun


class TestTextClassificationUtils:
    """Tests for utility functions for multi-class text classification."""
    @pytest.mark.parametrize('class_labels, train_labels',
                             [pytest.param(np.array(['ABC', 'DEF', 'XYZ']), np.array(['ABC', 'DEF'])),
                              pytest.param(np.array(['ABC', 'DEF', 'XYZ']), np.array(['ABC', 'DEF', 'XYZ']))])
    def test_compute_metrics(self, class_labels, train_labels):
        predictions = np.random.rand(5, len(train_labels))
        y_val = np.random.choice(class_labels, size=5)
        results = compute_metrics(y_val, predictions, class_labels, train_labels)
        metrics_names = list(constants.Metric.CLASSIFICATION_SET)
        assert all(key in metrics_names for key in results)

    @pytest.mark.usefixtures('MulticlassDatasetTester')
    @pytest.mark.parametrize('multiple_text_column', [True, False])
    @pytest.mark.parametrize('include_label_col', [True, False])
    def test_concat_text_columns(self, MulticlassDatasetTester, include_label_col):
        input_df = MulticlassDatasetTester.get_data().copy()
        label_column_name = "labels_col" if include_label_col else None
        all_text_cols = [column for column in input_df.columns
                         if label_column_name is None or label_column_name != column]
        expected_concatenated_text = input_df[all_text_cols].apply(lambda x: ". ".join(x.values.astype(str)), axis=1)
        for index in range(len(input_df)):
            concatenated_text = concat_text_columns(input_df.iloc[index], input_df.columns, label_column_name)
            assert concatenated_text == expected_concatenated_text[index]

    @patch("azureml.automl.dnn.nlp.classification.multiclass.utils.os.mkdir")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.utils.np.save")
    def test_get_max_seq_length_disabled(self, mock_np_save, mock_os_mkdir):
        training_configuration = TrainingConfiguration(
            {TrainingInputLiterals.MAX_SEQ_LENGTH: TrainingDefaultSettings.DEFAULT_SEQ_LEN,
             TrainingInputLiterals.LONG_RANGE_LENGTH: TrainingDefaultSettings.LONG_RANGE_MAX,
             TrainingInputLiterals.LONG_RANGE_THRESHOLD: TrainingDefaultSettings.MIN_PROPORTION_LONG_RANGE},
            _internal=True)
        seq_len = get_max_seq_length(train_df=Mock(),
                                     tokenizer=Mock(),
                                     label_column_name="labels",
                                     training_configuration=training_configuration,
                                     enable_long_range_text=False)
        assert seq_len == TrainingDefaultSettings.DEFAULT_SEQ_LEN

    @pytest.mark.usefixtures('MulticlassTokenizer')
    @patch("azureml.automl.dnn.nlp.classification.multiclass.utils.os.mkdir")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.utils.np.save")
    def test_get_max_seq_length_single_column_long_range(self, mock_np_save, mock_os_mkdir, MulticlassTokenizer):
        train_df = pd.DataFrame({"input": np.array(["This is a very long text entry. " * 20] * 2
                                                   + ["These are shorter entries."] * 8),
                                 "labels": np.arange(10)})
        training_configuration = TrainingConfiguration(
            {TrainingInputLiterals.MAX_SEQ_LENGTH: TrainingDefaultSettings.DEFAULT_SEQ_LEN,
             TrainingInputLiterals.LONG_RANGE_LENGTH: TrainingDefaultSettings.LONG_RANGE_MAX,
             TrainingInputLiterals.LONG_RANGE_THRESHOLD: TrainingDefaultSettings.MIN_PROPORTION_LONG_RANGE},
            _internal=True)
        seq_len = get_max_seq_length(train_df=train_df,
                                     tokenizer=MulticlassTokenizer,
                                     label_column_name="labels",
                                     training_configuration=training_configuration,
                                     enable_long_range_text=True)
        assert seq_len == TrainingDefaultSettings.LONG_RANGE_MAX

    @pytest.mark.usefixtures('MulticlassTokenizer')
    @patch("azureml.automl.dnn.nlp.classification.multiclass.utils.os.mkdir")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.utils.np.save")
    def test_get_max_seq_length_multi_column_long_range(self, mock_np_save, mock_os_mkdir, MulticlassTokenizer):
        train_df = pd.DataFrame({"input": np.array(["This is a text entry that's long enough that two columns of it "
                                                    "concatenated together will be considered long range. " * 4] * 2
                                                   + ["These are shorter entries."] * 8),
                                 "second_input": np.array(["This is a text entry that's long enough that two columns "
                                                           "of it concatenated together will be considered long "
                                                           "range. " * 4] * 2
                                                          + ["These are shorter entries."] * 8),
                                 "labels": np.arange(10)})
        training_configuration = TrainingConfiguration(
            {TrainingInputLiterals.MAX_SEQ_LENGTH: TrainingDefaultSettings.DEFAULT_SEQ_LEN,
             TrainingInputLiterals.LONG_RANGE_LENGTH: TrainingDefaultSettings.LONG_RANGE_MAX,
             TrainingInputLiterals.LONG_RANGE_THRESHOLD: TrainingDefaultSettings.MIN_PROPORTION_LONG_RANGE},
            _internal=True)
        seq_len = get_max_seq_length(train_df=train_df,
                                     tokenizer=MulticlassTokenizer,
                                     label_column_name="labels",
                                     training_configuration=training_configuration,
                                     enable_long_range_text=True)
        assert seq_len == TrainingDefaultSettings.LONG_RANGE_MAX

    @pytest.mark.usefixtures('MulticlassTokenizer')
    @patch("azureml.automl.dnn.nlp.classification.multiclass.utils.os.mkdir")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.utils.np.save")
    def test_get_max_seq_length_single_column_short_range(self, mock_np_save, mock_os_mkdir, MulticlassTokenizer):
        train_df = pd.DataFrame({"input": np.array(["These are shorter entries."] * 10),
                                 "labels": np.arange(10)})
        training_configuration = TrainingConfiguration(
            {TrainingInputLiterals.MAX_SEQ_LENGTH: TrainingDefaultSettings.DEFAULT_SEQ_LEN,
             TrainingInputLiterals.LONG_RANGE_LENGTH: TrainingDefaultSettings.LONG_RANGE_MAX,
             TrainingInputLiterals.LONG_RANGE_THRESHOLD: TrainingDefaultSettings.MIN_PROPORTION_LONG_RANGE},
            _internal=True)
        seq_len = get_max_seq_length(train_df=train_df,
                                     tokenizer=MulticlassTokenizer,
                                     label_column_name="labels",
                                     training_configuration=training_configuration,
                                     enable_long_range_text=True)
        assert seq_len == TrainingDefaultSettings.DEFAULT_SEQ_LEN

    @pytest.mark.usefixtures('MulticlassTokenizer')
    @patch("azureml.automl.dnn.nlp.classification.multiclass.utils.os.mkdir")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.utils.np.save")
    def test_get_max_seq_length_multi_column_short_range(self, mock_np_save, mock_os_mkdir, MulticlassTokenizer):
        train_df = pd.DataFrame({"input": np.array(["This is a the first short text entry!"] * 10),
                                 "second_input": np.array(["This is the second short text entry!"] * 10),
                                 "labels": np.arange(10)})
        training_configuration = TrainingConfiguration(
            {TrainingInputLiterals.MAX_SEQ_LENGTH: TrainingDefaultSettings.DEFAULT_SEQ_LEN,
             TrainingInputLiterals.LONG_RANGE_LENGTH: TrainingDefaultSettings.LONG_RANGE_MAX,
             TrainingInputLiterals.LONG_RANGE_THRESHOLD: TrainingDefaultSettings.MIN_PROPORTION_LONG_RANGE},
            _internal=True)
        seq_len = get_max_seq_length(train_df=train_df,
                                     tokenizer=MulticlassTokenizer,
                                     label_column_name="labels",
                                     training_configuration=training_configuration,
                                     enable_long_range_text=True)
        assert seq_len == TrainingDefaultSettings.DEFAULT_SEQ_LEN

    def test_is_data_labeling_negative_with_parent(self):
        current_run = MockRun()
        assert not is_data_labeling_run_with_file_dataset(current_run)

    def test_is_data_labeling_negative_none_parent(self):
        assert not is_data_labeling_run_with_file_dataset(None)

    def test_is_data_labeling_positive_with_parent(self):
        current_run = MockRun('Labeling', 'y', "auto", 'FileDataset')
        assert is_data_labeling_run_with_file_dataset(current_run)
