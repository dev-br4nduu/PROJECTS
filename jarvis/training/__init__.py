"""
Training Pipeline — real model-weight training.

Two trainers:

  mlp_trainer.py  : a neural network trained FROM SCRATCH in numpy (explicit
                    forward pass, backprop, gradient descent). Runs on CPU with
                    zero heavy dependencies. Trains a real response-quality
                    classifier from captured feedback. This actually updates
                    weights via gradient descent — a genuine ML exercise that
                    runs in this environment right now.

  lora_finetune.py: a real LoRA/PEFT fine-tuning script for an open LLM
                    (transformers + peft + trl). Requires a GPU and model
                    access (HuggingFace). Documented for use in an environment
                    that has those — it does true LLM weight training.
"""
