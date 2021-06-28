import os
import abc
import torch
import torch.distributed as dist
from face_lib.utils import cfg, FACE_METRICS


class TrainerBase(metaclass=abc.ABCMeta):
    _INF = -1e10

    def __init__(self, args, board):
        self.args = args
        # Load configurations
        self.board = board
        self.model_args = cfg.load_config(args.model_config)

        self.backbone = None
        self.head = None
        self.backbone_criterion = None
        self.head_criterion = None

        self.model = dict()
        self.data = dict()

        self.device = "cuda" if torch.cuda.is_available else "cpu"
        # create directory for experiment

        self.checkpoints_path = self.args.root / "checkpoints"
        os.makedirs(self.checkpoints_path)

        # Set up distributed train
        if self.model_args.is_distributed:
            self.world_size = int(os.environ["WORLD_SIZE"])
            self.rank = int(os.environ["RANK"])
            dist_url = "tcp://{}:{}".format(
                os.environ["MASTER_ADDR"], os.environ["MASTER_PORT"]
            )
            dist.init_process_group(
                backend=self.args.distr_backend,
                init_method=dist_url,
                rank=self.rank,
                world_size=self.world_size,
            )
            self.local_rank = args.local_rank
            torch.cuda.set_device(self.local_rank)
        self.start_epoch = 0

    def train_runner(self):
        self._model_loader()
        self._report_settings()
        self._data_loader()
        self._main_loop()

    @abc.abstractmethod
    def _data_loader(self):
        """
        TODO: docs
        """
        ...

    @abc.abstractmethod
    def _model_evaluate(self, epoch: int):
        """
        TODO: docs
        """
        ...

    @abc.abstractmethod
    def _model_train(self, epoch: int):
        """
        TODO: docs
        """
        ...

    @abc.abstractmethod
    def _main_loop(self):
        """
        TODO: docs
        """
        ...

    @abc.abstractmethod
    def _report_settings(self):
        """
        TODO: docs
        """
        ...
