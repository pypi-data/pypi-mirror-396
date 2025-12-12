import builtins
import tempfile

import numpy as np
import os
import pandas as pd
import pickle
import pytest
import torch
import unittest

from unittest.mock import patch, mock_open, Mock

from sklearn.preprocessing import MultiLabelBinarizer

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.inference import inference
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InsufficientMemory
from azureml.automl.core.shared.constants import SCORING_FILE_PATH
from azureml.automl.core.shared.exceptions import ClientException, DataException, ResourceException
from azureml.automl.dnn.nlp.classification.multilabel.model_wrapper import ModelWrapper as MultilabelModelWrapper
from azureml.automl.dnn.nlp.classification.multiclass.model_wrapper import ModelWrapper as MulticlassModelWrapper
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import AutoNLPInternal, UnexpectedNERDataFormat
from azureml.automl.dnn.nlp.common._utils import (is_data_labeling_run_with_file_dataset,
                                                  save_script,
                                                  prepare_run_properties,
                                                  prepare_post_run_properties,
                                                  save_conda_yml,
                                                  save_deploy_script,
                                                  _get_language_code,
                                                  _get_input_example_dictionary,
                                                  _get_output_example,
                                                  get_unique_download_path,
                                                  calc_inter_eval_freq,
                                                  is_known_user_error,
                                                  scrub_system_exception)
from azureml.automl.dnn.nlp.common._data_utils import download_file_dataset
from azureml.automl.dnn.nlp.common.constants import (ModelNames,
                                                     Split,
                                                     SystemSettings,
                                                     TrainingInputLiterals)
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration
from azureml.automl.dnn.nlp.ner.model_wrapper import ModelWrapper as NERModelWrapper

from azureml.data import TabularDataset
from ..mocks import MockBertClass, MockRun

try:
    import mlflow
    has_mlflow = True
except ImportError:
    has_mlflow = False


