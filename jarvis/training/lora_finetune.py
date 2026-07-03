"""
LoRA Fine-Tuning — real LLM weight training on an open model.

This trains actual transformer weights (via low-rank adapters) on the
preference/conversation data JARVIS collects. Unlike the Claude API — whose
weights you cannot touch — an open model (Llama, Mistral, Qwen, Phi, etc.) can
be genuinely fine-tuned to internalize your style and preferences.

REQUIREMENTS (not available in a network-restricted / CPU-only sandbox):
  - a GPU (LoRA on a 1-7B model needs ~8-24 GB VRAM)
  - model access: `pip install transformers peft trl bitsandbytes accelerate`
  - ability to download the base model (HuggingFace Hub reachable)

Two modes:
  - SFT  (supervised fine-tuning): learn from good (prompt, response) pairs
  - DPO  (preference optimization): learn to prefer `chosen` over `rejected`
         using the preference pairs the FeedbackStore produces from corrections.

Run:
  python -m jarvis.training.lora_finetune --mode sft  --data jarvis_data/dataset_classification.jsonl
  python -m jarvis.training.lora_finetune --mode dpo  --data jarvis_data/dataset_preference.jsonl

This file is intentionally standalone and dependency-guarded: importing it
never fails, so the rest of JARVIS runs even where these libraries are absent.
It only requires the heavy stack when you actually call run_sft()/run_dpo().
"""

from __future__ import annotations
from typing import Optional, List, Dict
import json
import argparse


DEFAULT_BASE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"  # small enough for modest GPUs


def _check_deps():
    """Import the heavy training stack, with a clear error if it's missing."""
    try:
        import torch  # noqa
        import transformers  # noqa
        import peft  # noqa
        import trl  # noqa
        return True
    except ImportError as e:
        raise ImportError(
            "LoRA fine-tuning needs a GPU training stack that isn't installed "
            "here. Install it in a GPU environment:\n"
            "  pip install torch transformers peft trl bitsandbytes accelerate datasets\n"
            f"(missing: {e.name})"
        )


def _load_sft_dataset(path: str):
    """Load classification/conversation JSONL into a chat-format HF dataset."""
    from datasets import Dataset
    rows = []
    with open(path) as f:
        for line in f:
            row = json.loads(line)
            # Only train on positively-rated exchanges for SFT.
            if row.get("label") and row["label"] != "positive":
                continue
            text = row.get("text", "")
            rows.append({"text": text})
    return Dataset.from_list(rows)


def _load_dpo_dataset(path: str):
    """Load preference pairs (prompt, chosen, rejected) into an HF dataset."""
    from datasets import Dataset
    rows = []
    with open(path) as f:
        for line in f:
            row = json.loads(line)
            rows.append({
                "prompt": row["prompt"],
                "chosen": row["chosen"],
                "rejected": row["rejected"],
            })
    return Dataset.from_list(rows)


def _lora_config():
    from peft import LoraConfig
    return LoraConfig(
        r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )


def run_sft(data_path: str, base_model: str = DEFAULT_BASE_MODEL,
            output_dir: str = "jarvis_data/lora_sft", epochs: int = 3):
    """Supervised LoRA fine-tuning on positively-rated conversations."""
    _check_deps()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import SFTTrainer, SFTConfig

    tokenizer = AutoTokenizer.from_pretrained(base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(base_model, device_map="auto")

    dataset = _load_sft_dataset(data_path)
    config = SFTConfig(output_dir=output_dir, num_train_epochs=epochs,
                       per_device_train_batch_size=2,
                       gradient_accumulation_steps=4, learning_rate=2e-4,
                       logging_steps=10, save_strategy="epoch",
                       max_seq_length=512)

    trainer = SFTTrainer(model=model, train_dataset=dataset,
                         peft_config=_lora_config(), args=config,
                         tokenizer=tokenizer)
    trainer.train()
    trainer.save_model(output_dir)
    return {"status": "trained", "mode": "sft", "output_dir": output_dir,
            "examples": len(dataset)}


def run_dpo(data_path: str, base_model: str = DEFAULT_BASE_MODEL,
            output_dir: str = "jarvis_data/lora_dpo", epochs: int = 3):
    """Direct Preference Optimization on (chosen > rejected) pairs."""
    _check_deps()
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import DPOTrainer, DPOConfig

    tokenizer = AutoTokenizer.from_pretrained(base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(base_model, device_map="auto")

    dataset = _load_dpo_dataset(data_path)
    config = DPOConfig(output_dir=output_dir, num_train_epochs=epochs,
                       per_device_train_batch_size=2,
                       gradient_accumulation_steps=4, learning_rate=5e-5,
                       logging_steps=10, save_strategy="epoch", beta=0.1)

    trainer = DPOTrainer(model=model, args=config, train_dataset=dataset,
                         processing_class=tokenizer, peft_config=_lora_config())
    trainer.train()
    trainer.save_model(output_dir)
    return {"status": "trained", "mode": "dpo", "output_dir": output_dir,
            "examples": len(dataset)}


def main():
    parser = argparse.ArgumentParser(description="LoRA fine-tune an open LLM on JARVIS data")
    parser.add_argument("--mode", choices=["sft", "dpo"], required=True)
    parser.add_argument("--data", required=True, help="path to JSONL dataset")
    parser.add_argument("--base-model", default=DEFAULT_BASE_MODEL)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--epochs", type=int, default=3)
    args = parser.parse_args()

    if args.mode == "sft":
        out = args.output_dir or "jarvis_data/lora_sft"
        result = run_sft(args.data, args.base_model, out, args.epochs)
    else:
        out = args.output_dir or "jarvis_data/lora_dpo"
        result = run_dpo(args.data, args.base_model, out, args.epochs)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
