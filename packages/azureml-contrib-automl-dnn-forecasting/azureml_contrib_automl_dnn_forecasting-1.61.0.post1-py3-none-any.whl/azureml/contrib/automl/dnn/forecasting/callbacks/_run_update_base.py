# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Callbacks which computes and uploads metric to run."""
from abc import abstractmethod
import json
import logging
import os
import platform
from typing import MutableMapping, Any

from overrides import overrides
import pkg_resources
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from azureml.automl.core import inference, package_utilities
from azureml.automl.core.shared import logging_utilities, constants as automl_core_constants
from azureml.automl.core.systemusage_telemetry import SystemResourceUsageTelemetryFactory
from azureml.core.run import Run
from azureml.train.automl.runtime._azureautomlruncontext import AzureAutoMLRunContext
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TCNModelNotConvergent
from forecast.callbacks import Callback
from forecast.callbacks.utils import CallbackDistributedExecMode

from ..constants import ForecastConstant
from ..wrapper.forecast_wrapper import DNNForecastWrapper, DNNParams

logger = logging.getLogger(__name__)


class RunUpdateCallbackBase(Callback):
    """Wraps AutoML metric computation and upload in a callback."""

    def __init__(self,
                 model_wrapper: DNNForecastWrapper,
                 run_context: Run,
                 params: DNNParams):
        """Initialize callback to compute and upload metric to the run context.

        :param model_wrapper: DNNForecastWrapper Model that is being trained
        :param run_context:AutoML run context to be used for uploading model/metrices
        :param X_valid: X validation data used for computing metrices
        :param y_valid: y validation data used for computing metrices
        :param params: DNNParams
        :param featurizer: Trained featurizer
        """
        super().__init__()
        self.model_wrapper = model_wrapper
        self.run_context = run_context
        self.params = params
        self._exception_count = 0
        self.telemetry_logger = SystemResourceUsageTelemetryFactory.get_system_usage_telemetry(interval=10)
        self.automl_run_context = AzureAutoMLRunContext(self.run_context)
        # Add properties required for automl UI.
        run_properties_for_ui = {"runTemplate": "automl_child",
                                 "run_preprocessor": "",
                                 "run_algorithm": self.model_wrapper.name,
                                 ForecastConstant.primary_metric: model_wrapper.primary_metric}
        self.run_context.add_properties(run_properties_for_ui)

        self.report_interval = params.get_value(ForecastConstant.report_interval)
        self.num_epochs = params.get_value(ForecastConstant.num_epochs)
        self.num_epochs_done = 0
        self._last_epoch_scores = None

    def upload_model_and_tabular_metrics(self) -> None:
        """Upload the model and compute and upload the tabular metrics."""
        if self._exception_count > 0:
            logger.error("model does not have any valid score")
            raise ClientException._with_error(AzureMLError.create(
                TCNModelNotConvergent, target="X",
                reference_code=ReferenceCodes._TCN_MODEL_NOT_CONVERGENT)
            )
        if self._is_validation_data_available():
            self.upload_properties_tabular_metrics()
        self.upload_model()

    @abstractmethod
    def _is_validation_data_available(self) -> bool:
        raise NotImplementedError()

    def _get_primary_metric_score(self, scores: MutableMapping[str, Any]) -> float:
        primary_metric = self.model_wrapper.primary_metric
        score = scores.get(primary_metric, None)
        if score is None:
            logger.warning(f"Primary metric '{primary_metric}' is missing from the scores")
            score = float("nan")
        return score

    def upload_properties_tabular_metrics(self) -> None:
        """On train end set to upload tabular metrics.

        :param y_pred: predicted target values
        :param y_test: actual target values
        """
        # upload tabular metrics
        # Add the score that is mandatory for the ui to show the run in UI
        score = self._get_primary_metric_score(self._last_epoch_scores)
        self.run_context.add_properties({"score": float(score)})

    def upload_model(self) -> None:
        """Upload dnn model to run context."""
        model_id = self._get_model_id(self.run_context.id)
        self._save_model_for_automl_inference(model_id, self.model_wrapper)

    @abstractmethod
    def _get_sample_data_json(self) -> str:
        raise NotImplementedError

    def _get_inference_file_content(self) -> str:
        # generate sample data for scoring file, by looking at first row fom sample data
        input_json = self._get_sample_data_json()
        return self._get_scoring_file(input_json)

    # this code has to be refactored in automl sdk where it can take the model and context and save
    # all inferencing related data
    def _save_model_for_automl_inference(self, model_id: str,
                                         model: DNNForecastWrapper) -> None:
        """Save model and runproperties needed for inference.

        :param model_id: the unique id for identifying the model with in the workspace.
        :param model: model to save in artifact.
        :return:
        """
        all_dependencies = package_utilities._all_dependencies()

        # Initialize the artifact data dictionary for the current run
        strs_to_save = {automl_core_constants.RUN_ID_OUTPUT_PATH: self.run_context.id}

        # save versions to artifacts
        strs_to_save[ForecastConstant.automl_constants.DEPENDENCIES_PATH] = json.dumps(all_dependencies, indent=4)

        # save conda environment file into artifacts
        try:
            strs_to_save[ForecastConstant.automl_constants.CONDA_ENV_FILE_PATH] = self._create_conda_env_file_content()
        except Exception as e:
            logger.warning("Failed to create conda environment file.")
            logging_utilities.log_traceback(e, logger, is_critical=False)

        # save scoring file into artifacts
        try:
            scoring_file_str_v1, scoring_file_str_v2 = self._get_inference_file_content()
            strs_to_save[ForecastConstant.automl_constants.SCORING_FILE_PATH] = scoring_file_str_v1
            strs_to_save[ForecastConstant.automl_constants.SCORING_FILE_V2_PATH] = scoring_file_str_v2
            # As TCN does not support forecast_quantile yet, we use the SCORING_FILE_V2_PATH as the PBI inference
            # file.
            strs_to_save[ForecastConstant.automl_constants.SCORING_FILE_PBI_V1_PATH] = scoring_file_str_v2
        except Exception as e:
            logger.warning("Failed to create score inference file.")
            logging_utilities.log_traceback(e, logger, is_critical=False)

        # Upload files to artifact store
        models_to_upload = {automl_core_constants.PT_MODEL_PATH: model}

        # Default to save mlflow model unless the customer set it to false.
        save_as_mlflow = True
        try:
            # This code makes 3 network calls, we may want to optimize it away and consume save_mlflow some other way
            automl_settings = self.run_context.parent.parent.get_properties().get('AMLSettingsJsonString', "{}")
            if json.loads(automl_settings).get("save_mlflow", True) is False:
                save_as_mlflow = False
        except Exception:
            logger.warning("Could not load AutoMLSettings from parent run.")

        with logging_utilities.log_activity(logger=logger, activity_name='Save artifacts'):
            logger.info(f"Save MLFlow: [{save_as_mlflow}]")
            mlflow_options = {
                automl_core_constants.MLFlowLiterals.SCHEMA_SIGNATURE: None,
                automl_core_constants.MLFlowLiterals.FLAVOR_FORECASTING: True
            }
            self.automl_run_context.batch_save_artifacts(
                working_directory=os.getcwd(),
                input_strs=strs_to_save,
                model_outputs=models_to_upload,
                save_as_mlflow=save_as_mlflow,
                mlflow_options=mlflow_options)

        # save artifact ids as properties
        properties_to_add = {
            inference.AutoMLInferenceArtifactIDs.CondaEnvDataLocation:
                self.automl_run_context._get_artifact_id(ForecastConstant.automl_constants.CONDA_ENV_FILE_PATH),
            inference.AutoMLInferenceArtifactIDs.ModelDataLocation:
                self.automl_run_context._get_artifact_id(automl_core_constants.PT_MODEL_PATH),
            inference.AutoMLInferenceArtifactIDs.ScoringDataLocation:
                self.automl_run_context._get_artifact_id(ForecastConstant.automl_constants.SCORING_FILE_PATH),
            inference.AutoMLInferenceArtifactIDs.ScoringDataLocationV2:
                self.automl_run_context._get_artifact_id(ForecastConstant.automl_constants.SCORING_FILE_V2_PATH),
            inference.AutoMLInferenceArtifactIDs.ScoringDataLocationPBI:
                self.automl_run_context._get_artifact_id(ForecastConstant.automl_constants.SCORING_FILE_PBI_V1_PATH),
            inference.AutoMLInferenceArtifactIDs.ModelName: model_id
        }

        # automl code saves the graph json for the pipeline. Todo add code to save the model graph.

        self.automl_run_context._run.add_properties(properties_to_add)

    def _get_model_id(self, runid: str) -> str:
        """Generate a model name from runid.

        :param runid:  runid string of the hyperdrive child run.
        :return: the id produced by taking run number and last 12 chars from hyperdrive runid.
        """
        name = 'DNN'
        parent_num_part = ''
        child_num = ''
        if runid:
            parts = runid.split("_")
            if len(parts) > 0:
                child_num = parts[-1]
            if "Offline" in runid and len(parts) > 1:
                # Example run id for offline run is- 'OfflineRun_d383aab5-7ecf-422e-abf9-a9f5ee2e78fb'
                # In this case, parent_num_part should be a9f5ee2e78fb.
                parent_num_part = parts[-2][-12:]
            elif len(parts) > 1:
                # Example run id is- AutoML_36628647-299e-4630-871b-fc7177fb2745_HD_3
                # If we split it by "_", we get AutoML, 36628647-299e-4630-871b-fc7177fb2745, HD and 3.
                # Parent_num_part should be fc7177fb2745. Hence, parts[-3][-12:] is used.
                parent_num_part = parts[-3][-12:]

        return name + parent_num_part + child_num

    def _get_scoring_file(self, input_sample_str: str = "pd.DataFrame()") -> str:
        """
        Return scoring file to be used at the inference time.

        If there are any changes to the scoring file, the version of the scoring file should
        be updated in the vendor.

        :return: Scoring python file as a string
        """
        inference_data_type = inference.inference.PandasParameterType

        content_v1 = self._format_scoring_file('score_forecasting_dnn.txt', inference_data_type, input_sample_str)
        content_v2 = self._format_scoring_file('score_forecasting_dnn_v2.txt', inference_data_type, input_sample_str)

        return content_v1, content_v2

    def _format_scoring_file(self, filename: str, inference_data_type: str, input_sample_str: str) -> str:
        scoring_file_path = pkg_resources.resource_filename(
            inference.inference.PACKAGE_NAME, os.path.join('inference', filename))
        content = None
        with open(scoring_file_path, 'r') as scoring_file_ptr:
            content = scoring_file_ptr.read()
            content = content.replace('<<ParameterType>>', inference_data_type)
            content = content.replace('<<input_sample>>', input_sample_str)
            content = content.replace('<<model_filename>>', automl_core_constants.PT_MODEL_FILENAME)

        return content

    def _create_conda_env_file_content(self) -> str:
        """
        Return conda/pip dependencies for the current AutoML run.

        If there are any changes to the conda environment file, the version of the conda environment
        file should be updated in the vendor.

        :return: Conda dependencies as string
        """
        from azureml.core.conda_dependencies import CondaDependencies
        sdk_dependencies = package_utilities._all_dependencies()
        pip_package_list_with_version = []
        automl_forecast_dnn_package = ['azureml-contrib-automl-dnn-forecasting']
        azureml_version = ""
        need_azureml_defaults = False
        for pip_package in inference.AutoMLPipPackagesList + automl_forecast_dnn_package:
            if 'azureml' in pip_package and pip_package in sdk_dependencies:
                pip_package_list_with_version.append(pip_package + "==" + sdk_dependencies[pip_package])
                azureml_version = sdk_dependencies[pip_package]
            # We are taking all the dependencies as working set i.e. we ask, what package and version is
            # installed on the environment we are in. In the tests we are not guaranteed to have azureml-defaults
            # installed, because this environment is build dynamically. To fix it, we will remember that
            # we need this package and azureml version.
            elif 'azureml-defaults' in pip_package:
                need_azureml_defaults = True
            else:
                pip_package_list_with_version.append(pip_package)
        if need_azureml_defaults:
            package = "azureml_defaults"
            if azureml_version:
                package = "".join([package, "==", azureml_version])
            pip_package_list_with_version.append(package)
        AutoMLCondaPackagesList = inference.AutoMLCondaPackagesList
        AutoMLCondaPackagesList.append("pytorch>=1.2")

        myenv = CondaDependencies.create(conda_packages=AutoMLCondaPackagesList,
                                         pip_packages=pip_package_list_with_version,
                                         python_version=platform.python_version(),
                                         pin_sdk_version=False)
        myenv.add_channel("pytorch")
        return myenv.serialize_to_string()

    @staticmethod
    @overrides
    def get_distributed_exec_mode() -> CallbackDistributedExecMode:
        """Get the execution mode of callback, here only on rank_0 for metrics upload."""
        return CallbackDistributedExecMode.RANK_0