class TestCommonFuncs:
    @pytest.mark.parametrize(
        'input,expected', [
            ('auto', 'eng'),
            ({"_dataset_language": "eng"}, 'eng'),
            ({"_dataset_language": "deu"}, 'deu'),
            ({"_dataset_language": "ita"}, 'ita')]
    )
    def test_language_recognition(self, input, expected):
        language = _get_language_code(input)
        assert language == expected

    @pytest.mark.parametrize(
        'file_to_save', ['some_file', 'score', 'score_script']
    )
    def test_save_script(self, file_to_save):
        mocked_file = mock_open(read_data='some file contents to write')
        with patch.object(builtins, 'open', mocked_file, create=True):
            save_script(file_to_save, "some_directory")

        assert mocked_file.call_count == 2
        mocked_file.assert_any_call(os.path.join("some_directory", file_to_save))
        mocked_file.assert_called_with(os.path.join("outputs", file_to_save), 'w')
        any('write(some file contents to write)' in str(call) for call in mocked_file()._mock_mock_calls)

    def test_prepare_run_properties(self):
        run = MockRun()
        prepare_run_properties(run, 'some_model')

        assert "runTemplate" in run.properties
        assert "run_algorithm" in run.properties
        assert run.properties['runTemplate'] == "automl_child"
        assert run.properties['run_algorithm'] == "some_model"

    def test_prepare_post_run_properties(self):
        run = MockRun()
        run._id = "some_run_id"
        with patch("azureml.automl.core.inference._get_model_name", return_value="some_model_id"):
            prepare_post_run_properties(run,
                                        "some_model_path",
                                        1234,
                                        "some_conda_file",
                                        'some_deploy_path',
                                        'accuracy',
                                        0.1234)

        artifact_path = "aml://artifact/ExperimentRun/dcid.some_run_id/"
        assert inference.AutoMLInferenceArtifactIDs.CondaEnvDataLocation in run.properties
        file_path = artifact_path + "some_conda_file"
        assert run.properties[inference.AutoMLInferenceArtifactIDs.CondaEnvDataLocation] == file_path

        assert inference.AutoMLInferenceArtifactIDs.ModelDataLocation in run.properties
        file_path = artifact_path + "some_model_path"
        assert run.properties[inference.AutoMLInferenceArtifactIDs.ModelDataLocation] == file_path

        assert inference.AutoMLInferenceArtifactIDs.ModelName in run.properties
        assert run.properties[inference.AutoMLInferenceArtifactIDs.ModelName] == "somerunid"

        assert inference.AutoMLInferenceArtifactIDs.ModelSizeOnDisk in run.properties
        assert run.properties[inference.AutoMLInferenceArtifactIDs.ModelSizeOnDisk] == 1234

        assert 'score' in run.properties
        assert run.properties['score'] == 0.1234

        assert 'primary_metric' in run.properties
        assert run.properties['primary_metric'] == "accuracy"

    def test_save_conda_yml(self):
        mocked_file = mock_open(read_data="name: project_environment")
        with patch.object(builtins, 'open', mocked_file, create=True) as yaml_file:
            save_conda_yml()

        output_file_contents = str(yaml_file().write.call_args_list)
        for item in inference.AutoMLNLPCondaPackagesList:
            assert item in output_file_contents
        for item in ['azureml-automl-dnn-nlp', 'inference-schema']:
            assert item in output_file_contents

    @pytest.mark.parametrize('run_source', ["automl", "Labeling"])
    @pytest.mark.parametrize('labeling_dataset_type', ["FileDataset", "TabularDataset", None])
    def test_is_data_labeling_run_with_file_dataset(self, run_source, labeling_dataset_type):
        mock_run = MockRun(
            run_source=run_source,
            label_column_name="label",
            labeling_dataset_type=labeling_dataset_type
        )
        result = is_data_labeling_run_with_file_dataset(mock_run)
        expected_result = True \
            if (run_source == SystemSettings.LABELING_RUNSOURCE
                and labeling_dataset_type == SystemSettings.LABELING_DATASET_TYPE_FILEDATSET) \
            else False
        assert result == expected_result

    def _mlflow_round_trip(self, model):
        with tempfile.TemporaryDirectory() as td:
            model_path = os.path.join(td, "model.pkl")
            with open(os.path.join(td, model_path), 'wb') as f:
                pickle.dump(model, f)

            mlflow_path = os.path.join(td, "mlflow_model")
            mlflow.pyfunc.save_model(path=mlflow_path,
                                     loader_module='azureml.automl.dnn.nlp',
                                     data_path=model_path,
                                     pip_requirements=[])
            return mlflow.pyfunc.load_model(mlflow_path)

    def _compare_models_mlflow(self, wrapped_model, mlflow_model):
        assert isinstance(mlflow_model, mlflow.pyfunc.PyFuncModel), \
            "MLflow model not parsed correctly."
        # This test is technically a little more brittle because we're making assumptions about MLflow.
        assert isinstance(mlflow_model._model_impl, type(wrapped_model)), \
            "Model has wrong type after MLflow round trip conversion."

        source_dnn = wrapped_model.model
        processed_dnn = mlflow_model._model_impl.model
        assert torch.equal(source_dnn.l1.weight, processed_dnn.l1.weight), \
            "Underlying DNN weights not preserved across MLflow conversion."

    @unittest.skipIf(not has_mlflow, "MLflow not present in current environment.")
    def test_mlflow_round_trip_multiclass(self):
        mock_tokenizer = Mock()
        mock_tokenizer.__reduce__ = lambda slf: (Mock, ())

        expected_prediction = np.random.rand(10, 10)
        with patch.object(MulticlassModelWrapper, "predict", return_value=expected_prediction):
            wrapped_model = MulticlassModelWrapper(model=MockBertClass(num_labels=2),
                                                   label_list=np.array(["positive", "negative"]),
                                                   tokenizer=mock_tokenizer,
                                                   training_configuration=TrainingConfiguration(
                                                       {"model_name": "bert-base-cased"}, _internal=True))

            mlflow_model = self._mlflow_round_trip(wrapped_model)
            self._compare_models_mlflow(wrapped_model, mlflow_model)

            np.testing.assert_array_equal(expected_prediction, mlflow_model.predict(np.empty(0)))

    @unittest.skipIf(not has_mlflow, "MLflow not present in current environment.")
    def test_mlflow_round_trip_multilabel(self):
        mock_component = Mock()
        mock_component.__reduce__ = lambda slf: (Mock, ())
        y_transformer = MultiLabelBinarizer()
        y_transformer.fit([["label0", "label1"]])

        expected_prediction = np.random.rand(10, 10)
        with patch.object(MultilabelModelWrapper, "predict", return_value=expected_prediction):
            wrapped_model = MultilabelModelWrapper(model=MockBertClass(num_labels=2),
                                                   tokenizer=mock_component,
                                                   training_configuration=TrainingConfiguration(
                                                       {"model_name": "bert-base-uncased"}, _internal=True),
                                                   y_transformer=y_transformer)

            mlflow_model = self._mlflow_round_trip(wrapped_model)
            self._compare_models_mlflow(wrapped_model, mlflow_model)

            np.testing.assert_array_equal(expected_prediction, mlflow_model.predict(np.empty(0)))

    @unittest.skipIf(not has_mlflow, "MLflow not present in current environment.")
    def test_mlflow_round_trip_ner(self):
        mock_tokenizer = Mock()
        mock_tokenizer.__reduce__ = lambda slf: (Mock, ())

        expected_prediction = np.random.rand(10, 10)
        with patch.object(NERModelWrapper, "predict", return_value=expected_prediction):
            wrapped_model = NERModelWrapper(model=MockBertClass(num_labels=2),
                                            label_list=["positive", "negative"],
                                            tokenizer=mock_tokenizer,
                                            training_configuration=TrainingConfiguration(
                                                {"model_name": "bert-base-cased"}, _internal=True))

            mlflow_model = self._mlflow_round_trip(wrapped_model)
            self._compare_models_mlflow(wrapped_model, mlflow_model)

            np.testing.assert_array_equal(expected_prediction, mlflow_model.predict(np.empty(0)))

    def test_get_input_example_directory(self):
        test_df = pd.DataFrame({"text": ["example sentence"], "label": ["some_label"]})
        example = _get_input_example_dictionary(test_df, "label")
        expected = "pd.DataFrame({\"text\": pd.Series([\"example_value\"], dtype=\"object\")})"
        assert example == expected

    def test_get_input_example_directory_multicolumn(self):
        test_df = pd.DataFrame(
            {"text1": ["example sentence1"],
             "text2": ["example sentence2"],
             "label": ["some_label"]})
        example = _get_input_example_dictionary(test_df, "label")
        expected = "pd.DataFrame({\"text1\": pd.Series([\"example_value\"], dtype=\"object\"), " + \
                   "\"text2\": pd.Series([\"example_value\"], dtype=\"object\")})"
        assert example == expected

    def test_get_output_example(self):
        test_df = pd.DataFrame({"text": ["example sentence"], "label": ["some_label"]})
        example = _get_output_example(test_df, "label")
        expected = "np.array([\"example_value\"])"
        assert example == expected

    def test_save_deploy_file(self):
        mocked_file = mock_open()
        script = "score_nlp_multiclass_v2.txt"
        input_example = "test_input_example"
        output_example = "test_output_example"
        with patch.object(builtins, 'open', mocked_file, create=True):
            save_deploy_script(script, input_example, output_example)
        mocked_file.assert_called_with(SCORING_FILE_PATH, 'w')

    @pytest.mark.parametrize(
        'rank, file_name', [
            (None, ModelNames.BERT_BASE_GERMAN_CASED),
            (0, ModelNames.BERT_BASE_UNCASED),
            (1, ModelNames.BERT_BASE_MULTILINGUAL_CASED)]
    )
    @patch("azureml.automl.dnn.nlp.common._utils.os")
    def test_get_unique_download_path(self, os_mock, rank, file_name):
        os_mock.environ = {}
        if rank:
            os_mock.environ["AZUREML_PROCESS_NAME"] = str(rank)
        get_unique_download_path(file_name)
        sub_dir = str(rank) if rank else "main"
        os_mock.path.join.assert_called_once()
        assert os_mock.path.join.call_args[0][0] == sub_dir
        assert os_mock.path.join.call_args[0][1] == file_name

    def test_download_file_dataset_tabular(self):
        tabular_dataset = Mock(spec=TabularDataset)
        with pytest.raises(DataException) as exc:
            download_file_dataset(tabular_dataset, Split.test, '')
        assert exc.value.error_code == UnexpectedNERDataFormat.__name__

    def test_calc_inter_eval_freq(self):
        training_configuration = TrainingConfiguration({TrainingInputLiterals.NUM_TRAIN_EPOCHS: 3,
                                                        TrainingInputLiterals.TRAIN_BATCH_SIZE: 32,
                                                        TrainingInputLiterals.GRADIENT_ACCUMULATION_STEPS: 1},
                                                       _internal=True)
        for dataset_length in (1e3, 1e4, 1e5):
            assert calc_inter_eval_freq(dataset_length, training_configuration) == 2000
        for dataset_length, expected_freq in [(1e6, 9375), (1e7, 93750), (1e8, 937500)]:
            assert calc_inter_eval_freq(dataset_length, training_configuration) == expected_freq

        training_configuration[TrainingInputLiterals.TRAIN_BATCH_SIZE] = 1
        assert calc_inter_eval_freq(1e4, training_configuration) == 3000

        training_configuration[TrainingInputLiterals.GRADIENT_ACCUMULATION_STEPS] = 2
        assert calc_inter_eval_freq(1e4, training_configuration) == 2000

    def test_is_known_user_error(self):
        known_user_error = ResourceException._with_error(
            AzureMLError.create(InsufficientMemory,
                                target="NLP-Training"))
        assert is_known_user_error(known_user_error)

        known_system_error = ClientException._with_error(
            AzureMLError.create(
                AutoNLPInternal,
                error_details="",
                traceback="",
                pii_safe_message="",
                target=""
            )
        )
        assert not is_known_user_error(known_system_error)

        assert not is_known_user_error(TypeError("An exception with a type external to the AML SDK."))

    def test_scrub_system_exception_only_wraps_system_errors(self):
        known_user_error = ResourceException._with_error(
            AzureMLError.create(InsufficientMemory,
                                target="NLP-Training"))
        scrubbed_exception = scrub_system_exception(known_user_error)
        assert scrubbed_exception == known_user_error  # Pass through

        system_error = ValueError("An exception with a type external to the AML SDK.")
        scrubbed_exception = scrub_system_exception(system_error)
        assert isinstance(scrubbed_exception, ClientException)
        assert scrubbed_exception.error_code == AutoNLPInternal.__name__
