import os
import math
from pathlib import Path
from datasets import Dataset, DatasetDict
from sklearn.model_selection import train_test_split
import pandas as pd
from typing import Dict, List, Callable, Optional, Union

# Local application
from ml_trainer.base import BaseDataset, AbstractModelArchitecture
from ml_trainer.trainer import BaseTrainer
from ml_trainer.tasks.task_factory import AbstractTaskFactory
from ml_trainer.utils.metrics import LLMFinetuneMetrics
from ml_trainer.utils.logger import BaseLogger


class LLMFineTuningDataset(BaseDataset):
    """
    Flexible dataset loader / formatter.

    Expected dataset config (example):
    dataset_config = {
        "source": "/path/to/file.json",   # or DataFrame, or dict with 'train'/'test'
        "format_fn": optional_callable,   # function(row) -> List[{"role","content"}]
        "test_size": 0.1,
        "random_state": 42,
    }

    Behavior:
    - If `format_fn` provided, use it to convert each row -> messages.
    - Else, accept rows that already have 'messages'.
    """

    def __init__(
        self,
        tokenizer,
        system_prompt: str = None,
        config: Optional[dict] = None,
        **kwargs,
    ):
        self.tokenizer = tokenizer  # Must have apply_chat_template method
        self.system_prompt = system_prompt or "You are a helpful assistant."
        self.config = config or {}
        super().__init__(config=self.config, **kwargs)

        # Extract config values
        if "source" not in self.config:
            raise ValueError("config must contain 'source' key")

        self.data_source = self.config["source"]
        self.test_size = self.config.get(
            "test_size", None
        )  # Optional - if None, no split
        # Handle format function behavior
        self.format_fn = self.config.get("format_fn", None)

        # If user passes "default" or None, we will infer automatically later
        if isinstance(self.format_fn, str):
            if self.format_fn.lower() == "default":
                self.format_fn = self._default_format_fn
                print("Applying the default format function")
            else:
                raise ValueError(f"Unknown format function name: {self.format_fn}")
        
        # Added for metrics
        # self.dataset = self.load_dataset()

    def _load_raw_data(self) -> pd.DataFrame:
        """Load data from various sources"""
        # Pandas DataFrame -> return as-is (handled downstream)
        if isinstance(self.data_source, pd.DataFrame):
            return self.data_source

        # HuggingFace DatasetDict -> normalize to dict of record-lists
        if isinstance(self.data_source, DatasetDict):
            normalized = {}
            for split, ds in self.data_source.items():
                # convert each dataset split to list of dict records
                normalized[split] = [dict(r) for r in ds]
            return normalized

        # Single HuggingFace Dataset -> treat as 'train' split
        if isinstance(self.data_source, Dataset):
            return {"train": [dict(r) for r in self.data_source]}

        # If user passed a plain list of records (already formatted), treat as train
        if isinstance(self.data_source, list):
            return {"train": self.data_source}

        # If a dict was passed, normalize any Dataset/DataFrame values inside
        if isinstance(self.data_source, dict):
            normalized = {}
            for k, v in self.data_source.items():
                if isinstance(v, Dataset):
                    normalized[k] = [dict(r) for r in v]
                elif isinstance(v, pd.DataFrame):
                    normalized[k] = v.to_dict("records")
                elif isinstance(v, list):
                    normalized[k] = v
                else:
                    # keep as-is (caller may handle)
                    normalized[k] = v
            return normalized
        elif isinstance(self.data_source, (str, Path)):
            path = Path(self.data_source)
            if path.suffix == ".json":
                return pd.read_json(path)
            elif path.suffix == ".jsonl":
                return pd.read_json(path, lines=True)
            elif path.suffix == ".csv":
                return pd.read_csv(path)
            elif path.suffix == ".parquet":
                return pd.read_parquet(path)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
        else:
            raise ValueError(f"Unsupported data_source type: {type(self.data_source)}")

    def _apply_chat_template(
        self, messages: List[Dict], include_assistant: bool = True
    ) -> str:
        """Apply tokenizer's chat template to messages"""
        # Add system prompt if provided and not already in messages
        if self.system_prompt and (not messages or messages[0]["role"] != "system"):
            messages = [{"role": "system", "content": self.system_prompt}] + messages

        return self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=not include_assistant
        )

    def _default_format_fn(self, row: dict):
        """Default format function for (instruction, response) datasets"""
        if "instruction" in row and "response" in row:
            return [
                {"role": "user", "content": row["instruction"]},
                {"role": "assistant", "content": row["response"]},
            ]
        else:
            raise ValueError(
                "Default format function expects columns 'instruction' and 'response'. "
                f"Got keys: {list(row.keys())}"
            )

    def load_dataset(self) -> Dict[str, Dataset]:
        """Load and format dataset"""
        raw_data = self._load_raw_data()

        # Handle pre-split data
        if isinstance(raw_data, dict) and "train" in raw_data:
            train_data = raw_data["train"]
            test_data = raw_data.get("test", [])
        else:
            # Split the data
            if isinstance(raw_data, pd.DataFrame):
                if self.test_size is None:
                    train_data = raw_data.to_dict("records")
                    test_data = []
                else:
                    train_df, test_df = train_test_split(
                        raw_data,
                        test_size=self.test_size,
                        random_state=self.config.get("random_state", 42),
                    )
                    train_data = train_df.to_dict("records")
                    test_data = test_df.to_dict("records")

            else:
                raise ValueError("Data must be DataFrame or dict with train/test keys")

        # Format training data (with assistant responses)
        train_texts = []
        for item in train_data:
            # If format_fn provided, use it to convert to messages
            if self.format_fn:
                messages = self.format_fn(item)
            else:
                # Assume data already has 'messages' key in standard format
                if "messages" not in item:
                    raise ValueError(
                        "Data must have 'messages' key with standard format, "
                        "or you must provide a 'format_fn' to convert your data. "
                        f"Got keys: {list(item.keys())}"
                    )
                messages = item["messages"]

            formatted = self._apply_chat_template(messages, include_assistant=True)
            train_texts.append(formatted)

        # Format test data (without assistant responses for generation)
        test_texts = []
        for item in test_data:
            # If format_fn provided, use it to convert to messages
            if self.format_fn:
                messages = self.format_fn(item)
            else:
                # Assume data already has 'messages' key
                if "messages" not in item:
                    raise ValueError(
                        "Data must have 'messages' key with standard format, "
                        "or you must provide a 'format_fn' to convert your data. "
                        f"Got keys: {list(item.keys())}"
                    )
                messages = item["messages"]

            # Remove assistant message for inference
            messages_no_assist = [m for m in messages if m["role"] != "assistant"]
            formatted = self._apply_chat_template(
                messages_no_assist, include_assistant=False
            )
            test_texts.append(formatted)

        self.formatted_dataset = {
            "train": Dataset.from_dict({"text": train_texts}),
            "test": Dataset.from_dict({"text": test_texts}),
        }
        return self.formatted_dataset
    
    # #Added for metrics
    # def get_dataset(self):
    #     """Get the loaded dataset"""
    #     return self.dataset


