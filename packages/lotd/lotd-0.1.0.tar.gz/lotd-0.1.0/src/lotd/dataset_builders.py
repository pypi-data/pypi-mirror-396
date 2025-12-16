from typing import Union, Callable, Tuple
from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast
from datasets import load_dataset
from torch.utils.data import DataLoader
from .processors import ChatTokenizer
from .filters import LengthFilter
from .utils import load_cached, get_loaders
from .collators import PadCollator

"""
Pre-processing functions for some standard datasets
"""


def alpaca(
    tokenizer: Union[PreTrainedTokenizer, PreTrainedTokenizerFast],
    cache_path: Union[str, None] = None,
    max_length: int = 512,
    batch_size: int = 16,
    seed: int = 42,
    pre: Union[Callable, None] = None,
    post: Union[Callable, None] = None,
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Downloads and Pre-processes [Alpaca](https://huggingface.co/datasets/tatsu-lab/alpaca) dataset for instruction fine-tuning.



    Args:
        tokenizer: transformers tokenizer with `chat_template` parameter set.
        cache_path: path to load/save dataset.
        max_length: maximum sequence length for filter.
        batch_size: dataloaders batch size.
        seed: splitting and shuffling seed.
        pre: see `PadCollator`.
        post: see `PadCollator`.

    Returns:
        a tuple of train, validation and test dataloaders.
    """

    # Pre-process dataset
    def preprocess_alpaca():
        dataset_name = "tatsu-lab/alpaca"
        print(f"Loading {dataset_name} dataset (train split)...")
        ds = load_dataset(dataset_name, split="train")
        print("Shuffling dataset...")
        ds = ds.shuffle(seed=seed)
        print("Processing prompts...")
        ds = ds.map(
            lambda instructions, inputs: {
                "prompt": [
                    f"{instructions[i]}\n{inputs[i]}" if inputs[i] else instructions[i]
                    for i in range(len(instructions))
                ]
            },
            input_columns=["instruction", "input"],
            batched=True,
            batch_size=512,
        )
        print("Tokenization...")
        ds = ds.map(
            ChatTokenizer(tokenizer),
            input_columns=["prompt", "output"],
            batched=True,
            batch_size=512,
        )
        print("Filtering...")
        old_size = len(ds)  # type: ignore
        ds = ds.filter(
            LengthFilter(min_length=0, max_length=max_length),
            input_columns=["input_ids"],
            batched=True,
            batch_size=512,
        )
        new_size = len(ds)  # type: ignore
        print(
            f"{old_size - new_size} samples were removed ({(1.0-new_size/old_size)*100:.2f}%)"
        )
        return ds

    # Load from cache
    if cache_path != None:
        ds = load_cached(cache_path, preprocess_alpaca)
    else:
        ds = preprocess_alpaca()

    # Split and create dataloaders
    collate_fn = PadCollator(pad_id=tokenizer.pad_token_id, pre=pre, post=post)  # type: ignore

    # Return dataloaders
    return get_loaders(dataset=ds, collate_fn=collate_fn, batch_size=batch_size, seed=seed)  # type: ignore
