import importlib
import unittest
import pytest
import torch
from unittest.mock import MagicMock, patch
from transformers.training_args import TrainingArguments
from azureml.automl.dnn.nlp.common.distributed_trainer import (
    DistributedTrainer,
    DistributedTrainingArguments
)
from torch.utils.data.distributed import DistributedSampler


horovod_spec = importlib.util.find_spec("horovod")
has_horovod = horovod_spec is not None


class TestDistributedTrainingArgsTests:

    @unittest.skipIf(not has_horovod, "Horovod not installed")
    @patch("torch.cuda.set_device")
    @patch("horovod.torch.init")
    @patch("horovod.torch.local_rank")
    def test_setup_devices(self, local_rank_mock, init_mock, set_device_mock):

        init_mock.return_value = None
        local_rank_mock.return_value = 0
        args = TrainingArguments(
            output_dir="some_dir",
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            num_train_epochs=1,
            save_strategy="no",
            gradient_accumulation_steps=1,
            logging_strategy="no",
            report_to="none"
        )
        distr_args = DistributedTrainingArguments(args)
        assert distr_args._setup_devices == torch.device("cuda", 0)
        assert set_device_mock.call_count == 1
        assert distr_args.distributed_state is None


class TestDistributedTrainerTests:

    @unittest.skipIf(not has_horovod, "Horovod not installed")
    @patch("torch.cuda.set_device")
    @patch("horovod.torch.broadcast_optimizer_state")
    @patch("horovod.torch.broadcast_parameters")
    @patch("horovod.torch.init")
    @patch("horovod.torch.local_size")
    @patch("horovod.torch.local_rank")
    def test_trainer(self, local_rank_mock, local_size_mock, init_mock, param_mock, optim_mock, set_device_mock):
        init_mock.return_value = None
        local_size_mock.return_value = 2
        local_rank_mock.return_value = 0

        args = TrainingArguments(
            output_dir="some_dir",
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            num_train_epochs=1,
            save_strategy="no",
            gradient_accumulation_steps=1,
            logging_strategy="no",
            report_to="none"
        )
        training_args = DistributedTrainingArguments(args)
        DistributedTrainer(model=torch.nn.Module(),
                           args=training_args,
                           train_dataset=MagicMock(),
                           tokenizer=MagicMock(),
                           data_collator=MagicMock())
        init_mock.assert_called_once()
        param_mock.asert_called_once()

    @unittest.skipIf(not has_horovod, "Horovod not installed")
    @patch("torch.cuda.set_device")
    @patch("horovod.torch.DistributedOptimizer")
    @patch("horovod.torch.broadcast_optimizer_state")
    @patch("horovod.torch.broadcast_parameters")
    @patch("horovod.torch.init")
    @patch("horovod.torch.size")
    @patch("horovod.torch.rank")
    @patch("horovod.torch.local_size")
    @patch("horovod.torch.local_rank")
    @pytest.mark.parametrize('gradient_accumulation_steps', [1, 2])
    def test_optimizer(self, local_rank_mock, local_size_mock, rank_mock, size_mock, init_mock,
                       param_mock, optim_mock, dist_optim_mock, set_device_mock, gradient_accumulation_steps):
        init_mock.return_value = None
        local_size_mock.return_value = 2
        local_rank_mock.return_value = 0
        rank_mock.return_value = 0
        size_mock.return_value = 4

        args = TrainingArguments(
            output_dir="some_dir",
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            num_train_epochs=1,
            save_strategy="no",
            gradient_accumulation_steps=gradient_accumulation_steps,
            logging_strategy="no",
            report_to="none"
        )
        training_args = DistributedTrainingArguments(args)
        trainer = DistributedTrainer(model=torch.nn.Module(),
                                     args=training_args,
                                     train_dataset=MagicMock(),
                                     tokenizer=MagicMock(),
                                     data_collator=MagicMock())
        trainer.create_optimizer()
        optim_mock.assert_called_once()

        sampler = trainer._get_train_sampler(MagicMock())
        assert type(sampler) is DistributedSampler

        dist_optim_mock.assert_called_once()
        if (gradient_accumulation_steps == 1):
            assert dist_optim_mock.call_args[1]['backward_passes_per_step'] == 1
        else:
            assert dist_optim_mock.call_args[1]['backward_passes_per_step'] == 3