class LLMModel(AbstractModelArchitecture):
    def __init__(self, model_name, config=None):
        self.config = config
        self.model_name = model_name or self.config.get("model_name")

        self._model_loaded = False

        # # LoRA settings
        self.setup_lora_flag = self.config.get("setup_lora", True)
        self.lora_r = self.config.get("lora_r", 16)
        self.lora_alpha = self.config.get("lora_alpha", 16)

        # Internal state
        self.model = None
        self.tokenizer = None

    def _load_model_if_needed(self):
        """Load model only once when needed"""
        from unsloth import FastLanguageModel, is_bfloat16_supported

        if not self._model_loaded:
            print(f"Loading model from {self.model_name}...")

            # Load base model
            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name=self.model_name,
                max_seq_length=self.config.get("max_seq_length", 2048),
                dtype=self.config.get("dtype", "bfloat16"),
                load_in_4bit=self.config.get("load_in_4bit", False),
                full_finetuning=self.config.get("full_finetuning", False),
                # load_in_8bit=self.config.get("load_in_8bit", False),
            )
            print(
                f"Model loaded with device map: {getattr(self.model, 'hf_device_map', 'Unknown')}"
            )

            # Setup LoRA if requested
            if self.setup_lora_flag:
                self.setup_lora()

            self._model_loaded = True

    def setup_lora(self):
        """Setup LoRA fine-tuning"""
        from unsloth import FastLanguageModel

        if self.model is None:
            raise ValueError("Model not loaded yet")

        print("Setting up LoRA fine-tuning...")
        self.model = FastLanguageModel.get_peft_model(
            self.model,
            r=self.config.get("lora_r", 16),
            target_modules=self.config.get(
                "lora_target_modules",
                [
                    "q_proj",
                    "k_proj",
                    "v_proj",
                    "o_proj",
                    "gate_proj",
                    "up_proj",
                    "down_proj",
                ],
            ),
            lora_alpha=self.config.get("lora_alpha", 16),
            lora_dropout=self.config.get("lora_dropout", 0),
            bias=self.config.get("lora_bias", "none"),
            use_gradient_checkpointing=self.config.get(
                "use_gradient_checkpointing", "unsloth"
            ),
            random_state=self.config.get("random_state", 3407),
            use_rslora=self.config.get("use_rslora", False),
            loftq_config=self.config.get("loftq_config", None),
            # fan_in_fan_out=self.config.get("fan_in_fan_out", False),
            # modules_to_save=self.config.get("modules_to_save", None),
        )

    def get_tokenizer(self):
        self._load_model_if_needed()
        return self.tokenizer

    def get_model(self):
        self._load_model_if_needed()
        return self.model

    def forward(self, x):
        self._load_model_if_needed()
        return self.model(x)

    def save(self, path):
        self.model.save_pretrained_merged(path, self.tokenizer, save_method="merged_16bit")

    def load(self, path):
        pass


