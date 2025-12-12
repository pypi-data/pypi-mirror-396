from sklearn.preprocessing import MultiLabelBinarizer

import numpy as np
import pandas as pd
import pytest

from azureml.automl.core.shared.constants import Metric
from azureml.automl.dnn.nlp.classification.multilabel.utils import change_label_col_format, compute_metrics
from azureml.automl.dnn.nlp.common.model_parameters import DEFAULT_NLP_PARAMETERS
from azureml.automl.dnn.nlp.common.constants import TrainingInputLiterals
from azureml.automl.runtime.shared.score.constants import CLASSIFICATION_NLP_MULTILABEL_SET


@pytest.mark.usefixtures('MultilabelDatasetTester')
@pytest.mark.parametrize('dataset_size',
                         [pytest.param(10),
                          pytest.param(10000),
                          pytest.param(DEFAULT_NLP_PARAMETERS[TrainingInputLiterals.VALID_BATCH_SIZE] // 2),
                          pytest.param(DEFAULT_NLP_PARAMETERS[TrainingInputLiterals.VALID_BATCH_SIZE] + 3),
                          pytest.param(DEFAULT_NLP_PARAMETERS[TrainingInputLiterals.VALID_BATCH_SIZE] * 3)]
                         )
@pytest.mark.parametrize('multiple_text_column', [False, True])
def test_compute_metrics(multiple_text_column, dataset_size, MultilabelDatasetTester):
    num_labels = 2
    train_labels = np.array(['ABC', 'DEF'])
    y_transformer = MultiLabelBinarizer(sparse_output=True)
    y_transformer.fit([[str(i) for i in range(num_labels)]])
    predictions = np.random.rand(5, len(train_labels))
    label_ids = np.fix(np.random.rand(5, len(train_labels)))
    metrics_dict, metrics_dict_with_thresholds = compute_metrics(predictions, label_ids, y_transformer)

    # Check extra metrics are not computed and no metrics are missed from computation
    comp_actual_metric_diff = set(metrics_dict.keys()).symmetric_difference(CLASSIFICATION_NLP_MULTILABEL_SET)
    assert len(comp_actual_metric_diff) == 0

    for metric_name in Metric.TEXT_CLASSIFICATION_MULTILABEL_PRIMARY_SET:
        assert metrics_dict[metric_name] is not None and metrics_dict[metric_name] >= 0.0

    assert metrics_dict_with_thresholds is not None
    expected_keys = sorted(['threshold', 'accuracy', 'f1_score_micro', 'f1_score_macro', 'f1_score_weighted',
                            'recall_micro', 'recall_macro', 'recall_weighted', 'precision_micro',
                            'precision_macro', 'precision_weighted', 'num_labels'])
    assert expected_keys == sorted(metrics_dict_with_thresholds.keys())
    for k, v in metrics_dict_with_thresholds.items():
        assert len(v) == 21


def test_change_label_col_format_happy_path():
    input_df = pd.DataFrame({"input_text_col": np.array(["Some input text!",
                                                         "Some more input text!",
                                                         "Yet more input text, much wow."]),
                             "labels": np.array(["lbl1", "", "lbl1,lbl2"])})
    change_label_col_format(input_df=input_df, label_col_name="labels")

    expected_input_df = input_df.copy()
    expected_input_df["labels"] = np.array(["['lbl1']", "[]", "['lbl1','lbl2']"])

    np.testing.assert_array_equal(expected_input_df.values, input_df.values)


def test_change_label_col_format_period_case():
    input_df = pd.DataFrame({"input_text_col": np.array(["Some input text!",
                                                         "Some more input text!",
                                                         "Yet more input text, huzzah!"]),
                             "labels": np.array(["google.com", "bing.com", "microsoft.com"])})
    change_label_col_format(input_df=input_df, label_col_name="labels")

    expected_input_df = input_df.copy()
    expected_input_df["labels"] = np.array(["['com','google']", "['bing','com']", "['com','microsoft']"])

    np.testing.assert_array_equal(expected_input_df.values, input_df.values)
