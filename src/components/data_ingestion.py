"""Read the source dataset and persist raw, training, and test data."""

import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from src.exception import CustomException
from src.logger import logger


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class DataIngestionConfig:
    source_data_path: str = str(PROJECT_ROOT / "Notebook" / "data" / "stud.csv")
    train_data_path: str = str(PROJECT_ROOT / "artifacts" / "train.csv")
    test_data_path: str = str(PROJECT_ROOT / "artifacts" / "test.csv")
    raw_data_path: str = str(PROJECT_ROOT / "artifacts" / "data.csv")
    test_size: float = 0.2
    random_state: int = 42


class DataIngestion:
    def __init__(self, ingestion_config: DataIngestionConfig | None = None) -> None:
        self.ingestion_config = ingestion_config or DataIngestionConfig()

    def initiate_data_ingestion(self) -> tuple[str, str]:
        """Split the source CSV, persist the outputs, and return train/test paths."""
        logger.info("Starting data ingestion")
        try:
            source_path = Path(self.ingestion_config.source_data_path)
            df = pd.read_csv(source_path)
            logger.info("Loaded %d rows and %d columns from %s", *df.shape, source_path)

            if df.empty:
                raise ValueError(f"The source dataset is empty: {source_path}")
            if len(df) < 2:
                raise ValueError("At least two rows are required for a train/test split")

            train_set, test_set = train_test_split(
                df,
                test_size=self.ingestion_config.test_size,
                random_state=self.ingestion_config.random_state,
            )

            output_paths = (
                self.ingestion_config.raw_data_path,
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path,
            )
            for output_path in output_paths:
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            df.to_csv(self.ingestion_config.raw_data_path, index=False)
            train_set.to_csv(self.ingestion_config.train_data_path, index=False)
            test_set.to_csv(self.ingestion_config.test_data_path, index=False)

            logger.info(
                "Data ingestion completed: %d raw, %d training, and %d test rows",
                len(df),
                len(train_set),
                len(test_set),
            )
            return (
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path,
            )
        except Exception as error:
            logger.exception("Data ingestion failed")
            raise CustomException(error, sys) from error


if __name__ == "__main__":
    DataIngestion().initiate_data_ingestion()