class LLMTrainer(BaseTrainer):
    # def __init__(self, model, tokenizer, train_dataset, val_dataset, config, model_wrapper=None):
    def __init__(self, model, tokenizer, dataset, config, metrics=None ,model_wrapper=None):
        from unsloth import is_bfloat16_supported
        from trl import SFTTrainer, SFTConfig
        from transformers import TrainingArguments
        import math

        self.model = model
        self.tokenizer = tokenizer
        self.config = config
        self.model_wrapper = model_wrapper
        self.metrics = metrics or {}

        self.save_model_flag = config.get("save_model", False)
        self.load_model_flag = config.get("load_model", False)
        self.model_dir = config.get("model_dir", "checkpoints")
        self.model_load_dir = config.get("model_load_dir", "checkpoints")
        self.model_path = os.path.join(self.model_dir, "model.pt")
        self.model_load_path = os.path.join(self.model_load_dir, "model.pt")

        train_dataset = dataset["train"]
        val_dataset = dataset["test"]

        self.log_callbacks = config.get("log_callbacks", [])
        for cb in self.log_callbacks:
            cb.set_trainer(self)

        # dataset_dict = dataset.get_dataset()
        # train_dataset = dataset_dict.get("train")
        # val_dataset = dataset_dict.get("test")

        if val_dataset is None or len(val_dataset) == 0:
            val_dataset = None

        num_samples = len(train_dataset)  # total training examples
        batch_size = config.get("batch_size", 2)
        num_epochs = config.get("epochs", 1)

        total_steps = math.ceil(num_samples / batch_size * num_epochs)
        # warmup_fraction = 0.05  # 5% warmup
        warmup_fraction = 0.05  # 5% warmup
        calculated_warmup_steps = max(int(total_steps * warmup_fraction), 0)

        warmup_steps = config.get("warmup_steps")

        if warmup_steps is None:
            warmup_steps = calculated_warmup_steps
            print(
                f"Training setup: {num_samples} samples, {total_steps} total steps, {warmup_steps} warmup steps."
            )
        else:
            warmup_steps = int(warmup_steps)

        # self.trainer = SFTTrainer(
        #     model=self.model,
        #     tokenizer=tokenizer,
        #     train_dataset=train_dataset,
        #     eval_dataset=val_dataset,
        #     dataset_text_field=config.get("dataset_text_field", "text"),
        #     max_seq_length=config.get("max_seq_length", 2048),
        #     dataset_num_proc= 2,
        #     # tokenizer_max_length=config.get("tokenizer_max_length", 2048),
        #     packing=config.get("packing", True),
        #     args=TrainingArguments(
        #         per_device_train_batch_size=config.get("batch_size", 2),
        #         per_device_eval_batch_size=config.get("batch_size", 2),
        #         gradient_accumulation_steps=config.get(
        #             "gradient_accumulation_steps", 1
        #         ),
        #         warmup_steps=warmup_steps,
        #         num_train_epochs=config.get("epochs", 1),
        #         eval_strategy=config.get(
        #             "eval_strategy",
        #             "steps"
        #             if val_dataset is not None and len(val_dataset) > 0
        #             else "no",
        #         ),
        #         eval_steps=config.get(
        #             "eval_steps",
        #             0.2 if val_dataset is not None and len(val_dataset) > 0 else 0,
        #         ),
        #         # eval_steps=config.get("eval_steps", 0.2),
        #         group_by_length=config.get("group_by_length", False),
        #         learning_rate=config.get("learning_rate", 2e-4),
        #         fp16=config.get("fp16", not is_bfloat16_supported()),
        #         bf16=config.get("bf16", is_bfloat16_supported()),
        #         logging_steps=config.get(
        #             "logging_steps", 20
        #         ),  # MLFlow recommended data_size /batch_size = total step train
        #         optim=config.get("optim", "adamw_8bit"),
        #         weight_decay=config.get("weight_decay", 0.01),
        #         lr_scheduler_type=config.get("lr_scheduler_type", "linear"),
        #         seed=config.get("seed", 3407),
        #         report_to=config.get("report_to", []),
        #         output_dir=config.get("output_dir", "output/"),
        #         # save_safetensors=config.get("save_safetensors", True),
        #         save_safetensors=True,
        #         save_strategy=config.get(
        #             "save_strategy", "steps"
        #         ),  # "steps", "epoch", or "no"
        #         save_steps=config.get("save_steps", 0.2),  # Save every N steps
        #         save_total_limit=config.get(
        #             "save_total_limit", 1
        #         ),  # Keep only last 3 checkpoints
        #         # Save final model at the end
        #         save_only_model=config.get(
        #             "save_only_model", False
        #         ),  # True = only model weights, False = full checkpoint
        #         # Load from checkpoint if exists
        #         # resume_from_checkpoint=config.get("resume_from_checkpoint", None),  # Path to checkpoint or True for auto-resume
        #     ),
        #     callbacks=config.get("callbacks", None),
        # )
        sft_config = SFTConfig(
            per_device_train_batch_size=config.get("batch_size", 2),
            per_device_eval_batch_size=config.get("batch_size", 2),
            gradient_accumulation_steps=config.get("gradient_accumulation_steps", 1),
            warmup_steps=warmup_steps,
            num_train_epochs=config.get("epochs"),
            eval_strategy=config.get(
                "eval_strategy",
                "steps" if val_dataset is not None and len(val_dataset) > 0 else "no",
            ),
            eval_steps=config.get(
                "eval_steps",
                0.2 if val_dataset is not None and len(val_dataset) > 0 else 0,
            ),
            group_by_length=config.get("group_by_length", False),
            learning_rate=config.get("learning_rate", 2e-4),
            fp16=config.get("fp16", not is_bfloat16_supported()),
            bf16=config.get("bf16", is_bfloat16_supported()),
            logging_steps=config.get("logging_steps", 20),
            optim=config.get("optim", "adamw_8bit"),
            weight_decay=config.get("weight_decay", 0.01),
            lr_scheduler_type=config.get("lr_scheduler_type", "linear"),
            seed=config.get("seed", 3407),
            report_to=config.get("report_to", []),


            output_dir=config.get("output_dir"),
            save_safetensors=True,
            save_strategy=config.get("save_strategy", "steps"),
            save_steps=config.get("save_steps", 0.2),
            save_total_limit=config.get("save_total_limit", 1),
            save_only_model=config.get("save_only_model", False),

            # Dataset-related options
            dataset_num_proc=config.get("dataset_num_proc", 2),
            # packing=config.get("packing", True),
        )

        # Create the SFTTrainer
        self.trainer = SFTTrainer(
            model=self.model,
            tokenizer=tokenizer,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            args=sft_config,  # Replace TrainingArguments with SFTConfig
            # max_length=config.get("max_seq_length", 2048),
            dataset_text_field=config.get("dataset_text_field", "text"),
            max_seq_length=config.get("max_seq_length", 2048),
            resume_from_checkpoint=config.get("resume_from_checkpoint", None),  # Path to checkpoint or True for auto-resume
            callbacks=config.get("callbacks", None),
        )

    def training_step(self, batch):
        pass

    def validation_step(self, batch):
        pass

    # def run(self):
    #     from unsloth import FastLanguageModel
    #     result = self.trainer.train()

    #     # Prepare for inference after training
    #     # FastLanguageModel.for_inference(self.model)

    #     return result

    def run(self):
        from unsloth import FastLanguageModel

        # Log training start
        if "train" in self.metrics:
            self.metrics["train"].on_train_begin()

        # Pass resume_from_checkpoint to train() method, NOT to TrainingArguments
        if self.config.get("resume_from_checkpoint", None):
            print(f"\n{'=' * 60}")
            print(f"RESUMING TRAINING FROM CHECKPOINT")
            print(f"{'=' * 60}")
            print(f"Checkpoint: {self.config.get('resume_from_checkpoint', None)}\n")
            result = self.trainer.train(
                resume_from_checkpoint=self.config.get("resume_from_checkpoint", None)
            )
        else:
            print(f"\n{'=' * 60}")
            print(f"STARTING TRAINING FROM SCRATCH")
            print(f"{'=' * 60}\n")
            result = self.trainer.train()

        # Log training end
        if "train" in self.metrics:
            self.final_metrics = self.metrics["train"].on_train_end()
            for callback in self.log_callbacks:
                callback.on_train_end()

        return result
    
    def evaluate(self):
        """Run evaluation and return metrics"""
        if hasattr(self.trainer, 'eval_dataset') and self.trainer.eval_dataset is not None:
            eval_results = self.trainer.evaluate()
            return eval_results
        return {}


