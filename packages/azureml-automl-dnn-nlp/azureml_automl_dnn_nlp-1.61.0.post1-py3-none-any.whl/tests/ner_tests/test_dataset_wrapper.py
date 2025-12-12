import pytest
import transformers

from azureml.automl.dnn.nlp.common.constants import ModelNames, Split, TrainingDefaultSettings, TrainingInputLiterals
from azureml.automl.dnn.nlp.common.training_configuration import TrainingConfiguration
from azureml.automl.dnn.nlp.ner.io.read.dataset_wrapper import NerDatasetWrapper
from ..mocks import get_local_tokenizer


@pytest.mark.usefixtures('new_clean_dir')
class TestDatasetWrapper:
    @pytest.fixture(autouse=True)
    def _before_each(self):
        self.training_configuration = TrainingConfiguration(
            {TrainingInputLiterals.MAX_SEQ_LENGTH: TrainingDefaultSettings.DEFAULT_SEQ_LEN,
             TrainingInputLiterals.PADDING_STRATEGY: TrainingDefaultSettings.MAX_LENGTH,
             TrainingInputLiterals.MODEL_NAME: ModelNames.BERT_BASE_CASED},
            _internal=True)
        yield

    @pytest.mark.parametrize('split', [Split.train, Split.test, Split.valid])
    def test_dataset_with_labels(self, split, get_tokenizer):
        if split == Split.test:
            # Adding an unseen label to the test set, to confirm that it'll be handled gracefully
            data = "Commissioner O\nFranz B-PER\nFischler I-PER\n\nproposed O\nBritain B-ABC\n"
        else:
            data = "Commissioner O\nFranz B-PER\nFischler I-PER\n\nproposed O\nBritain B-LOC\n"
        max_seq_length = 20
        self.training_configuration[TrainingInputLiterals.MAX_SEQ_LENGTH] = max_seq_length
        test_dataset = NerDatasetWrapper(
            data=data,
            tokenizer=get_tokenizer,
            labels=["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"],
            training_configuration=self.training_configuration,
            mode=split
        )
        assert len(test_dataset) == 2
        # Even though the labels are ignored for test set, they should still not get appended to actual text.
        # The below assertions confirm that the tokenization of text data is agnostic to the inclusion of labels.
        assert test_dataset[0]['input_ids'].count(0) == 13
        assert test_dataset[1]['input_ids'].count(0) == 16
        for test_example in test_dataset:
            assert type(test_example) == transformers.tokenization_utils_base.BatchEncoding
            assert len(test_example.input_ids) == max_seq_length
            assert len(test_example.attention_mask) == max_seq_length
            assert len(test_example.token_type_ids) == max_seq_length
            assert len(test_example.label_ids) == max_seq_length
            assert any(i >= 0 for i in test_example.label_ids)

    def test_dataset_without_labels_for_test_input(self, get_tokenizer):
        data = "Commissioner\nFranz\nFischler\n\nproposed\nBritain\n"
        max_seq_length = 20
        self.training_configuration[TrainingInputLiterals.MAX_SEQ_LENGTH] = 20
        test_dataset = NerDatasetWrapper(
            data=data,
            tokenizer=get_tokenizer,
            labels=["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"],
            training_configuration=self.training_configuration,
            mode=Split.test
        )
        assert len(test_dataset) == 2
        for test_example in test_dataset:
            assert type(test_example) == transformers.tokenization_utils_base.BatchEncoding
            assert len(test_example.input_ids) == max_seq_length
            assert len(test_example.attention_mask) == max_seq_length
            assert len(test_example.token_type_ids) == max_seq_length
            assert len(test_example.label_ids) == max_seq_length
            assert any(i >= 0 for i in test_example.label_ids)

    def test_xlnet_label_construction_handles_padding(self):
        data = "Nick B-PER\nworks O\nat O\nMicrosoft B-ORG\n, O\nwhich O\nis O\na O\ngreat O\ncompany O\n. O\n"
        tokenizer = get_local_tokenizer(model_name=ModelNames.XLNET_BASE_CASED)
        labels = ["B-PER", "B-ORG", "O"]
        self.training_configuration[TrainingInputLiterals.MAX_SEQ_LENGTH] = 32
        self.training_configuration[TrainingInputLiterals.MODEL_NAME] = ModelNames.XLNET_BASE_CASED
        wrapped_data = NerDatasetWrapper(data=data,
                                         tokenizer=tokenizer,
                                         labels=labels,
                                         training_configuration=self.training_configuration,
                                         mode=Split.train)
        input_dict = wrapped_data[0].data
        # Tokenized, this should look like:
        expected_input_ids = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,  # Left-padded <pad> tokens.
                              4000, 1021, 38, 2491, 17, 19, 59, 27, 24, 312, 226, 17, 9, 4, 3]
        # Decoded, this translates back to:
        # <left padding> Nick works at Microsoft , which is a great company . <sep> <cls>
        expected_attention_mask = [0] * 17 + [1] * 15  # Ignore the left-padding (first 17 tokens); use the rest.
        expected_token_type_ids = [3] * 17 + [0] * 14 + [2]  # Pads, word tokens, then cls token.
        # Only the first token for each word is labeled; ignore (label id -100) all pads, seps, and cls tokens.
        expected_label_ids = [-100] * 17 + [0, 2, 2, 1, 2, -100, 2, 2, 2, 2, 2, 2, -100, -100, -100]

        assert input_dict['input_ids'] == expected_input_ids
        assert input_dict['attention_mask'] == expected_attention_mask
        assert input_dict['token_type_ids'] == expected_token_type_ids
        assert input_dict['label_ids'] == expected_label_ids

    def test_xlnet_label_construction_handles_truncation(self):
        data = "Anup B-PER\nmanages O\na O\nteam O\nat O\nMicrosoft B-ORG\nthat O\nworks O\non O\nNLP O\n. O\n"
        tokenizer = get_local_tokenizer(model_name=ModelNames.XLNET_BASE_CASED)
        labels = ["B-PER", "B-ORG", "O"]
        self.training_configuration[TrainingInputLiterals.MAX_SEQ_LENGTH] = 8
        self.training_configuration[TrainingInputLiterals.MODEL_NAME] = ModelNames.XLNET_BASE_CASED
        wrapped_data = NerDatasetWrapper(data=data,
                                         tokenizer=tokenizer,
                                         labels=labels,
                                         training_configuration=self.training_configuration,
                                         mode=Split.train)
        input_dict = wrapped_data[0].data
        # Tokenized, this should look like:
        expected_input_ids = [460, 499, 10031, 24, 230, 38, 4, 3]
        # Decoded, this translates back to: Anup manages a team at <sep> <cls>
        expected_attention_mask = [1] * 8
        expected_token_type_ids = [0] * 7 + [2]  # Only word tokens, then cls token at end.
        expected_label_ids = [0, -100, 2, 2, 2, 2, -100, -100]

        assert input_dict['input_ids'] == expected_input_ids
        assert input_dict['attention_mask'] == expected_attention_mask
        assert input_dict['token_type_ids'] == expected_token_type_ids
        assert input_dict['label_ids'] == expected_label_ids

    def test_xlnet_label_construction_handles_perfect_length(self):
        data = "Arjun B-PER\nis O\na O\ndata O\nscientist O\n"
        tokenizer = get_local_tokenizer(model_name=ModelNames.XLNET_BASE_CASED)
        labels = ["B-PER", "O"]
        self.training_configuration[TrainingInputLiterals.MAX_SEQ_LENGTH] = 8
        self.training_configuration[TrainingInputLiterals.MODEL_NAME] = ModelNames.XLNET_BASE_CASED
        wrapped_data = NerDatasetWrapper(data=data,
                                         tokenizer=tokenizer,
                                         labels=labels,
                                         training_configuration=self.training_configuration,
                                         mode=Split.train)
        input_dict = wrapped_data[0].data
        # Tokenized, this should look like:
        expected_input_ids = [1903, 10003, 27, 24, 527, 8388, 4, 3]
        # Decoded, this translates back to: Arjun is a data scientist <sep> <cls>
        expected_attention_mask = [1] * 8
        expected_token_type_ids = [0] * 7 + [2]
        expected_label_ids = [0, -100, 1, 1, 1, 1, -100, -100]

        assert input_dict['input_ids'] == expected_input_ids
        assert input_dict['attention_mask'] == expected_attention_mask
        assert input_dict['token_type_ids'] == expected_token_type_ids
        assert input_dict['label_ids'] == expected_label_ids

    def test_bert_label_construction_handles_padding(self):
        data = "Miseon B-PER\nis O\na O\ncoding O\nwizard O\n. O\n"
        tokenizer = get_local_tokenizer(model_name=ModelNames.BERT_BASE_CASED)
        labels = ["B-PER", "O"]
        self.training_configuration[TrainingInputLiterals.MAX_SEQ_LENGTH] = 16
        wrapped_data = NerDatasetWrapper(data=data,
                                         tokenizer=tokenizer,
                                         labels=labels,
                                         training_configuration=self.training_configuration,
                                         mode=Split.train)
        input_dict = wrapped_data[0].data
        # Tokenized, this should look like:
        expected_input_ids = [101, 12107, 2217, 1320, 1110, 170, 19350, 16678, 119, 102, 0, 0, 0, 0, 0, 0]
        # Decoded, this translates back to: [CLS] Miseon is a coding wizard. [SEP] [right padding]
        expected_attention_mask = [1] * 10 + [0] * 6
        expected_token_type_ids = [0] * 16
        expected_label_ids = [-100, 0, -100, -100, 1, 1, 1, 1, 1, -100, -100, -100, -100, -100, -100, -100]

        assert input_dict['input_ids'] == expected_input_ids
        assert input_dict['attention_mask'] == expected_attention_mask
        assert input_dict['token_type_ids'] == expected_token_type_ids
        assert input_dict['label_ids'] == expected_label_ids

    def test_bert_label_construction_handles_truncation(self):
        data = "Madhu B-PER\nis O\nvery O\nknowledgeable O\nabout O\nall O\nparts O\nof O\nthe O\nproduct O\n. O\n"
        tokenizer = get_local_tokenizer(model_name=ModelNames.BERT_BASE_CASED)
        labels = ["B-PER", "O"]
        self.training_configuration[TrainingInputLiterals.MAX_SEQ_LENGTH] = 8
        wrapped_data = NerDatasetWrapper(data=data,
                                         tokenizer=tokenizer,
                                         labels=labels,
                                         training_configuration=self.training_configuration,
                                         mode=Split.train)
        input_dict = wrapped_data[0].data
        # Tokenized this should look like:
        expected_input_ids = [101, 10779, 6583, 1110, 1304, 3044, 1895, 102]
        # Decoded, this translates to: [CLS] Madhu is very knowledgeable [SEP]
        expected_attention_mask = [1] * 8
        expected_token_type_ids = [0] * 8
        expected_label_ids = [-100, 0, -100, 1, 1, 1, -100, -100]

        assert input_dict['input_ids'] == expected_input_ids
        assert input_dict['attention_mask'] == expected_attention_mask
        assert input_dict['token_type_ids'] == expected_token_type_ids
        assert input_dict['label_ids'] == expected_label_ids

    def test_bert_label_construction_handles_perfect_length(self):
        data = "Ravi B-PER\nhas O\ntons O\nof O\nexperience O\n. O\n"
        tokenizer = get_local_tokenizer(model_name=ModelNames.BERT_BASE_CASED)
        labels = ["B-PER", "O"]
        self.training_configuration[TrainingInputLiterals.MAX_SEQ_LENGTH] = 8
        wrapped_data = NerDatasetWrapper(data=data,
                                         tokenizer=tokenizer,
                                         labels=labels,
                                         training_configuration=self.training_configuration,
                                         mode=Split.train)
        input_dict = wrapped_data[0].data
        # Tokenized this should look like:
        expected_input_ids = [101, 17968, 1144, 5606, 1104, 2541, 119, 102]
        # Decoded, this translates to: [CLS] Ravi has tons of experience. [SEP]
        expected_attention_mask = [1] * 8
        expected_token_type_ids = [0] * 8
        expected_label_ids = [-100, 0, 1, 1, 1, 1, 1, -100]

        assert input_dict['input_ids'] == expected_input_ids
        assert input_dict['attention_mask'] == expected_attention_mask
        assert input_dict['token_type_ids'] == expected_token_type_ids
        assert input_dict['label_ids'] == expected_label_ids
