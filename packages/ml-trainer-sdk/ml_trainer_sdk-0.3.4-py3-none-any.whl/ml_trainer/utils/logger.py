import logging
import os
from datetime import datetime


# def get_logger(name="trainer", log_dir="logs"):
#     os.makedirs(log_dir, exist_ok=True)
#     log_path = os.path.join(
#         log_dir, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
#     )

#     logger = logging.getLogger(name)
#     logger.setLevel(logging.INFO)

#     if not logger.handlers:
#         fh = logging.FileHandler(log_path)
#         ch = logging.StreamHandler()
#         formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
#         fh.setFormatter(formatter)
#         ch.setFormatter(formatter)
#         logger.addHandler(fh)
#         logger.addHandler(ch)

#     return logger, log_path


class LoggerTemplate:

    def on_train_start(self):
        pass
    
    def on_epoch_start(self):
        pass
    
    def on_epoch_end(self,*args,**kwargs):
        pass

    def on_save_checkpoint(self):
        pass

    def on_batch_end(self,*args,**kwargs):
        pass

    def on_train_end(self,*args,**kwargs):
        pass

    def set_trainer(self,trainer):
        self.trainer=trainer

class BaseLogger:
    def __init__(self, name="trainer", log_dir="logs"):
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(
            log_dir, f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            fh = logging.FileHandler(log_path)
            ch = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
            fh.setFormatter(formatter)
            ch.setFormatter(formatter)
            self.logger.addHandler(fh)
            self.logger.addHandler(ch)


    def on_train_start(self,model,device,train_loader,val_loader):
        self.logger.info(f"Device: {device}")
        self.logger.info(f"Model: {type(model).__name__}")
        self.logger.info(f"Training set size: {len(train_loader.dataset)}")
        self.logger.info(f"Validation set size: {len(val_loader.dataset)}")
    
    def on_epoch_start(self):
        self.info(f"--- Epoch {self.trainer.current_epoch + 1}/{self.trainer.epochs} ---")
        pass

    def info(self,message):
        self.logger.info(message)


class TensorboardLogger(BaseLogger):
    def __init__(self, name="trainer", log_dir="logs"):
        super().__init__(name, log_dir)
        from torch.utils.tensorboard import SummaryWriter

        tb_log_dir = os.path.join(
            log_dir, f"tb_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        self.writer = SummaryWriter(tb_log_dir)

    def log_metrics(self, metrics, step, prefix=""):
        for key, value in metrics.items():
            self.writer.add_scalar(f"{prefix}{key}", value, step)

    def close(self):
        self.writer.close()