# @register_task("llm_finetuning")
class LLMTaskFactory(AbstractTaskFactory):
    def __init__(self):
        self._model_instance = None  # Cache the model instance

    def create_dataset(self, config):
        # Create model first to get tokenizer
        model = self.create_model(config)
        tokenizer = model.get_tokenizer()

        # Get dataset configuration
        dataset_config = config.get("dataset_config") or {}

        if "source" not in dataset_config:
            raise ValueError("dataset_config must contain a 'source' key")

        print(f"Creating LLMFineTuningDataset with config: {dataset_config}")

        return LLMFineTuningDataset(
            tokenizer=tokenizer,
            system_prompt=config.get("system_prompt"),
            config=dataset_config,
        )

    def create_model(self, config):
        # Return cached model if it exists, otherwise create new one
        if self._model_instance is None:
            model_config = config.get("model_config", {})
            print(f"Creating LLMModel with config: {model_config}")

            model_name = config.get("model_name") or model_config.get("model_name")
            if model_name is None:
                raise ValueError(
                    "Model name must be specified in config or model_config"
                )

            self._model_instance = LLMModel(
                model_name=model_name,
                config=model_config,
            )
        return self._model_instance
    
    def create_metrics(self, config):
        train_metrics = LLMFinetuneMetrics()
        val_metrics = LLMFinetuneMetrics()
        return {"train": train_metrics, "val": val_metrics}

    def create_trainer(self, model, dataset, metrics, config):
        # formatted = dataset.load_dataset()
        dataset = dataset.load_dataset()

        trainer_config = config.get("trainer_config", {})
        print(f"Creating LLMTrainer with config: {trainer_config}")

        return LLMTrainer(
            model=model.get_model(),
            tokenizer=model.get_tokenizer(),
            dataset=dataset,
            model_wrapper=model,
            config=trainer_config,
            metrics=metrics,
            # config=config,   # pass directly
            # train_dataset=formatted["train"],
            # val_dataset=formatted["test"],
        )