import os
import re
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Sequence, Tuple
from copy import deepcopy

from .rudderPB import MATERIAL_PREFIX, RudderPB
from .mockPB import MockPB

from ..utils import utils
from ..utils.constants import TrainTablesInfo, MATERIAL_DATE_FORMAT
from ..utils.logger import logger
from ..connectors.Connector import Connector
from ..trainers.MLTrainer import MLTrainer
from profiles_rudderstack.material import WhtMaterial


def split_key(item):
    parts = item.split("_")
    if len(parts) > 1 and parts[-1].isdigit():
        return int(parts[-1])
    return 0


class PyNativeWHT:
    def __init__(
        self, whtMaterial: WhtMaterial, site_config_path: str, project_folder_path: str
    ) -> None:
        self.connector = None
        self.site_config_path = site_config_path
        self.project_folder_path = project_folder_path
        self.whtMaterial = whtMaterial
        self.cached_registry_table_name = ""
        self.begin_time = self._get_begin_time()

    def _get_begin_time(self) -> Optional[str]:
        """
        Retrieve begin_time from wht_ctx.time_info().
        Returns the begin_time as a unix timestamp string if available, None otherwise.
        """
        try:
            start_date, _ = self.whtMaterial.wht_ctx.time_info()
            if start_date is not None:
                unix_timestamp = int(start_date.timestamp())
                return str(unix_timestamp)
            return None
        except Exception as e:
            logger.get().debug(f"Could not retrieve begin_time from wht_ctx: {e}")
            return None

    def set_connector(
        self,
        connector: Connector,
    ) -> None:
        self.connector = connector

    def get_date_range(
        self, creation_ts: datetime, prediction_horizon_days: int
    ) -> Tuple:
        def _get_date_range(
            created_at: datetime, prediction_horizon_days: int
        ) -> Tuple:
            start_date = created_at - timedelta(days=2 * prediction_horizon_days)
            end_date = created_at - timedelta(days=prediction_horizon_days)
            if isinstance(start_date, datetime):
                start_date = start_date.date()
                end_date = end_date.date()
            return str(start_date), str(end_date)

        start_date, end_date = self.whtMaterial.wht_ctx.time_info()
        if end_date is None:
            start_date, end_date = _get_date_range(creation_ts, prediction_horizon_days)
        else:
            if (start_date is None) or (
                start_date is not None
                and (end_date - start_date)
                >= timedelta(days=2 * prediction_horizon_days)
            ):
                start_date, end_date = _get_date_range(
                    end_date, prediction_horizon_days
                )
            elif start_date is not None and (end_date - start_date) < timedelta(
                days=2 * prediction_horizon_days
            ):
                raise Exception(
                    f"begin_time and end_time needs to be atleast {2*prediction_horizon_days} days apart for the predictive feature {self.whtMaterial.model.name()} with prediction_horizon_days: {prediction_horizon_days}"
                )

        return str(start_date), str(end_date)

    def get_model_hash(self) -> str:
        return self.whtMaterial.model.hash()

    def get_latest_entity_var_table(self, entity_key: str) -> Tuple[str, str, str]:
        model_ref = f"entity/{entity_key}/var_table"
        material = self.whtMaterial.de_ref(model_ref)
        if material is None:
            raise Exception(f"Material not found for model ref: {model_ref}")
        material_split = self.split_material_name(material.name())
        creation_ts = self.get_model_creation_ts(
            material_split["model_hash"],
            entity_key,
        )
        return material_split["model_hash"], material_split["model_name"], creation_ts

    def get_column_name(self, model_ref):
        column_name = self.whtMaterial.de_ref(model_ref).model.db_object_name_prefix()
        return column_name

    def update_config_info(self, merged_config):
        entity = self.whtMaterial.model.entity()
        merged_config["data"]["entity_key"] = entity["Name"]
        merged_config["data"]["entity_column"] = (
            self.connector.get_entity_column_case_corrected(entity["IdColumnName"])
        )
        merged_config["data"][
            "output_profiles_ml_model"
        ] = self.whtMaterial.model.name()
        self.connector.feature_table_name = f"{self.whtMaterial.name()}_feature_table"
        merged_config["data"]["label_column"] = self.get_column_name(
            merged_config["data"]["label_column"]
        )
        return merged_config

    def get_end_ts(self) -> str:
        _, end_ts = self.whtMaterial.wht_ctx.time_info()
        return str(end_ts)

    def get_material_names(
        self,
        start_date: str,
        end_date: str,
        prediction_horizon_days: int,
        inputs: List[utils.InputsConfig],
        input_columns: List[str],
        entity_column: str,
        return_partial_pairs: bool = False,
        feature_data_min_date_diff: int = 3,
    ) -> List[TrainTablesInfo]:
        """
        Retrieves the names of the feature and label tables, as well as their corresponding training dates, based on the provided inputs.
        If no materialized data is found within the specified date range, the function attempts to materialize the feature and label data using the `materialise_past_data` function.
        If no materialized data is found even after materialization, an exception is raised.

        Returns:
            List[TrainTablesInfo]: A list of TrainTablesInfo objects, each containing the names of the feature and label tables, as well as their corresponding training dates.
        """

        def get_complete_sequences(sequences: List[Sequence]) -> int:
            """
            A sequence is said to be complete if it does not have any Nones.
            """
            complete_sequences = [
                sequence
                for sequence in sequences
                if all(element is not None for element in sequence)
            ]
            return complete_sequences

        logger.get().info("getting material names")
        (materials) = self._get_material_names(
            start_date,
            end_date,
            prediction_horizon_days,
            inputs,
            input_columns,
            entity_column,
            return_partial_pairs,
        )

        # If we want to include partial pairs, we dont need to look for full valid sequences
        if return_partial_pairs:
            return self.get_past_materials_with_valid_date_range(
                materials, prediction_horizon_days, feature_data_min_date_diff
            )

        if len(get_complete_sequences(materials)) == 0:
            self._generate_training_materials(
                materials,
                start_date,
                prediction_horizon_days,
                inputs,
            )
            (materials) = self._get_material_names(
                start_date,
                end_date,
                prediction_horizon_days,
                inputs,
                input_columns,
                entity_column,
            )

        complete_sequences_materials = get_complete_sequences(materials)
        if len(complete_sequences_materials) == 0:
            raise Exception(
                f"Tried to materialise past data but no materialized data found for given inputs between dates {start_date} and {end_date}. Materials partial list: {materials}"
            )

        return self.get_past_materials_with_valid_date_range(
            complete_sequences_materials,
            prediction_horizon_days,
            feature_data_min_date_diff,
        )

    def run(self, feature_package_path: str, unix_timestamp: str):
        # Validate that we're not trying to materialize for future dates
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_date_unix_timestamp = utils.convert_date_to_unix_str(
            current_date, add_jitter=False
        )

        if int(unix_timestamp) > int(current_date_unix_timestamp):
            materialization_date = datetime.fromtimestamp(
                int(unix_timestamp), timezone.utc
            ).strftime(MATERIAL_DATE_FORMAT)
            logger.get().warn(
                f"Skipping materialization run as the Propensity model is attempting to materialize for future dates with Materialization date: {materialization_date}."
            )
            return

        args = {
            "feature_package_path": feature_package_path,
            "features_valid_time": unix_timestamp,
            "site_config_path": self.site_config_path,
            "project_folder": self.project_folder_path,
        }

        if self.begin_time is not None:
            args["begin_time"] = self.begin_time

        date = datetime.fromtimestamp(int(unix_timestamp), timezone.utc).strftime(
            MATERIAL_DATE_FORMAT
        )
        logger.get().info(f"Running profiles project for date {date}")
        self._getPB().run(args)
        logger.get().info(f"Ran profiles project for date {date} successfully.")

    def compute_material_name(
        self, model_name: str, model_hash: str, seq_no: int
    ) -> str:
        return f"{MATERIAL_PREFIX}{model_name}_{model_hash}_{seq_no:.0f}"

    def get_registry_table_name(self) -> str:
        if self.cached_registry_table_name == "":
            material_registry_tables = self.connector.get_tables_by_prefix(
                "MATERIAL_REGISTRY"
            )

            sorted_material_registry_tables = sorted(
                material_registry_tables, key=split_key, reverse=True
            )
            self.cached_registry_table_name = sorted_material_registry_tables[0]
        return self.cached_registry_table_name

    def get_latest_seq_no(self, inputs: List[utils.InputsConfig]) -> int:
        return int(inputs[0].table_name.split("_")[-1])

    def get_inputs(self, input_model_refs: List[str]) -> List[utils.InputsConfig]:
        inputs: List[utils.InputsConfig] = []
        for input_model_ref in input_model_refs:
            material = self.whtMaterial.de_ref(input_model_ref)
            # if material.model.model_type() == "sql_template":
            #     material = self.whtMaterial.de_ref(input_model_ref + "/var_table")
            #     id_column_name = self.whtMaterial.model.entity()["IdColumnName"]
            #     self.whtMaterial.de_ref(input_model_ref + f"/var_table/{id_column_name}")
            column_name = None
            if material.model.materialization()["output_type"] == "column":
                column_name = material.model.db_object_name_prefix()
                table_material_ref = (
                    material.model.encapsulating_model().model_ref_from_level_root()
                )
                table_material = self.whtMaterial.de_ref(table_material_ref)
            else:
                table_material = material
            material_name_dict = self.split_material_name(material.name())

            input = {
                "table_name": table_material.name(),
                "model_ref": material.model.model_ref(),
                "model_type": material.model.model_type(),
                "selector_sql": material.get_selector_sql(),
                "column_name": column_name,
                # FIXME: Once python model is removed, get rid of model_name and replace it with model_ref
                "model_name": material.model.name(),
                "model_hash": material_name_dict["model_hash"],
            }
            inputs.append(utils.InputsConfig(**input))
        return inputs

    def validate_sql_table(
        self, inputs: List[utils.InputsConfig], entity_column: str
    ) -> None:
        for input in inputs:
            if input.model_type == "sql_template":
                self.connector.validate_sql_table(input.table_name, entity_column)

    def get_credentials(self, project_path: str, site_config_path: str) -> str:
        connection_name = utils.load_yaml(
            os.path.join(project_path, "pb_project.yaml")
        )["connection"]
        connection = utils.load_yaml(site_config_path)["connections"][connection_name]
        return connection["outputs"][connection["target"]]

    def check_and_generate_more_materials(
        self,
        get_material_func: callable,
        materials: List[TrainTablesInfo],
        inputs: List[utils.InputsConfig],
        trainer: MLTrainer,
    ):
        met_data_requirement = trainer.check_min_data_requirement(
            self.connector, materials
        )

        logger.get().info(f"Min data requirement satisfied: {met_data_requirement}")
        if met_data_requirement or trainer.materialisation_strategy == "":
            return materials

        model_refs = [input_.model_ref for input_ in inputs]
        feature_package_path = utils.get_feature_package_path(model_refs)
        max_materializations = (
            trainer.materialisation_max_no_dates
            if trainer.materialisation_strategy == "auto"
            else len(trainer.materialisation_dates)
        )

        logger.get().info(
            f"""Generating snapshots of past data by doing a profiles run on input models, at different points of time in the past. 
                                Expected to run max of {2 * max_materializations} runs."""
        )
        for i in range(max_materializations):
            feature_date = None
            label_date = None

            if trainer.materialisation_strategy == "auto":
                training_dates = [
                    utils.datetime_to_date_string(m.feature_table_date)
                    for m in materials
                ]
                training_dates = [
                    date_str for date_str in training_dates if len(date_str) != 0
                ]
                logger.get().info(f"training_dates : {training_dates}")
                training_dates = sorted(
                    training_dates,
                    key=lambda x: datetime.strptime(x, MATERIAL_DATE_FORMAT),
                    reverse=True,
                )

                max_feature_date = training_dates[0]
                min_feature_date = training_dates[-1]

                feature_date, label_date = utils.generate_new_training_dates(
                    max_feature_date,
                    min_feature_date,
                    training_dates,
                    trainer.prediction_horizon_days,
                    trainer.feature_data_min_date_diff,
                )
                logger.get().info(
                    f"new generated dates for feature: {feature_date}, label: {label_date}"
                )
            elif trainer.materialisation_strategy == "manual":
                dates = trainer.materialisation_dates[i].split(",")
                if len(dates) >= 2:
                    feature_date = dates[0]
                    label_date = dates[1]

                if feature_date is None or label_date is None:
                    continue

            logger.get().info(
                f"Looking for past data on dates {feature_date} and {label_date}. Will do a profiles run if they are not present."
            )
            try:
                # Check wether the materialisation is already present
                existing_materials = get_material_func(
                    start_date=feature_date,
                    end_date=feature_date,
                    return_partial_pairs=True,
                )

                if len(existing_materials) > 0:
                    # Check if any full sequence is exist or not
                    complete_sequences = [
                        sequence
                        for sequence in existing_materials
                        if all(element is not None for element in sequence)
                    ]

                    if len(complete_sequences) < 1:
                        existing_material = existing_materials[0]
                        if existing_material.feature_table_date is None:
                            feature_unix_timestamp = utils.convert_date_to_unix_str(
                                feature_date, add_jitter=True
                            )
                            self.run(feature_package_path, feature_unix_timestamp)

                        if existing_material.label_table_date is None:
                            label_unix_timestamp = utils.convert_date_to_unix_str(
                                label_date, add_jitter=True
                            )
                            self.run(feature_package_path, label_unix_timestamp)
                else:
                    for date in [feature_date, label_date]:
                        unix_timestamp = utils.convert_date_to_unix_str(
                            date, add_jitter=True
                        )
                        self.run(feature_package_path, unix_timestamp)
            except Exception as e:
                logger.get().error(str(e))
                logger.get().error("Stopped generating new material dates.")
                break

            logger.get().info(
                "Materialised feature and label data successfully, "
                f"for dates {feature_date} and {label_date}"
            )

            # Get materials with new feature start date
            # and validate min data requirement again

            # For manual strategy, we need to get the materials for the selected dates separately
            # because the selected dates may not be in the search window. so searching for materials
            # with "feature_date" as start and end date.

            # This logic will be valid for "auto" strategy as well, so we are not handling it separately.
            materials += get_material_func(
                start_date=feature_date, end_date=feature_date
            )

            logger.get().info(
                f"new feature tables: {[m.feature_table_name for m in materials]}"
            )
            logger.get().info(
                f"new label tables: {[m.label_table_name for m in materials]}"
            )
            if (
                trainer.materialisation_strategy == "auto"
                and trainer.check_min_data_requirement(self.connector, materials)
            ):
                logger.get().info("Minimum data requirement satisfied.")
                break
        if not trainer.check_min_data_requirement(self.connector, materials):
            logger.get().error(
                "Minimum data requirement not satisfied. Model performance may suffer. Try adding more datapoints by including more dates or increasing max_no_of_dates in the config."
            )

        return materials

    def _getPB(self):
        mock = False
        if mock:
            return MockPB()
        return RudderPB()

    def split_material_name(self, name: str) -> dict:
        # TODO - Move this logic to bigquery conenctor
        if "`" in name:  # BigQuery case table name
            table_name = name.split("`")[-2]
        elif '"' in name:  # Redshift case table name
            table_name = name.split('"')[-2]
        else:
            table_name = name.split()[-1]

        if "." in table_name:
            table_name = table_name.split(".")[-1]
        table_suffix = table_name.strip("\"'")
        split_parts = table_suffix.split("_")
        try:
            seq_no = int(split_parts[-1])
        except ValueError:
            raise Exception(f"Unable to extract seq_no from material name {name}")
        model_hash = split_parts[-2]
        material_prefix = split_parts[0]
        model_name = "_".join(split_parts[1:-2])
        return {
            "model_name": model_name,
            "model_hash": model_hash,
            "seq_no": seq_no,
        }

    def get_model_creation_ts(self, model_hash: str, entity_key: str):
        return self.connector.get_creation_ts(
            self.get_registry_table_name(),
            model_hash,
            entity_key,
        )

    def get_past_inputs(self, inputs: List[utils.InputsConfig], seq_no: int):
        past_inputs = []
        for input_ in inputs:
            past_input = deepcopy(input_)
            past_input.table_name = utils.replace_seq_no_in_query(
                past_input.table_name, int(seq_no)
            )
            past_inputs.append(past_input)
        return past_inputs

    def get_past_materials_with_valid_date_range(
        self,
        materials: List[TrainTablesInfo],
        prediction_horizon_days: int,
        feature_data_min_date_diff,
    ):
        valid_feature_dates = []
        valid_materials = []

        for material in materials:
            feature_date = None
            if material.feature_table_date != "None":
                feature_date = material.feature_table_date
            elif material.label_table_date != "None":
                feature_date = utils.date_add(
                    material.label_table_date, -1 * prediction_horizon_days
                )

            if feature_date is None:
                continue

            sorted_feature_dates = sorted(
                valid_feature_dates,
                key=lambda x: datetime.strptime(x, MATERIAL_DATE_FORMAT),
                reverse=True,
            )
            is_valid_date = utils.dates_proximity_check(
                feature_date, sorted_feature_dates, feature_data_min_date_diff
            )

            if is_valid_date:
                valid_feature_dates.append(feature_date)
                valid_materials.append(material)

        return valid_materials

    def _validate_historical_materials_hash(
        self,
        input: utils.InputsConfig,
        material_seq_no: Optional[int],
        material_registry_table=None,
    ) -> bool:
        """
        We need to validate if the historic tables were generated by the same model
        that is generating current table.
        We do that by checking the input tables and replacing
        the current seq no with historic seq nos and verify those tables exist.
        This relies on the input sql queries sent by profiles which point to the current materialised tables.

        Returns:
            bool: True if the material table exists with given seq no else False
        """
        # This check is for entity var item input in python model.
        # Without the hash, there is nothing to verify in the registry table.
        # So we assume that the var table contains this var item.
        if input.model_hash is None:
            return True
        try:
            # Replace the last seq_no with the current seq_no
            # and prepare sql statement to check for the table existence
            # Ex. select * from material_shopify_user_features_fa138b1a_785 limit 1
            model_name = input.model_name
            model_hash = input.model_hash
            if material_seq_no is not None:
                seq = int(material_seq_no)
                assert self.connector.check_table_entry_in_material_registry(
                    self.get_registry_table_name(),
                    {"model_name": model_name, "model_hash": model_hash, "seq_no": seq},
                    material_registry_table,
                ), f"Material registry entry for model name - {model_name}, model hash - {model_hash}, seq - {seq} does not exist."

                past_material_name = utils.replace_seq_no_in_query(
                    input.table_name, seq
                )
                assert self.connector.is_valid_table(
                    past_material_name
                ), f"Table {past_material_name} does not exist in the warehouse."
                return True
            else:
                return False
        except AssertionError as e:
            logger.get().info(
                f"{e}. Skipping the sequence {material_seq_no} as it is not valid."
            )
            return False

    def _fetch_valid_historic_materials(
        self,
        table_row,
        inputs,
        input_columns,
        entity_column,
        materials,
        return_partial_pairs: bool = False,
        material_registry_table=None,
    ):
        found_feature_material, found_label_material = True, True

        for input_ in inputs:
            if found_feature_material:
                found_feature_material = self._validate_historical_materials_hash(
                    input_,
                    table_row.FEATURE_SEQ_NO,
                    material_registry_table,
                )
            if found_label_material:
                found_label_material = self._validate_historical_materials_hash(
                    input_,
                    table_row.LABEL_SEQ_NO,
                    material_registry_table,
                )
            # Both not found in the warehouse (no point in including invalid pairs)
            if not found_feature_material and not found_label_material:
                return

        # One of them is not found in the warehouse and we don't want to include invalid pairs
        # Other possibilities are:
        # feature found + label found + return_partial_pairs = Final result
        #  True         + False       + False                 = Exit
        #  False        + True        + False                 = Exit
        #  True         + False       + True                  = Continue
        #  False        + True        + True                  = Continue
        #  True         + True        + False                 = Continue
        if (
            not (found_feature_material and found_label_material)
            and not return_partial_pairs
        ):
            return

        feature_table_date = (
            table_row.FEATURE_END_TS.strftime(MATERIAL_DATE_FORMAT)
            if found_feature_material
            else None
        )

        label_table_date = (
            table_row.LABEL_END_TS.strftime(MATERIAL_DATE_FORMAT)
            if found_label_material
            else None
        )

        feature_past_table_name = (
            f"{self.connector.feature_table_name}_{int(table_row.FEATURE_SEQ_NO)}"
            if found_feature_material
            else None
        )
        label_past_table_name = (
            f"{self.connector.feature_table_name}_{int(table_row.LABEL_SEQ_NO)}"
            if found_label_material
            else None
        )

        for flag, seq_no, target_table_name in zip(
            (found_feature_material, found_label_material),
            (table_row.FEATURE_SEQ_NO, table_row.LABEL_SEQ_NO),
            (feature_past_table_name, label_past_table_name),
        ):
            if flag:
                past_inputs = self.get_past_inputs(inputs, seq_no)
                self.connector.join_input_tables(
                    past_inputs,
                    input_columns,
                    entity_column,
                    target_table_name,
                )

        train_table_info = TrainTablesInfo(
            feature_table_name=feature_past_table_name,
            feature_table_date=feature_table_date,
            label_table_name=label_past_table_name,
            label_table_date=label_table_date,
        )
        materials.append(train_table_info)

    def _get_material_names(
        self,
        start_time: str,
        end_time: str,
        prediction_horizon_days: int,
        inputs: List[utils.InputsConfig],
        input_columns: List[str],
        entity_column: str,
        return_partial_pairs: bool = False,
        feature_data_min_date_diff: int = 3,
    ) -> List[TrainTablesInfo]:
        """Generates material names as list containing feature table name and label table name
            required to create the training model and their corresponding training dates.

        Returns:
            List[TrainTablesInfo]: A list of TrainTablesInfo objects,
            each containing the names of the feature and label tables, as well as their corresponding training dates.
        """
        registry_table = self.connector.get_material_registry_table(
            self.get_registry_table_name()
        )
        feature_label_df = self.connector.join_feature_label_tables(
            self.get_registry_table_name(),
            inputs[0].model_name,
            inputs[0].model_hash,
            start_time,
            end_time,
            prediction_horizon_days,
            registry_table,
        )

        materials = list()
        for row in feature_label_df:
            self._fetch_valid_historic_materials(
                row,
                inputs,
                input_columns,
                entity_column,
                materials,
                return_partial_pairs,
                material_registry_table=registry_table,
            )

        return materials

    def _get_valid_feature_label_dates(
        self,
        materials,
        start_date,
        prediction_horizon_days,
    ):
        if len(materials) == 0:
            feature_date = utils.date_add(start_date, prediction_horizon_days)
            label_date = utils.date_add(feature_date, prediction_horizon_days)
            return feature_date, label_date

        feature_date, label_date = None, None
        for material_info in materials:
            if (
                material_info.feature_table_name is not None
                and material_info.label_table_name is None
            ):
                feature_table_name_ = material_info.feature_table_name
                assert (
                    self.connector.is_valid_table(feature_table_name_) is True
                ), f"Failed to fetch \
                    valid feature_date and label_date because table {feature_table_name_} does not exist in the warehouse"
                label_date = utils.date_add(
                    material_info.feature_table_date.split()[0],
                    prediction_horizon_days,
                )
            elif (
                material_info.feature_table_name is None
                and material_info.label_table_name is not None
            ):
                label_table_name_ = material_info.label_table_name
                assert (
                    self.connector.is_valid_table(label_table_name_) is True
                ), f"Failed to fetch \
                    valid feature_date and label_date because table {label_table_name_} does not exist in the warehouse"
                feature_date = utils.date_add(
                    material_info.label_table_date.split()[0],
                    -prediction_horizon_days,
                )
            elif (
                material_info.feature_table_name is None
                and material_info.label_table_name is None
            ):
                feature_date = utils.date_add(start_date, prediction_horizon_days)
                label_date = utils.date_add(feature_date, prediction_horizon_days)
            else:
                logger.get().exception(
                    f"We don't need to fetch feature_date and label_date to materialise new datasets because Tables {material_info.feature_table_name} and {material_info.label_table_name} already exist. Please check generated materials for discrepancies."
                )
                raise Exception(
                    f"We don't need to fetch feature_date and label_date to materialise new datasets because Tables {material_info.feature_table_name} and {material_info.label_table_name} already exist. Please check generated materials for discrepancies."
                )
        return feature_date, label_date

    def _generate_training_materials(
        self,
        materials: List[TrainTablesInfo],
        start_date: str,
        prediction_horizon_days: int,
        inputs: List[utils.InputsConfig],
    ) -> None:
        """
        Generates training dataset from start_date and end_date, and fetches the resultant table names from the material_table.

        Returns:
            Tuple[str, str]: A tuple containing feature table date and label table date strings
        """
        model_refs = [input_.model_ref for input_ in inputs]
        feature_package_path = utils.get_feature_package_path(model_refs)
        feature_date, label_date = self._get_valid_feature_label_dates(
            materials,
            start_date,
            prediction_horizon_days,
        )

        materialise_data = True
        for date in [feature_date, label_date]:
            # TODO: Check if we are honoring material registry table at this point. we are likely generating it even if the data exists on this date.
            if date is not None:
                unix_timestamp = utils.convert_date_to_unix_str(date, add_jitter=True)
                self.run(feature_package_path, unix_timestamp)

        if not materialise_data:
            logger.get().error(
                "Failed to materialise feature and label data. Will attempt to fetch materialised data from warehouse registry table"
            )
