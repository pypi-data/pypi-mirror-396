from profiles_rudderstack.model import BaseModelType
from profiles_rudderstack.recipe import PyNativeRecipe, NoOpRecipe
from profiles_rudderstack.material import WhtFolder
from ..utils import utils
from typing import Tuple, Dict, Any, List
from profiles_rudderstack.schema import (
    EntityKeyBuildSpecSchema,
    EntityIdsBuildSpecSchema,
)

PredictionColumnSpecSchema = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "is_feature": {"type": "boolean"},
    },
    "required": ["name"],
}


class PropensityModel(BaseModelType):
    TypeName = "propensity"
    BuildSpecSchema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            **EntityKeyBuildSpecSchema["properties"],
            **EntityIdsBuildSpecSchema["properties"],
            "inputs": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "training": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "predict_var": {"type": "string"},
                    "predict_window_days": {"type": "integer"},
                    "max_row_count": {"type": "integer"},
                    "eligible_users": {"type": "string"},
                    "label_value": {"type": "number"},
                    "recall_to_precision_importance": {"type": "number"},
                    "new_materialisations_config": {"type": "object"},
                    "top_k_array_categories": {"type": "integer"},
                    "timestamp_columns": {"type": "array", "items": {"type": "string"}},
                    "arraytype_columns": {"type": "array", "items": {"type": "string"}},
                    "booleantype_columns": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "ignore_features": {"type": "array", "items": {"type": "string"}},
                    "numeric_features": {"type": "array", "items": {"type": "string"}},
                    "categorical_features": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "algorithms": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "type": {
                        "type": "string",
                        "enum": ["classification", "regression"],
                    },
                    "validity": {
                        "type": "string",
                        "enum": ["day", "week", "month"],
                    },
                    "warehouse": {"type": ["string", "null"]},
                    "file_lookup_path": {"type": "string"},
                },
                "required": ["predict_var", "predict_window_days"],
            },
            "prediction": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "output_columns": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "percentile": PredictionColumnSpecSchema,
                            "score": PredictionColumnSpecSchema,
                        },
                        "required": ["percentile", "score"],
                    },
                    "eligible_users": {"type": "string"},
                    "warehouse": {"type": ["string", "null"]},
                },
                "required": ["output_columns"],
            },
        },
        "required": ["training", "prediction", "inputs"]
        + EntityKeyBuildSpecSchema["required"],
    }

    @classmethod
    def sanitize_buildspec(
        cls,
        project_id: int,
        model_type: str,
        build_spec: Dict[Any, Any],
        kickstart: Dict[Any, Any],
        buildspec_ref: int,
    ) -> List[Dict[str, Any]]:
        """
        Sanitize the propensity model buildspec and generate BSN messages.
        This runs during parsing phase to generate child model specs (training and prediction models).

        Returns:
            List of BSN messages for child model creation
        """
        from profiles_rudderstack.tunnel import client as tunnel_client

        # Step 1: Get base messages from Go-side CVBS.Sanitize()
        # This gets LinkCohortFeature messages, etc.
        base_messages = tunnel_client.sanitize_base(
            project_id=project_id,
            buildspec_ref=buildspec_ref,
            model_type=model_type,
        )

        # Step 2: Generate child model specs
        # We need to create training and prediction models
        child_messages = []

        # Get model_name from kickstart (contains context about the model being parsed)
        # For now, we'll extract it from the destination path if available
        # Note: The actual model_name will be set during factory construction
        # Here we just need to signal that children will be created

        # Create training model spec
        training_spec = cls._create_training_spec_static(build_spec)
        training_message = {
            "update_type": "AddChildInfo",
            "destination": None,
            "payload": {
                "build_infos": [
                    {
                        "name": "training",  # Child name (will be nested under parent)
                        "type": "training_model",
                        "build_spec": training_spec,
                    }
                ]
            },
            "context_entity_key": build_spec.get("entity_key", ""),
            "for_parent_project": False,
        }
        child_messages.append(training_message)

        # Create prediction model spec
        # Construct full prediction spec including reference to sibling training model
        prediction_spec = cls._create_prediction_spec_static(build_spec, training_spec)
        prediction_message = {
            "update_type": "AddChildInfo",
            "destination": None,
            "payload": {
                "build_infos": [
                    {
                        "name": "prediction",  # Child name (will be nested under parent)
                        "type": "prediction_model",
                        "build_spec": prediction_spec,
                    }
                ]
            },
            "context_entity_key": build_spec.get("entity_key", ""),
            "for_parent_project": False,
        }
        child_messages.append(prediction_message)

        # Step 4: Create nested column models for ALL output columns via BSN_AddChildInfo
        # This ensures columns are created early (during sanitization) before other models reference them
        output_columns = build_spec["prediction"]["output_columns"]
        nested_column_infos = []
        columns = ["percentile", "score"]
        for column in columns:
            is_feature = output_columns[column].get("is_feature", True)
            col_name = output_columns[column]["name"]
            col_type = 1 if is_feature else 0  # 1=FeatureColumn, 0=ReferredColumn

            nested_col_spec = {
                "entitykey": build_spec[
                    "entity_key"
                ],  # lowercase for YAML unmarshalling
                "description": output_columns[column].get("description", ""),
                "columntype": col_type,
            }
            nested_column_infos.append(
                {
                    "name": col_name,
                    "type": "nested_column",
                    "build_spec": nested_col_spec,
                }
            )

        if nested_column_infos:
            # Send all columns as children of the prediction model
            # Destination [".", "prediction"] means prediction child relative to caller (propensity)
            nested_columns_message = {
                "update_type": "AddChildInfo",
                "destination": {
                    "path": [
                        ".",
                        "prediction",
                    ],  # "." = caller (propensity), "prediction" = child
                },
                "payload": {"build_infos": nested_column_infos},
                "context_entity_key": build_spec.get("entity_key", ""),
                "for_parent_project": False,
            }
            child_messages.append(nested_columns_message)

        # Step 5: Combine base messages + child messages
        all_messages = base_messages + child_messages

        return all_messages

    @staticmethod
    def _create_prediction_spec_static(build_spec: dict, training_spec: dict) -> dict:
        """
        Static helper to create prediction spec during sanitization phase.
        Uses relative path "../training" to reference the sibling training model.
        """
        data = training_spec["ml_config"]["data"].copy()
        output_columns = build_spec["prediction"]["output_columns"]
        features = []
        columns = ["percentile", "score"]
        for column in columns:
            if output_columns[column].get("is_feature", True):
                features.append(
                    {
                        "name": output_columns[column]["name"],
                        "description": output_columns[column].get("description", None),
                    }
                )
        if build_spec["prediction"].get("eligible_users", None) is not None:
            data["eligible_users"] = build_spec["prediction"]["eligible_users"]

        spec = {
            "entity_key": build_spec["entity_key"],
            "training_model": "../training",  # Relative path to sibling training model
            "inputs": build_spec["inputs"],
            "warehouse": build_spec["prediction"].get("warehouse", None),
            "ml_config": {
                "data": data,
                "outputs": {
                    "column_names": {
                        "percentile": output_columns["percentile"]["name"],
                        "score": output_columns["score"]["name"],
                    },
                },
            },
            "features": features,
        }
        if "ids" in build_spec:
            spec["ids"] = build_spec["ids"]
        return spec

    @staticmethod
    def _create_training_spec_static(build_spec: dict) -> dict:
        """
        Static helper to create training spec during sanitization phase.
        This mirrors the logic from _get_training_spec() but doesn't require instance state.
        """
        data = {}
        data["label_column"] = build_spec["training"]["predict_var"]
        data["prediction_horizon_days"] = build_spec["training"]["predict_window_days"]
        training_params = build_spec.get("training", {})

        data["task"] = training_params.get("type", "classification")

        if data["task"] == "classification":
            data["label_value"] = training_params.get("label_value", None)

        data_keys = [
            "eligible_users",
            "max_row_count",
            "recall_to_precision_importance",
            "new_materialisations_config",
        ]
        for key in data_keys:
            data[key] = training_params.get(key, None)

        preprocessing = {}
        preprocessing_keys = [
            "top_k_array_categories",
            "timestamp_columns",
            "arraytype_columns",
            "booleantype_columns",
            "ignore_features",
            "numeric_features",
            "categorical_features",
        ]
        for key in preprocessing_keys:
            preprocessing[key] = training_params.get(key, None)

        # Handle train config
        model_type = training_params.get("type", "classification")
        train_config = None
        if (
            "algorithms" in training_params
            and training_params["algorithms"] is not None
        ):
            if model_type == "classification":
                train_config = {
                    "model_params": {
                        "models": {
                            "include": {
                                "classifiers": training_params["algorithms"],
                            }
                        }
                    }
                }
            elif model_type == "regression":
                train_config = {
                    "model_params": {
                        "models": {
                            "include": {
                                "regressors": training_params["algorithms"],
                            }
                        }
                    }
                }

        ml_config = {"data": data, "preprocessing": preprocessing}
        if train_config is not None:
            ml_config["train"] = train_config

        return {
            "entity_key": build_spec["entity_key"],
            "materialization": build_spec.get("materialization", {}),
            "inputs": build_spec["inputs"],
            "training_file_lookup_path": build_spec["training"].get(
                "file_lookup_path", None
            ),
            "validity_time": build_spec["training"].get("validity", None),
            "warehouse": build_spec["training"].get("warehouse", None),
            "ml_config": ml_config,
        }

    def __init__(
        self,
        build_spec: dict,
        schema_version: int,
        pb_version: str,
        parent_folder: WhtFolder,
        model_name: str,
    ) -> None:
        build_spec["materialization"] = {"output_type": "none"}
        super().__init__(build_spec, schema_version, pb_version)

        # Child specs are now created during sanitize_buildspec() phase
        # Store training_spec for internal use (validation, etc.)
        self.training_spec = self._get_training_spec()

        # Note: training_model_ref and prediction_spec are no longer needed here
        # as child models are created before this constructor runs

    def _get_train_config(self, training_params: dict) -> dict:
        model_type = training_params.get("type", "classification")
        if (
            model_type == "classification"
            and "algorithms" in training_params
            and training_params["algorithms"] is not None
        ):
            return {
                "model_params": {
                    "models": {
                        "include": {
                            "classifiers": training_params["algorithms"],
                        }
                    }
                }
            }
        elif (
            model_type == "regression"
            and "algorithms" in training_params
            and training_params["algorithms"] is not None
        ):
            return {
                "model_params": {
                    "models": {
                        "include": {
                            "regressors": training_params["algorithms"],
                        }
                    }
                }
            }
        else:
            return None

    def _get_training_spec(self) -> dict:
        data = {}
        data["label_column"] = self.build_spec["training"]["predict_var"]
        data["prediction_horizon_days"] = self.build_spec["training"][
            "predict_window_days"
        ]
        training_params = self.build_spec.get("training", {})

        # Map 'type' to 'task' for TrainerFactory compatibility
        data["task"] = training_params.get("type", "classification")

        # Include label_value only for classification tasks
        if data["task"] == "classification":
            data["label_value"] = training_params.get("label_value", None)

        # Include other common data keys
        data_keys = [
            "eligible_users",
            "max_row_count",
            "recall_to_precision_importance",
            "new_materialisations_config",
        ]
        for key in data_keys:
            data[key] = training_params.get(key, None)

        preprocessing = {}
        preprocessing_keys = [
            "top_k_array_categories",
            "timestamp_columns",
            "arraytype_columns",
            "booleantype_columns",
            "ignore_features",
            "numeric_features",
            "categorical_features",
        ]
        for key in preprocessing_keys:
            preprocessing[key] = training_params.get(key, None)

        train_config = self._get_train_config(training_params)

        ml_config = {"data": data, "preprocessing": preprocessing}
        if train_config is not None:
            ml_config["train"] = train_config

        return {
            "entity_key": self.build_spec["entity_key"],
            "materialization": self.build_spec.get("materialization", {}),
            "inputs": self.build_spec["inputs"],
            "training_file_lookup_path": self.build_spec["training"].get(
                "file_lookup_path", None
            ),
            "validity_time": self.build_spec["training"].get("validity", None),
            "warehouse": self.build_spec["training"].get("warehouse", None),
            "ml_config": ml_config,
        }

    def _get_prediction_spec(self, training_model_ref: str) -> dict:
        data = self.training_spec["ml_config"]["data"]
        output_columns = self.build_spec["prediction"]["output_columns"]
        features = []
        columns = ["percentile", "score"]
        for column in columns:
            if output_columns[column].get("is_feature", True):
                features.append(
                    {
                        "name": output_columns[column]["name"],
                        "description": output_columns[column].get("description", None),
                    }
                )
        if self.build_spec["prediction"].get("eligible_users", None) is not None:
            data["eligible_users"] = self.build_spec["prediction"]["eligible_users"]
        spec = {
            "entity_key": self.build_spec["entity_key"],
            "training_model": training_model_ref,
            "inputs": self.build_spec["inputs"],
            "warehouse": self.build_spec["prediction"].get("warehouse", None),
            "ml_config": {
                "data": data,
                "outputs": {
                    "column_names": {
                        "percentile": output_columns["percentile"]["name"],
                        "score": output_columns["score"]["name"],
                    },
                },
            },
            "features": features,
        }
        if "ids" in self.build_spec:
            spec["ids"] = self.build_spec["ids"]
        return spec

    def get_material_recipe(self) -> PyNativeRecipe:
        return NoOpRecipe()

    def validate(self) -> Tuple[bool, str]:
        is_valid, message = super().validate()
        if not is_valid:
            return is_valid, message

        # Validate algorithms if provided
        algorithm_models = (
            self.training_spec["ml_config"]
            .get("train", {})
            .get("model_params", {})
            .get("models", {})
            .get("include", None)
        )
        if algorithm_models:
            config_path = utils.get_model_configs_file_path()
            config = utils.load_yaml(config_path)

            model_type = self.build_spec.get("training", {}).get(
                "type", "classification"
            )
            if model_type == "classification":
                algorithms = algorithm_models["classifiers"]
                supported_algos = config["train"]["model_params"]["models"]["include"][
                    "classifiers"
                ]
            else:
                algorithms = algorithm_models["regressors"]
                supported_algos = config["train"]["model_params"]["models"]["include"][
                    "regressors"
                ]

            # Check if algorithms is None or empty
            if algorithms is None or algorithms == []:
                return (
                    False,
                    f"Error: No algorithms provided in propensity model spec.",
                )

            unsupported = [algo for algo in algorithms if algo not in supported_algos]
            if unsupported:
                return (
                    False,
                    f"Error: Invalid algorithm(s) {unsupported} detected in propensity model spec. Supported algos: {supported_algos}",
                )

        return True, ""
