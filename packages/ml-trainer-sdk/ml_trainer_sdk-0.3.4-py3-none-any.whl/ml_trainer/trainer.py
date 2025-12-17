# Standard library imports
import abc
import os
from pathlib import Path
from datetime import datetime
from typing import Dict

# Third-party
import torch
import numpy as np
from torch.utils.tensorboard import SummaryWriter

# Local application
from ml_trainer.utils.logger import BaseLogger
from ml_trainer.utils.metrics import BaseMetrics
from ml_trainer.utils.metrics import ClassificationMetrics
from ml_trainer.utils.metrics import TimeSeriesMetrics

Path(__file__).resolve().parent.parent


class BaseTrainer(abc.ABC):
    """
    BaseTrainer - Abstract Base Class for Machine Learning Training

    This module provides an abstract base class for training machine learning models
    with PyTorch. It includes common functionality for training loops, validation,
    logging, checkpointing, and TensorBoard integration.

    Features:
        - Abstract training and validation step methods for customization
        - Automatic device detection (CUDA/CPU)
        - Integrated logging with configurable log directories
        - Model checkpointing with timestamp-based naming
        - TensorBoard integration for training visualization
        - Configurable model saving/loading functionality
        - Automatic data type handling for different loss functions

    Usage:
        Inherit from BaseTrainer and implement the abstract methods:
        - training_step(batch): Define how to process a training batch
        - validation_step(batch): Define how to process a validation batch

    Example:
        class MyTrainer(BaseTrainer):
            def training_step(self, batch):
                inputs, labels = self.prepare_batch(*batch)
                outputs = self.model(inputs)
                return self.loss_fn(outputs, labels)

            def validation_step(self, batch):
                inputs, labels = self.prepare_batch(*batch)
                outputs = self.model(inputs)
                return self.loss_fn(outputs, labels)

    Key methods:
    - __init__: Initializes the trainer with model, data loaders, optimizer, loss function,
      and other configuration parameters.
    - save_model: Saves the trained model to the specified directory.
    - load_model: Loads a previously saved model.
    - prepare_batch: Prepares inputs and labels for training, adjusting them for the
      specific loss function.
    - training_step: Abstract method to define the training step (to be implemented in subclasses).
    - validation_step: Abstract method to define the validation step (to be implemented in subclasses).
    - train_one_epoch: Handles one epoch of training, including loss calculation and optimization.
    - validate: Evaluates the model on the validation dataset.
    - run: Executes the full training process for the specified number of epochs.


    """

    def __init__(
        self,
        model,
        train_loader,
        val_loader,
        optimizer,
        loss_fn,
        epochs=10,
        device=None,
        log_dir=None,
        checkpoint_path=None,
        log_name="trainer",
        config=None,
        train_metrics: BaseMetrics = None,  # <--- METRICS ADDED
        val_metrics: BaseMetrics = None,  # <--- METRICS ADDED
    ):
        self.config = config or {}
        self.device = device or torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.model = model.to(self.device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        self.epochs = epochs

        # self.logger, _ = get_logger(name=log_name, log_dir=log_dir or "logs")

        self.base_logger = BaseLogger(name=log_name, log_dir=log_dir or "logs")
        

        self.log_callbacks = config.get("log_callbacks", [])
        for cb in self.log_callbacks:
            cb.set_trainer(self)

        # --- ADDED METRICS INITIALIZATION ---
        num_classes = self.config.get("num_classes", 2)
        self.train_metrics = train_metrics
        self.val_metrics = val_metrics
        # raise ValueError(self.train_metrics.num_classes, self.val_metrics.num_classes)
        # --- END OF ADDED CODE ---

        self.checkpoint_path = self.config.get("checkpoint_path", None)

        self.writer = SummaryWriter(
            log_dir or f"runs/train_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.best_val_loss = float("inf")


        self.save_model_dir = self.config.get("save_model", False)
        self.load_model_dir = self.config.get("load_model", False)
        self.resume_from_checkpoint = self.config.get("resume_from_checkpoint", None)

        if self.load_model_dir:
            self.load_model()

        # for checkpointing
        self.current_epoch = 0
        self.loss = None
        # if checkpoint_path:
        #     os.makedirs(self.checkpoint_path, exist_ok=True)

        if self.resume_from_checkpoint:
            print(f"Resuming from checkpoint: {self.resume_from_checkpoint}")
            self.load_checkpoint(self.resume_from_checkpoint)

    # def save_model(self):
    #     print("saving the model")
    #     if hasattr(self.model, "save"):
    #         Path(self.save_model_dir).mkdir(parents=True, exist_ok=True)
    #         self.model.save(self.save_model_dir)
    #         self.base_logger.info(f"Model saved via .save() to {self.save_model_dir}")

    #     else:
    #         self.logger.warning("Model has no `.save()` method.")

    def save_model(self):
        print("saving the model")
        if hasattr(self.model, "save"):
            Path(self.save_model_dir).mkdir(parents=True, exist_ok=True)
            # Create a proper file path with .pth extension
            model_file = Path(self.save_model_dir) / "model.pth"
            self.model.save(str(model_file))
            self.base_logger.info(f"Model saved via .save() to {model_file}")
        else:
            self.logger.warning("Model has no `.save()` method.")


    def load_model(self):
        if hasattr(self.model, "load"):
            self.model.load(self.load_model_dir)
            self.base_logger.info(f"Model loaded via .load() from {self.load_model_dir}")
        else:
            self.logger.warning("Model has no `.load()` method.")

    def prepare_batch(self, inputs, labels):
        inputs = inputs.to(self.device)
        labels = labels.to(self.device)

        if isinstance(self.loss_fn, torch.nn.CrossEntropyLoss):
            labels = labels.long()
        elif isinstance(
            self.loss_fn,
            (torch.nn.MSELoss, torch.nn.BCELoss, torch.nn.BCEWithLogitsLoss),
        ):
            labels = labels.float()

        return inputs, labels

    @abc.abstractmethod
    def training_step(self, batch):
        raise NotImplemented

    @abc.abstractmethod
    def validation_step(self, batch):
        raise NotImplemented

    # @abc.abstractmethod
    def checkpointing_step(self):
        print("checkpointing step NOT IMPLEMENTED")
        pass

    # @abc.abstractmethod
    def load_checkpoint(self, checkpoint_path):
        print("load checkpoint NOT IMPLEMENTED")
        pass

    def train_one_epoch(self, epoch_index):
        self.model.train()
        total_loss = 0.0
        print("Training... metrics:", self.train_metrics)
        self.train_metrics.reset()

        for batch in self.train_loader:
            # classification_trainer = ClassificationTrainer()
            # if self.config.get("task") == "classification":
            # step_output = ClassificationTrainer.training_step(self, batch)
            step_output = self.training_step(batch)
            # raise ValueError(step_output)
            loss = step_output["loss"]

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()

            self.train_metrics.update(
                predictions=step_output["preds"], labels=step_output["labels"]
            )
            for cb in self.log_callbacks:
                cb.on_batch_end()
        

        return total_loss / len(self.train_loader)

    def validate(self):
        self.model.eval()
        total_loss = 0.0
        self.val_metrics.reset()

        with torch.no_grad():
            for batch in self.val_loader:
                step_output = self.validation_step(batch)
                # remove this and make the metric selection dynamic: polymophism
                # if self.config.get("task") == "classification":
                #     step_output = ClassificationTrainer.validation_step(self, batch)

                loss = step_output["loss"]
                total_loss += loss.item()

                self.val_metrics.update(
                    predictions=step_output["preds"], labels=step_output["labels"]
                )

        return total_loss / len(self.val_loader)

    def _log_confusion_matrix(self, cm: np.ndarray, class_names: list):
        """Logs the confusion matrix in a readable format."""
        if not class_names:
            class_names = [f"C{i}" for i in range(len(cm))]

        header = f"{'':<12}" + " ".join([f"{name[:8]:^8}" for name in class_names])
        self.base_logger.info(
            "Validation Confusion Matrix (True Label vs. Predicted Label):"
        )
        self.base_logger.info(header)
        self.base_logger.info(f"{'-' * (len(header) + 2)}")

        for i, row in enumerate(cm):
            row_str = f"{class_names[i][:10]:<10s} |"
            for val in row:
                row_str += f" {int(val):^8}"
            self.base_logger.info(row_str)
        self.base_logger.info("-" * (len(header) + 2))

    def run(self):
        self.base_logger.info(f"Device: {self.device}")
        self.base_logger.info(f"Model: {type(self.model).__name__}")
        self.base_logger.info(f"Training set size: {len(self.train_loader.dataset)}")
        self.base_logger.info(f"Validation set size: {len(self.val_loader.dataset)}")

        for cb in self.log_callbacks:
            cb.on_train_start()
        for epoch in range(self.current_epoch, self.epochs):
            self.current_epoch = epoch
            self.base_logger.info(f"--- Epoch {epoch + 1}/{self.epochs} ---")

            for cb in self.log_callbacks: 
                cb.on_epoch_start()

            self.train_loss = self.train_one_epoch(epoch)
            val_loss = self.validate()

            self.loss = val_loss
            self.writer.add_scalars(
                "Loss", {"Train": self.train_loss, "Validation": val_loss}, epoch + 1
            )
            self.base_logger.info(
                f"Epoch {epoch + 1}: Train Loss = {self.train_loss:.4f}, Val Loss = {val_loss:.4f}"
            )
            if self.checkpoint_path:
                print(f"current epoch: {self.current_epoch}")
                print(f"epoch: {epoch}")
                print(
                    f"Saving checkpoint at epoch {epoch + 1} to {self.checkpoint_path}"
                )
                self.checkpointing_step()

            # --- ADDED: Compute and log metrics ---
            # print(self.train_metrics, self.val_metrics)
            if self.train_metrics:
                # train_results = self.train_metrics.compute()
                train_results = self.train_metrics.compute()
                self.train_results = train_results
                self.base_logger.info(
                    f"Train Accuracy: {train_results.get('accuracy', -1):.4f}"
                )
                self.writer.add_scalar(
                    "Accuracy/Train", train_results.get("accuracy", -1), epoch + 1
                )

            if self.val_metrics:
                val_results = self.val_metrics.compute()
                summary = self.val_metrics.get_summary()
                self.val_results = val_results
                self.summary = summary
                self.base_logger.info(f"\n{summary}")

                # Log key validation metrics to TensorBoard
                self.writer.add_scalar(
                    "Accuracy/Validation", val_results.get("accuracy", -1), epoch + 1
                )
                self.writer.add_scalar(
                    "F1-Macro/Validation", val_results.get("f1_macro", -1), epoch + 1
                )

                # Log the confusion matrix as requested
                if "confusion_matrix" in val_results:
                    cm = np.array(val_results["confusion_matrix"])
                    self._log_confusion_matrix(cm, self.val_metrics.class_names)
            # --- END OF ADDED CODE ---
            for callback in self.log_callbacks:
                callback.on_epoch_end()

        if self.save_model_dir:
            self.save_model()
            for callback in self.log_callbacks:
                callback.on_save_checkpoint()
        for callback in self.log_callbacks:
            callback.on_train_end()

        return self.model