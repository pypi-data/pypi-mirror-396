from unittest.mock import patch

import pytest

from azureml.automl.core.shared.exceptions import ClientException, UserException
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import DetectedVnetIssue
from azureml.automl.dnn.nlp.common._resource_path_resolver import ResourcePathResolver
from azureml.automl.dnn.nlp.common.constants import ModelNames
from azureml.automl.runtime.featurizer.transformer.data.word_embeddings_info import EmbeddingInfo


class TestResourcePathResolver:
    @pytest.mark.parametrize(
        'dataset_language, expected', [
            ('eng', ModelNames.BERT_BASE_CASED),
            ('deu', ModelNames.BERT_BASE_GERMAN_CASED),
            ('ita', ModelNames.BERT_BASE_MULTILINGUAL_CASED),
            ('ENG', ModelNames.BERT_BASE_CASED),
            ('english', ModelNames.BERT_BASE_MULTILINGUAL_CASED),
            ('', ModelNames.BERT_BASE_MULTILINGUAL_CASED),
            ('DEU', ModelNames.BERT_BASE_GERMAN_CASED),
            ('Deu', ModelNames.BERT_BASE_GERMAN_CASED)])
    def test_rpr_model_retrieval(self, dataset_language, expected):
        rpr = ResourcePathResolver(dataset_language=dataset_language, is_multilabel_training=False)
        assert rpr.model_name == expected

    def test_rpr_cdn_return_none(self):
        with patch("azureml.automl.dnn.nlp.common._resource_path_resolver.ResourcePathResolver._download_model",
                   return_value=None):
            rpr = ResourcePathResolver(dataset_language="some_language", is_multilabel_training=False)
            assert rpr.model_path is None

    @patch("azureml.automl.runtime.network_compute_utils.get_cluster_name", return_value="test_cluster_name")
    @patch("azureml.automl.runtime.network_compute_utils.get_vnet_name", return_value="test_vnet_name")
    @patch("azureml.automl.dnn.nlp.common._resource_path_resolver.AutoMLPretrainedDNNProvider.get_model_dirname",
           side_effect=ClientException())
    def test_rpr_raises_on_cdn_failure_vnet(self, mock_fetch_model, test_vnet_name, test_clustern_name):
        with pytest.raises(UserException) as exc:
            rpr = ResourcePathResolver()
            rpr.model_path
        assert exc.value.error_code == DetectedVnetIssue.__name__

    @pytest.mark.parametrize(
        'input_language, input_multilabel, embedding_name, model_name', [
            ('eng', True, EmbeddingInfo.BERT_BASE_UNCASED_AUTONLP_3_1_0, ModelNames.BERT_BASE_UNCASED),
            ('eng', False, EmbeddingInfo.BERT_BASE_CASED, ModelNames.BERT_BASE_CASED),
            ('deu', False, EmbeddingInfo.BERT_BASE_GERMAN_CASED_AUTONLP_3_1_0,
             ModelNames.BERT_BASE_GERMAN_CASED),
            ('ita', False, EmbeddingInfo.BERT_BASE_MULTLINGUAL_CASED_AUTONLP_3_1_0,
             ModelNames.BERT_BASE_MULTILINGUAL_CASED)])
    def test_rpr_get_path(self, input_language, input_multilabel, embedding_name, model_name):
        mock_path = "azureml.automl.dnn.nlp.common._resource_path_resolver.AutoMLPretrainedDNNProvider"
        with patch(mock_path) as mock_provider:
            rpr = ResourcePathResolver(input_language, input_multilabel)
            assert rpr.model_name == model_name
            assert rpr._embedded_model_name == embedding_name
            rpr.model_path
            assert mock_provider.call_args[0][0] == embedding_name

    def test_rpr_with_model(self):
        rpr = ResourcePathResolver(dataset_language="mul", model_name="bert-base-cased")
        # Even though language code "mul" is specified, which would cause bert multilingual to get downloaded
        # by default, since we've specified bert-base-cased, that will be used instead.
        assert rpr.model_name == "bert-base-cased"
