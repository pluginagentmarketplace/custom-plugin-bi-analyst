#!/usr/bin/env python3
"""
ML Pipeline Builder
BI Analyst Plugin - Data-AI Skill
Builds and validates machine learning pipelines with best practices.
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime


@dataclass
class PipelineStep:
    """Represents a step in the ML pipeline."""
    name: str
    type: str  # data_loading, preprocessing, feature_engineering, training, evaluation
    config: dict = field(default_factory=dict)
    dependencies: list = field(default_factory=list)
    outputs: list = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed


@dataclass
class MLPipeline:
    """Complete ML pipeline definition."""
    name: str
    version: str
    steps: list[PipelineStep] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class MLPipelineBuilder:
    """Build and validate ML pipelines."""

    def __init__(self, name: str, version: str = "1.0.0"):
        self.pipeline = MLPipeline(name=name, version=version)
        self.pipeline.metadata = {
            "created_at": datetime.now().isoformat(),
            "framework": "generic",
        }

    def add_data_loading(
        self,
        source: str,
        format: str = "csv",
        **kwargs
    ) -> "MLPipelineBuilder":
        """Add data loading step."""
        step = PipelineStep(
            name="data_loading",
            type="data_loading",
            config={
                "source": source,
                "format": format,
                **kwargs
            },
            outputs=["raw_data"]
        )
        self.pipeline.steps.append(step)
        return self

    def add_data_validation(
        self,
        schema: Optional[dict] = None,
        checks: Optional[list] = None
    ) -> "MLPipelineBuilder":
        """Add data validation step."""
        step = PipelineStep(
            name="data_validation",
            type="preprocessing",
            config={
                "schema": schema or {},
                "checks": checks or [
                    "no_nulls_in_target",
                    "no_duplicate_ids",
                    "valid_date_ranges",
                    "expected_columns"
                ]
            },
            dependencies=["raw_data"],
            outputs=["validated_data"]
        )
        self.pipeline.steps.append(step)
        return self

    def add_preprocessing(
        self,
        missing_strategy: str = "median",
        scaling: str = "standard",
        encoding: str = "onehot",
        **kwargs
    ) -> "MLPipelineBuilder":
        """Add preprocessing step."""
        step = PipelineStep(
            name="preprocessing",
            type="preprocessing",
            config={
                "missing_values": {
                    "strategy": missing_strategy,
                    "fill_value": kwargs.get("fill_value")
                },
                "scaling": {
                    "method": scaling,
                    "columns": kwargs.get("scale_columns", "numeric")
                },
                "encoding": {
                    "method": encoding,
                    "columns": kwargs.get("encode_columns", "categorical")
                }
            },
            dependencies=["validated_data"],
            outputs=["preprocessed_data"]
        )
        self.pipeline.steps.append(step)
        return self

    def add_feature_engineering(
        self,
        transformations: Optional[list] = None,
        feature_selection: Optional[dict] = None
    ) -> "MLPipelineBuilder":
        """Add feature engineering step."""
        step = PipelineStep(
            name="feature_engineering",
            type="feature_engineering",
            config={
                "transformations": transformations or [
                    {"type": "polynomial", "degree": 2, "columns": []},
                    {"type": "datetime_features", "columns": []},
                    {"type": "text_features", "columns": [], "method": "tfidf"}
                ],
                "feature_selection": feature_selection or {
                    "method": "mutual_information",
                    "k_best": 20
                }
            },
            dependencies=["preprocessed_data"],
            outputs=["features", "feature_metadata"]
        )
        self.pipeline.steps.append(step)
        return self

    def add_train_test_split(
        self,
        test_size: float = 0.2,
        stratify: bool = True,
        random_state: int = 42
    ) -> "MLPipelineBuilder":
        """Add train/test split step."""
        step = PipelineStep(
            name="train_test_split",
            type="preprocessing",
            config={
                "test_size": test_size,
                "stratify": stratify,
                "random_state": random_state
            },
            dependencies=["features"],
            outputs=["X_train", "X_test", "y_train", "y_test"]
        )
        self.pipeline.steps.append(step)
        return self

    def add_training(
        self,
        algorithm: str = "random_forest",
        hyperparameters: Optional[dict] = None,
        cross_validation: bool = True,
        cv_folds: int = 5
    ) -> "MLPipelineBuilder":
        """Add model training step."""
        default_params = self._get_default_hyperparameters(algorithm)
        step = PipelineStep(
            name="model_training",
            type="training",
            config={
                "algorithm": algorithm,
                "hyperparameters": {**default_params, **(hyperparameters or {})},
                "cross_validation": {
                    "enabled": cross_validation,
                    "folds": cv_folds,
                    "scoring": ["accuracy", "f1", "roc_auc"]
                },
                "early_stopping": {
                    "enabled": True,
                    "patience": 10
                }
            },
            dependencies=["X_train", "y_train"],
            outputs=["trained_model", "cv_scores"]
        )
        self.pipeline.steps.append(step)
        return self

    def add_hyperparameter_tuning(
        self,
        search_method: str = "optuna",
        n_trials: int = 100,
        param_space: Optional[dict] = None
    ) -> "MLPipelineBuilder":
        """Add hyperparameter tuning step."""
        step = PipelineStep(
            name="hyperparameter_tuning",
            type="training",
            config={
                "method": search_method,
                "n_trials": n_trials,
                "param_space": param_space or {},
                "optimization": {
                    "direction": "maximize",
                    "metric": "f1_score"
                }
            },
            dependencies=["X_train", "y_train"],
            outputs=["best_params", "tuning_history"]
        )
        self.pipeline.steps.append(step)
        return self

    def add_evaluation(
        self,
        metrics: Optional[list] = None,
        threshold: float = 0.5
    ) -> "MLPipelineBuilder":
        """Add model evaluation step."""
        step = PipelineStep(
            name="model_evaluation",
            type="evaluation",
            config={
                "metrics": metrics or [
                    "accuracy",
                    "precision",
                    "recall",
                    "f1_score",
                    "roc_auc",
                    "confusion_matrix"
                ],
                "threshold": threshold,
                "reports": [
                    "classification_report",
                    "feature_importance",
                    "roc_curve",
                    "precision_recall_curve"
                ]
            },
            dependencies=["trained_model", "X_test", "y_test"],
            outputs=["evaluation_metrics", "evaluation_report"]
        )
        self.pipeline.steps.append(step)
        return self

    def add_model_registry(
        self,
        registry: str = "mlflow",
        auto_register: bool = True,
        stage: str = "staging"
    ) -> "MLPipelineBuilder":
        """Add model registry step."""
        step = PipelineStep(
            name="model_registry",
            type="deployment",
            config={
                "registry": registry,
                "auto_register": auto_register,
                "stage": stage,
                "metadata": {
                    "log_metrics": True,
                    "log_artifacts": True,
                    "log_params": True
                }
            },
            dependencies=["trained_model", "evaluation_metrics"],
            outputs=["registered_model", "model_uri"]
        )
        self.pipeline.steps.append(step)
        return self

    def add_deployment(
        self,
        format: str = "onnx",
        serving: str = "fastapi",
        monitoring: bool = True
    ) -> "MLPipelineBuilder":
        """Add deployment step."""
        step = PipelineStep(
            name="deployment",
            type="deployment",
            config={
                "export_format": format,
                "serving_framework": serving,
                "monitoring": {
                    "enabled": monitoring,
                    "data_drift": True,
                    "prediction_logging": True
                },
                "endpoints": {
                    "predict": "/predict",
                    "health": "/health",
                    "metrics": "/metrics"
                }
            },
            dependencies=["registered_model"],
            outputs=["deployed_model", "endpoint_url"]
        )
        self.pipeline.steps.append(step)
        return self

    def _get_default_hyperparameters(self, algorithm: str) -> dict:
        """Get default hyperparameters for common algorithms."""
        defaults = {
            "random_forest": {
                "n_estimators": 100,
                "max_depth": 10,
                "min_samples_split": 5,
                "min_samples_leaf": 2
            },
            "xgboost": {
                "n_estimators": 100,
                "max_depth": 6,
                "learning_rate": 0.1,
                "subsample": 0.8
            },
            "lightgbm": {
                "n_estimators": 100,
                "max_depth": -1,
                "learning_rate": 0.1,
                "num_leaves": 31
            },
            "logistic_regression": {
                "C": 1.0,
                "max_iter": 1000,
                "solver": "lbfgs"
            },
            "neural_network": {
                "hidden_layers": [128, 64, 32],
                "activation": "relu",
                "dropout": 0.3,
                "learning_rate": 0.001
            }
        }
        return defaults.get(algorithm, {})

    def validate(self) -> dict:
        """Validate the pipeline configuration."""
        errors = []
        warnings = []

        # Check for required steps
        step_types = [s.type for s in self.pipeline.steps]

        if "data_loading" not in step_types:
            errors.append("Pipeline must start with data_loading step")

        if "training" not in step_types:
            errors.append("Pipeline must include training step")

        if "evaluation" not in step_types:
            warnings.append("Pipeline should include evaluation step")

        # Check dependencies
        available_outputs = set()
        for step in self.pipeline.steps:
            for dep in step.dependencies:
                if dep not in available_outputs:
                    errors.append(f"Step '{step.name}' has unmet dependency: {dep}")
            available_outputs.update(step.outputs)

        # Check for best practices
        if "data_validation" not in [s.name for s in self.pipeline.steps]:
            warnings.append("Consider adding data validation step")

        if "hyperparameter_tuning" not in [s.name for s in self.pipeline.steps]:
            warnings.append("Consider adding hyperparameter tuning")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def build(self) -> dict:
        """Build and return the pipeline configuration."""
        validation = self.validate()

        if not validation["valid"]:
            raise ValueError(f"Pipeline validation failed: {validation['errors']}")

        return {
            "name": self.pipeline.name,
            "version": self.pipeline.version,
            "metadata": self.pipeline.metadata,
            "steps": [
                {
                    "name": step.name,
                    "type": step.type,
                    "config": step.config,
                    "dependencies": step.dependencies,
                    "outputs": step.outputs
                }
                for step in self.pipeline.steps
            ],
            "validation": validation
        }

    def to_yaml(self, path: str):
        """Export pipeline to YAML file."""
        import yaml
        config = self.build()
        Path(path).write_text(yaml.dump(config, default_flow_style=False))

    def to_json(self, path: str):
        """Export pipeline to JSON file."""
        config = self.build()
        Path(path).write_text(json.dumps(config, indent=2))


def create_classification_pipeline(
    name: str,
    data_source: str,
    algorithm: str = "xgboost"
) -> dict:
    """Create a standard classification pipeline."""
    builder = MLPipelineBuilder(name)

    pipeline = (
        builder
        .add_data_loading(source=data_source)
        .add_data_validation()
        .add_preprocessing()
        .add_feature_engineering()
        .add_train_test_split()
        .add_hyperparameter_tuning()
        .add_training(algorithm=algorithm)
        .add_evaluation()
        .add_model_registry()
        .build()
    )

    return pipeline


def main():
    """Demo pipeline creation."""
    pipeline = create_classification_pipeline(
        name="customer_churn_prediction",
        data_source="s3://bucket/data.parquet",
        algorithm="xgboost"
    )

    print(json.dumps(pipeline, indent=2))


if __name__ == "__main__":
    main()
