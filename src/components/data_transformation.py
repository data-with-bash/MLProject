"""Transform student score data into model-ready train and test arrays."""

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.exception import CustomException
from src.logger import logger
from src.utils import save_object


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TARGET_COLUMN = "math_score"
NUMERICAL_FEATURES = ["writing_score", "reading_score"]
CATEGORICAL_FEATURES = [
    "gender",
    "race_ethnicity",
    "parental_level_of_education",
    "lunch",
    "test_preparation_course",
]
REQUIRED_COLUMNS = {*NUMERICAL_FEATURES, *CATEGORICAL_FEATURES, TARGET_COLUMN}


@dataclass(frozen=True)
class DataTransformationConfig:
    preprocessor_obj_file_path: str = str(
        PROJECT_ROOT / "artifacts" / "preprocessor.pkl"
    )


class DataTransformation:
    def __init__(
        self,
        data_transformation_config: DataTransformationConfig | None = None,
    ) -> None:
        self.data_transformation_config = (
            data_transformation_config or DataTransformationConfig()
        )

    def get_data_transformer_object(self) -> ColumnTransformer:
        """Build the imputation, scaling, and categorical encoding pipeline."""
        try:
            numerical_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]
            )
            categorical_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    (
                        "one_hot_encoder",
                        OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    ),
                ]
            )

            preprocessor = ColumnTransformer(
                transformers=[
                    ("num_pipeline", numerical_pipeline, NUMERICAL_FEATURES),
                    ("cat_pipeline", categorical_pipeline, CATEGORICAL_FEATURES),
                ]
            )
            logger.info("Created numerical and categorical preprocessing pipelines")
            return preprocessor
        except Exception as error:
            raise CustomException(error, sys) from error

    @staticmethod
    def _validate_dataframe(dataframe: pd.DataFrame, split_name: str) -> None:
        if dataframe.empty:
            raise ValueError(f"The {split_name} dataset is empty")

        missing_columns = sorted(REQUIRED_COLUMNS.difference(dataframe.columns))
        if missing_columns:
            raise ValueError(
                f"The {split_name} dataset is missing required columns: "
                f"{', '.join(missing_columns)}"
            )

    def initiate_data_transformation(
        self, train_path: str, test_path: str
    ) -> tuple[np.ndarray, np.ndarray, str]:
        """Fit on the training CSV, transform both splits, and save the preprocessor."""
        logger.info("Starting data transformation")
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)
            logger.info(
                "Loaded training data (%d rows) and test data (%d rows)",
                len(train_df),
                len(test_df),
            )

            self._validate_dataframe(train_df, "training")
            self._validate_dataframe(test_df, "test")

            train_targets = pd.to_numeric(train_df[TARGET_COLUMN], errors="raise")
            test_targets = pd.to_numeric(test_df[TARGET_COLUMN], errors="raise")
            train_features = train_df.drop(columns=[TARGET_COLUMN])
            test_features = test_df.drop(columns=[TARGET_COLUMN])

            preprocessor = self.get_data_transformer_object()
            logger.info("Fitting preprocessing pipeline on training data")
            train_features_array = preprocessor.fit_transform(train_features)
            test_features_array = preprocessor.transform(test_features)

            train_array = np.hstack(
                (train_features_array, train_targets.to_numpy().reshape(-1, 1))
            )
            test_array = np.hstack(
                (test_features_array, test_targets.to_numpy().reshape(-1, 1))
            )

            save_object(
                file_path=self.data_transformation_config.preprocessor_obj_file_path,
                obj=preprocessor,
            )
            logger.info(
                "Data transformation completed: %d training rows, %d test rows; "
                "preprocessor saved to %s",
                train_array.shape[0],
                test_array.shape[0],
                self.data_transformation_config.preprocessor_obj_file_path,
            )

            return (
                train_array,
                test_array,
                self.data_transformation_config.preprocessor_obj_file_path,
            )
        except Exception as error:
            logger.exception("Data transformation failed")
            raise CustomException(error, sys) from error
