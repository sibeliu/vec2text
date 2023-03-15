import pytest
import shlex

import datasets
import transformers

from run_args import ModelArguments, DataTrainingArguments, TrainingArguments
from run_helpers import trainer_from_args
from trainer import InversionTrainer

DEFAULT_ARGS_STR = '--per_device_train_batch_size 32 --max_seq_length 128 --model_name_or_path t5-small --embedding_model_name dpr --num_repeat_tokens 32 --exp_name test-exp-123'
DEFAULT_ARGS = shlex.split(DEFAULT_ARGS_STR)

DEFAULT_ARGS += ['--use_wandb', '0']
DEFAULT_ARGS += ['--fp16', '1']

@pytest.fixture
def trainer() -> InversionTrainer:
    parser = transformers.HfArgumentParser((ModelArguments, DataTrainingArguments, TrainingArguments))
    model_args, data_args, training_args = parser.parse_args_into_dataclasses(args=DEFAULT_ARGS)
    ########################################################
    training_args.num_train_epochs = 1.0
    training_args.eval_steps = 4
    trainer = trainer_from_args(
        model_args=model_args, 
        data_args=data_args, 
        training_args=training_args
    )
    # make datasets smaller...
    trainer.train_dataset = trainer.train_dataset.select(range(256))
    trainer.eval_dataset = trainer.eval_dataset.select(range(64))
    ########################################################
    return trainer

def test_trainer(trainer):
    train_result = trainer.train(resume_from_checkpoint=None)
    metrics = train_result.metrics
    print("metrics:", metrics)