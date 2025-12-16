import logging
from typing import Any, Callable

try:
    import lightning as L
except ImportError:
    raise ImportError("Lightning is not installed. Please install lightning to use LightningHdf5DataModule.")

from torch.utils.data import DataLoader

from f9columnar.ml.dataloader_helpers import ColumnSelection
from f9columnar.ml.hdf5_dataloader import WeightedDatasetBatch, get_ml_hdf5_dataloader


class LightningHdf5DataModule(L.LightningDataModule):
    def __init__(
        self,
        name: str,
        files: str | list[str],
        column_names: list[str],
        stage_split_piles: dict[str, list[int] | int],
        shuffle: bool = False,
        collate_fn: Callable[[tuple[WeightedDatasetBatch, dict[str, Any]]], Any] | None = None,
        dataset_kwargs: dict[str, Any] | None = None,
        dataloader_kwargs: dict[str, Any] | None = None,
    ) -> None:
        super().__init__()
        self.dl_name = name
        self.files = files
        self.column_names = column_names
        self.stage_split_piles = stage_split_piles
        self.shuffle = shuffle
        self.collate_fn = collate_fn
        self.dataset_kwargs = dataset_kwargs
        self.dl_kwargs = dataloader_kwargs

        self._selection: ColumnSelection | None = None

    @property
    def selection(self) -> ColumnSelection:
        if self._selection is None:
            raise ValueError("DataModule not yet setup, selection is not available!")
        return self._selection

    def _get_dataloader(self, stage: str) -> DataLoader:
        logging.info(f"[green]Creating dataloader for stage: {stage}.[/green]")

        dl, self._selection, _ = get_ml_hdf5_dataloader(
            f"{stage} - {self.dl_name}",
            self.files,
            self.column_names,
            stage_split_piles=self.stage_split_piles,
            stage=stage,
            shuffle=self.shuffle,
            collate_fn=self.collate_fn,
            dataset_kwargs=self.dataset_kwargs,
            dataloader_kwargs=self.dl_kwargs,
        )
        return dl

    def train_dataloader(self) -> DataLoader:
        return self._get_dataloader("train")

    def val_dataloader(self) -> DataLoader:
        return self._get_dataloader("val")

    def test_dataloader(self) -> DataLoader:
        return self._get_dataloader("test")
