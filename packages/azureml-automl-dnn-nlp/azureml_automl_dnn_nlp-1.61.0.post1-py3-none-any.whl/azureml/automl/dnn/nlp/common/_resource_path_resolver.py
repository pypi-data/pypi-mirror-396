# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Path resolver for config, tokenizer and model."""
from typing import Optional
from urllib.parse import urljoin

import logging
import os

from azureml.automl.core._downloader import Downloader
from azureml.automl.core.automl_utils import get_automl_resource_url
from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.dnn.nlp.common._utils import Singleton, get_unique_download_path, intercept_vnet_failures
from azureml.automl.dnn.nlp.common.constants import ModelNames
from azureml.automl.runtime.featurizer.transformer.data.automl_textdnn_provider import AutoMLPretrainedDNNProvider
from azureml.automl.runtime.featurizer.transformer.data.word_embeddings_info import EmbeddingInfo

BASE_URL = urljoin(get_automl_resource_url(), "nlp-pretrained/")
TOKENIZER_ZIP = 'tokenizer.zip'
ZIP_FILE_PREFIX = 'azureml_automl_nlp'
_logger = logging.getLogger(__name__)

MODEL_TO_EMBEDDING_MAPPING = {
    ModelNames.BERT_BASE_CASED: EmbeddingInfo.BERT_BASE_CASED,
    ModelNames.BERT_BASE_UNCASED: EmbeddingInfo.BERT_BASE_UNCASED_AUTONLP_3_1_0,
    ModelNames.BERT_BASE_MULTILINGUAL_CASED: EmbeddingInfo.BERT_BASE_MULTLINGUAL_CASED_AUTONLP_3_1_0,
    ModelNames.BERT_BASE_GERMAN_CASED: EmbeddingInfo.BERT_BASE_GERMAN_CASED_AUTONLP_3_1_0,
    ModelNames.BERT_LARGE_CASED: EmbeddingInfo.BERT_LARGE_CASED,
    ModelNames.BERT_LARGE_UNCASED: EmbeddingInfo.BERT_LARGE_UNCASED,
    ModelNames.DISTILBERT_BASE_CASED: EmbeddingInfo.DISTILBERT_BASE_CASED,
    ModelNames.DISTILBERT_BASE_UNCASED: EmbeddingInfo.DISTILBERT_BASE_UNCASED,
    ModelNames.ROBERTA_BASE: EmbeddingInfo.ROBERTA_BASE,
    ModelNames.ROBERTA_LARGE: EmbeddingInfo.ROBERTA_LARGE,
    ModelNames.DISTILROBERTA_BASE: EmbeddingInfo.DISTILROBERTA_BASE,
    ModelNames.XLM_ROBERTA_BASE: EmbeddingInfo.XLM_ROBERTA_BASE,
    ModelNames.XLM_ROBERTA_LARGE: EmbeddingInfo.XLM_ROBERTA_LARGE,
    ModelNames.XLNET_BASE_CASED: EmbeddingInfo.XLNET_BASE_CASED,
    ModelNames.XLNET_LARGE_CASED: EmbeddingInfo.XLNET_LARGE_CASED
}


class ResourcePathResolver:
    """
    Singleton for resolving resource paths necessary for NLP training. Includes default model/path selection logic.
    All resources should be hosted in our Azure CDN. We first try to download from this CDN (see BASE_URL above)
    and fallback to their public equivalents hosted by HuggingFace.
    """
    __metaclass__ = Singleton

    def __init__(self,
                 dataset_language: str = "eng",
                 is_multilabel_training: bool = False,
                 model_name: Optional[str] = None):
        """
        Initializer for ResourcePathResolver. This is only called upon the first instantiation. All other instances of
        instantiation return that first object.

        :param model_name: the name of the model to be used for the training procedure.
        :param dataset_language: user-inputted language from FeaturizationConfig.
        :param is_multilabel_training: whether this is the multilabel task or not.
        :return: None.
        """
        if model_name is None:
            if dataset_language.lower() == "eng":
                self._model_name = \
                    ModelNames.BERT_BASE_UNCASED if is_multilabel_training else ModelNames.BERT_BASE_CASED
            elif dataset_language.lower() == "deu":
                self._model_name = ModelNames.BERT_BASE_GERMAN_CASED
            else:
                self._model_name = ModelNames.BERT_BASE_MULTILINGUAL_CASED
        else:
            self._model_name = model_name
        self._embedded_model_name = MODEL_TO_EMBEDDING_MAPPING[self._model_name]

        # Attributes to be set by properties later
        self._model_path = None      # type: Optional[str]
        self._tokenizer_config_path = None  # type: Optional[str]

    @property
    def model_name(self) -> str:
        """
        Property returns model to use
        :return: model name
        """
        return self._model_name

    @property
    def config_path(self) -> str:
        """
        Property returns config path
        :return: config path
        """
        # Config is zipped in same folder along with tokenizer and is required to load tokenizer.
        if self._tokenizer_config_path is None:
            self._download_tokenizer_and_config()
        return self._tokenizer_config_path

    @property
    def model_path(self) -> str:
        """
        Property returns model path
        :return: model path
        """
        if self._model_path is None:
            self._download_model()
        if self._model_path is None:
            _logger.warning(f"Failed to download {self.model_name} from CDN.")
        else:
            _logger.info(f"Downloaded {self.model_name} to '{self._model_path}'.")
        return self._model_path

    @property
    def tokenizer_path(self) -> str:
        """
        Property returns tokenizer path that has the tokenizer downloaded from CDN
        :return: tokenizer path
        """
        if self._tokenizer_config_path is None:
            self._download_tokenizer_and_config()
        return self._tokenizer_config_path

    @intercept_vnet_failures(extra_errors=[ClientException])
    def _download_model(self):
        """Download the model"""
        provider = AutoMLPretrainedDNNProvider(self._embedded_model_name)
        self._model_path = provider.get_model_dirname()

    def _download_tokenizer_and_config(self):
        """Download and extract the tokenizer and config artifacts."""
        download_prefix = BASE_URL + self._model_name + "/"
        download_type = constants.TelemetryConstants.CDN_DOWNLOAD
        with log_utils.log_activity(
                _logger,
                activity_name=f"{download_type}_{self._model_name}"
        ):
            local_path = get_unique_download_path('tokenizer')
            pid = str(os.getpid())
            download_path = os.path.join(os.path.realpath(os.path.curdir), 'pid', pid, local_path)
            if not os.path.isdir(download_path):
                os.makedirs(download_path)
            try:
                downloaded_file = Downloader.download(download_prefix=download_prefix,
                                                      file_name=TOKENIZER_ZIP,
                                                      target_dir=download_path,
                                                      prefix=ZIP_FILE_PREFIX)

                if os.path.exists(downloaded_file):
                    Downloader.unzip_file(zip_fname=downloaded_file, extract_path=download_path)
                    _logger.info(f"Downloaded tokenizer for {self._model_name} "
                                 f"from CDN {download_prefix}/{TOKENIZER_ZIP}.")
                    self._tokenizer_config_path = download_path
                else:
                    _logger.warning(f"Missing tokenizer downloaded file '{downloaded_file}'.")
            except Exception as e:
                _logger.warning(f"Download for tokenizer failed with error: {e}")
