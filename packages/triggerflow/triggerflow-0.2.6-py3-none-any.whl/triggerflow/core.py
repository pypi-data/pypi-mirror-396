from pathlib import Path
import json
import yaml
import numpy as np
import tarfile
import importlib
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union
import shutil, warnings
import importlib.resources as pkg_resources
import triggerflow.templates 
from triggerflow.interfaces.uGT import build_ugt_model


class ModelConverter(ABC):
    """Abstract base class for model converters"""
    
    @abstractmethod
    def convert(self, model, workspace: Path, **kwargs) -> Optional[Path]:
        """Convert model to intermediate format"""
        pass


class CompilerStrategy(ABC):
    """Abstract base class for compilation strategies"""
    
    @abstractmethod
    def compile(self, model, workspace: Path, config: Optional[Dict] = None,  **kwargs) -> Any:
        """Compile model to firmware"""
        pass
    
    @abstractmethod
    def load_compiled_model(self, workspace: Path) -> Any:
        """Load a previously compiled model"""
        pass


class ModelPredictor(ABC):
    """Abstract base class for model predictors"""
    
    @abstractmethod
    def predict(self, input_data: np.ndarray) -> np.ndarray:
        """Make predictions using the model"""
        pass


class KerasToQONNXConverter(ModelConverter):
    """Converts Keras models to QONNX format"""
    
    def convert(self, model, workspace: Path, **kwargs) -> Path:
        import tensorflow as tf
        from qonnx.converters import keras as keras_converter
        from qonnx.core.modelwrapper import ModelWrapper
        from qonnx.transformation.channels_last import ConvertToChannelsLastAndClean
        from qonnx.transformation.gemm_to_matmul import GemmToMatMul
        from qonnx.util.cleanup import cleanup_model
        
        qonnx_path = workspace / "model_qonnx.onnx"
        input_signature = [tf.TensorSpec(1, model.inputs[0].dtype, name="input_0")]
        qonnx_model, _ = keras_converter.from_keras(model, input_signature, output_path=qonnx_path)
        qonnx_model = ModelWrapper(qonnx_model)
        qonnx_model = cleanup_model(qonnx_model)
        qonnx_model = qonnx_model.transform(ConvertToChannelsLastAndClean())
        qonnx_model = qonnx_model.transform(GemmToMatMul())
        cleaned_model = cleanup_model(qonnx_model)
        
        return qonnx_path, cleaned_model


class NoOpConverter(ModelConverter):
    """No-operation converter for models that don't need conversion"""
    
    def convert(self, model, workspace: Path, **kwargs) -> Optional[Path]:
        return None


class HLS4MLStrategy(CompilerStrategy):
    def compile(self, model, workspace: Path, config: Optional[Dict] = None) -> Any:
        import hls4ml

        firmware_dir = workspace / "firmware"
        firmware_dir.mkdir(exist_ok=True)

        hls_config = hls4ml.utils.config_from_keras_model(model, granularity="name")
        hls_kwargs = {}

        for key in ["project_name", "namespace", "io_type", "backend", "write_weights_txt"]:
            if key in config:
                hls_kwargs[key] = config[key]

        firmware_model = hls4ml.converters.convert_from_keras_model(
            model,
            hls_config=hls_config,
            output_dir=str(firmware_dir),
            **hls_kwargs
        )

        firmware_model.compile()
        firmware_model.save(workspace / "firmware_model.fml")
        return firmware_model

        
    def load_compiled_model(self, workspace: Path) -> Any:
        from hls4ml.converters import link_existing_project
        
        firmware_model = link_existing_project(workspace / "firmware")
        firmware_model.compile()
        return firmware_model


class ConiferStrategy(CompilerStrategy):
    """Conifer compilation strategy for XGBoost models, unified config/workspace handling."""

    def compile(self, model, workspace: Path, config: Optional[Dict] = None) -> Any:
        import conifer
        import os

        firmware_dir = workspace / "firmware"
        firmware_dir.mkdir(exist_ok=True)

        cfg = conifer.backends.xilinxhls.auto_config()
        cfg['OutputDir'] = str(firmware_dir)
        cfg['ProjectName'] = config['project_name']
        cfg['XilinxPart'] = config['fpga_part']
        cfg['ClockPeriod'] = config['clock_period']

        if config:
            for key, value in config.items():
                cfg[key] = value

        firmware_model = conifer.converters.convert_from_xgboost(model, config=cfg)
        firmware_model.compile()
        firmware_model.save(firmware_dir / "firmware_model.fml")

        return firmware_model

    
    def load_compiled_model(self, workspace: Path) -> Any:
        from conifer import load_model
        
        firmware_model = load_model(workspace / "firmware_model.fml")
        firmware_model.compile()
        return firmware_model


class DA4MLStrategy(CompilerStrategy):
    """DA4ML compilation strategy (placeholder)"""
    
    def compile(self, model, workspace: Path, config: Optional[Dict] = None) -> Any:
        raise NotImplementedError("DA4ML conversion without QONNX not yet implemented")
    
    def load_compiled_model(self, workspace: Path) -> Any:
        raise NotImplementedError("DA4ML loading not yet implemented")


class FINNStrategy(CompilerStrategy):
    """FINN compilation strategy (placeholder)"""
    
    def compile(self, model, workspace: Path, config: Optional[Dict] = None) -> Any:
        raise NotImplementedError("FINN conversion without QONNX not yet implemented")
    
    def load_compiled_model(self, workspace: Path) -> Any:
        raise NotImplementedError("FINN loading not yet implemented")


class SoftwarePredictor(ModelPredictor):
    """Software-based model predictor"""
    
    def __init__(self, model, backend: str):
        self.model = model
        self.backend = backend.lower()
    
    def predict(self, input_data):
        if input_data.ndim == 1:
            input_data = np.expand_dims(input_data, axis=0)
        return self.model.predict(input_data)


class QONNXPredictor(ModelPredictor):
    """QONNX-based model predictor"""
    
    def __init__(self, qonnx_model, input_name: str):
        self.qonnx_model = qonnx_model
        self.input_name = input_name
    
    def predict(self, input_data: np.ndarray) -> np.ndarray:
        from qonnx.core.onnx_exec import execute_onnx
        
        input_data = np.asarray(input_data)
        if input_data.ndim == 1:
            input_data = np.expand_dims(input_data, axis=0)
        
        outputs = []
        for i in range(input_data.shape[0]):
            sample = input_data[i].astype("float32").reshape(1, -1)
            output_dict = execute_onnx(self.qonnx_model, {self.input_name: sample})
            outputs.append(output_dict["global_out"])
        
        return np.vstack(outputs)


class FirmwarePredictor(ModelPredictor):
    """Firmware-based model predictor"""
    
    def __init__(self, firmware_model, compiler):
        if firmware_model is None:
            raise RuntimeError("Firmware model not built.")
        self.firmware_model = firmware_model
        self.compiler = compiler
    
    
    def predict(self, input_data: np.ndarray) -> np.ndarray:
        if self.compiler == "conifer":
            return self.firmware_model.decision_function(input_data)
        else:
            return self.firmware_model.predict(input_data)


class ConverterFactory:
    """Factory for creating model converters"""
    
    @staticmethod
    def create_converter(ml_backend: str, compiler: str) -> ModelConverter:
        if ml_backend.lower() == "keras" and compiler.lower() == "hls4ml":
            return KerasToQONNXConverter()
        else:
            return NoOpConverter()


class CompilerFactory:
    """Factory for creating compilation strategies"""
    
    @staticmethod
    def create_compiler(ml_backend: str, compiler: str) -> CompilerStrategy:
        backend = ml_backend.lower()
        comp = compiler.lower()
        
        if backend == "keras" and comp == "hls4ml":
            return HLS4MLStrategy()
        elif backend == "xgboost" and comp == "conifer":
            return ConiferStrategy()
        elif comp == "da4ml":
            return DA4MLStrategy()
        elif comp == "finn":
            return FINNStrategy()
        else:
            raise RuntimeError(f"Unsupported combination: ml_backend={backend}, compiler={comp}")


class WorkspaceManager:
    """Manages workspace directories and metadata"""
    
    BASE_WORKSPACE = Path.cwd() / "triggermodel"
    
    def __init__(self):
        self.workspace = self.BASE_WORKSPACE
        self.artifacts = {"firmware": None}
        self.metadata = {
            "name": None,
            "ml_backend": None,
            "compiler": None,
            "versions": []
        }
    
    def setup_workspace(self, name: str, ml_backend: str, compiler: str):
        """Initialize workspace and metadata"""
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.metadata.update({
            "name": name,
            "ml_backend": ml_backend,
            "compiler": compiler,
        })
    
    def save_native_model(self, model, ml_backend: str):
        """Save the native model to workspace"""
        if ml_backend.lower() == "keras":
            model.save(self.workspace / "keras_model")
        elif ml_backend.lower() == "xgboost":
            model.save_model(str(self.workspace / "xgb_model.json"))
    
    def add_artifact(self, key: str, value: Any):
        """Add artifact to tracking"""
        self.artifacts[key] = value
    
    def add_version(self, version_info: Dict):
        """Add version information"""
        self.metadata["versions"].append(version_info)
    
    def save_metadata(self):
        """Save metadata to file"""
        with open(self.workspace / "metadata.json", "w") as f:
            json.dump({
                "name": self.metadata["name"],
                "ml_backend": self.metadata["ml_backend"],
                "compiler": self.metadata["compiler"],
            }, f, indent=2)


class ModelSerializer:
    """Handles model serialization and deserialization"""
    
    @staticmethod
    def save(workspace: Path, path: str):
        """Serialize the workspace into a tar.xz archive"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(path, mode="w:xz") as tar:
            tar.add(workspace, arcname=workspace.name)
        print(f"TriggerModel saved to {path}")
    
    @staticmethod
    def load(path: str) -> Dict[str, Any]:
        """Load workspace from tar.xz archive"""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"{path} does not exist")
        
        workspace = Path.cwd() / "triggermodel"
        
        if workspace.exists():
            response = input(f"{workspace} already exists. Overwrite? [y/N]: ").strip().lower()
            if response != "y":
                print("Load cancelled by user.")
                return None
            shutil.rmtree(workspace)
        
        with tarfile.open(path, mode="r:xz") as tar:
            tar.extractall(path=Path.cwd())
        
        # Load metadata
        metadata_path = workspace / "metadata.json"
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        return {
            "workspace": workspace,
            "metadata": metadata
        }
    
    @staticmethod
    def load_native_model(workspace: Path, ml_backend: str):
        """Load native model from workspace"""
        if ml_backend in ("keras", "qkeras"):
            try:
                tf_keras = importlib.import_module("keras.models")
            except ModuleNotFoundError:
                tf_keras = importlib.import_module("tensorflow.keras.models")
            return tf_keras.load_model(workspace / "keras_model")
        elif ml_backend == "xgboost":
            import xgboost as xgb
            model = xgb.Booster()
            model.load_model(str(workspace / "xgb_model.json"))
            return model
        else:
            raise ValueError(f"Unsupported ml_backend: {ml_backend}")
    
    @staticmethod
    def load_qonnx_model(workspace: Path):
        """Load QONNX model if it exists"""
        qonnx_path = workspace / "model_qonnx.onnx"
        if qonnx_path.exists():
            from qonnx.core.modelwrapper import ModelWrapper
            model = ModelWrapper(str(qonnx_path))
            input_name = model.graph.input[0].name
            return model, input_name
        return None, None


class TriggerModel:
    def __init__(self, config: Union[str, Path, Dict], native_model, scales):
        if isinstance(config, (str, Path)):
            with open(config, "r") as f:
                config = yaml.safe_load(f)
        elif not isinstance(config, dict):
            raise TypeError("config must be a dict or path to a YAML file")

        self.native_model = native_model
        self.scales = scales

        self.compiler_cfg  = config.get("compiler", {})
        self.subsystem_cfg = config.get("subsystem", {})

        self.name = self.compiler_cfg.get("name", "model")
        self.ml_backend = self.compiler_cfg.get("ml_backend", "").lower()
        self.compiler = self.compiler_cfg.get("compiler", "").lower()

        self.n_outputs = self.compiler_cfg.get("n_outputs")
        self.unscaled_type = self.subsystem_cfg.get("unscaled_type", "ap_fixed<16,6>")

        if self.ml_backend not in ("keras", "xgboost"):
            raise ValueError("Unsupported backend")

        self.workspace_manager = WorkspaceManager()
        self.converter = ConverterFactory.create_converter(self.ml_backend, self.compiler)
        self.compiler_strategy = CompilerFactory.create_compiler(self.ml_backend, self.compiler)

        self.firmware_model = None
        self.model_qonnx = None
        self.input_name = None
        
        
        self.workspace_manager.setup_workspace(
            self.name, 
            self.ml_backend, 
            self.compiler
        )
    
    @property
    def workspace(self) -> Path:
        """Get workspace path"""
        return self.workspace_manager.workspace
    
    @property
    def artifacts(self) -> Dict[str, Any]:
        """Get artifacts dictionary"""
        return self.workspace_manager.artifacts
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get metadata dictionary"""
        return self.workspace_manager.metadata
    
    def __call__(self):
        """Execute full model conversion and compilation pipeline using YAML config"""
        self.parse_dataset_object()
        
        # Save native model
        self.workspace_manager.save_native_model(self.native_model, self.ml_backend)
        
        # Convert model if needed
        conversion_result = self.converter.convert(
            self.native_model, 
            self.workspace_manager.workspace
        )
        
        if conversion_result is not None:
            qonnx_path, self.model_qonnx = conversion_result
            self.input_name = self.model_qonnx.graph.input[0].name
            self.workspace_manager.add_artifact("qonnx", qonnx_path)
            self.workspace_manager.add_version({"qonnx": str(qonnx_path)})

        
        # Compile model
        self.firmware_model = self.compiler_strategy.compile(
            self.native_model,
            self.workspace_manager.workspace,
            self.compiler_cfg,
            **self.compiler_cfg.get("kwargs", {})
        )
        
        self.workspace_manager.add_artifact("firmware", self.workspace_manager.workspace / "firmware")
        if self.compiler != "conifer" and self.scales is not None:
            self.build_emulator(
                self.scales['shifts'],
                self.scales['offsets'],
                self.n_outputs,
                self.unscaled_type
            )

        
        build_ugt_model(
                templates_dir=self.subsystem_cfg.get("templates_dir", Path("templates")),
                firmware_dir=self.workspace_manager.workspace / "firmware",
                compiler = self.compiler,
                model_name=self.name,
                n_inputs=self.subsystem_cfg["n_inputs"],
                n_outputs=self.subsystem_cfg.get("n_outputs", self.n_outputs),
                nn_offsets=self.scales["offsets"],
                nn_shifts=self.scales["shifts"],
                muon_size=self.subsystem_cfg.get("muon_size", 0),
                jet_size=self.subsystem_cfg.get("jet_size", 0),
                egamma_size=self.subsystem_cfg.get("egamma_size", 0),
                tau_size=self.subsystem_cfg.get("tau_size", 0),
                output_type=self.subsystem_cfg.get("output_type", "result_t"),
                offset_type=self.subsystem_cfg.get("offset_type", "ap_fixed<10,10>"),
                shift_type=self.subsystem_cfg.get("shift_type", "ap_fixed<10,10>"),
                object_features=self.subsystem_cfg.get("object_features"),
                global_features=self.subsystem_cfg.get("global_features")
            )
  


        self.workspace_manager.add_artifact("firmware", self.workspace_manager.workspace / "firmware")
        self.workspace_manager.save_metadata()

    
    @staticmethod
    def parse_dataset_object():
        """Parse dataset object (placeholder)"""
        pass

    @staticmethod
    def _render_template(template_path: Path, out_path: Path, context: dict):
        """Simple template substitution"""
        with open(template_path) as f:
            template = f.read()
        for k, v in context.items():
            template = template.replace("{{" + k + "}}", str(v))
        with open(out_path, "w") as f:
            f.write(template)
    
    def software_predict(self, input_data: np.ndarray) -> np.ndarray:
        """Make predictions using software model"""
        predictor = SoftwarePredictor(self.native_model, self.ml_backend)
        return predictor.predict(input_data)
    
    def qonnx_predict(self, input_data: np.ndarray) -> np.ndarray | None:
        """Make predictions using QONNX model"""
        
        if self.model_qonnx is None:
            warnings.warn(
                "QONNX model is not available. Prediction skipped.",
                UserWarning
            )
            return None 
            
        predictor = QONNXPredictor(self.model_qonnx, self.input_name)
        return predictor.predict(input_data)
    
    def firmware_predict(self, input_data: np.ndarray) -> np.ndarray:
        """Make predictions using firmware model"""
        predictor = FirmwarePredictor(self.firmware_model, self.compiler)
        return predictor.predict(input_data)
    
    def build_emulator(self, ad_shift: list, ad_offsets: list, n_outputs: int, unscaled_type: str = "ap_fixed<16,6>"):
        """Builds CMSSW emulator"""
    
        emulator_dir = self.workspace / "emulator"
        emulator_dir.mkdir(exist_ok=True)

        model_dir = emulator_dir / self.name 
        model_dir.mkdir(exist_ok=True)
        
        firmware_dir = self.workspace / "firmware" / "firmware"
        
        shutil.copytree(firmware_dir, f"{model_dir}/NN", dirs_exist_ok=True)
        
        # Access scales template from installed package
        with pkg_resources.path(triggerflow.templates, "scales.h") as scales_template_path:
            scales_out_path = model_dir / "scales.h"
            context = {
                "MODEL_NAME": self.name,
                "N_INPUTS": len(ad_shift),
                "N_OUTPUTS": n_outputs,
                "AD_SHIFT": ", ".join(map(str, ad_shift)),
                "AD_OFFSETS": ", ".join(map(str, ad_offsets)),
                "UNSCALED_TYPE": unscaled_type,  
            }
            self._render_template(scales_template_path, scales_out_path, context)

        with pkg_resources.path(triggerflow.templates, "model_template.cpp") as emulator_template_path:
            emulator_out_path = model_dir / "emulator.cpp"
            self._render_template(emulator_template_path, emulator_out_path, context) 
        
        with pkg_resources.path(triggerflow.templates, "makefile_version") as makefile_template_path:
            makefile_out_path = model_dir / "Makefile"
            self._render_template(makefile_template_path, makefile_out_path, {"MODEL_NAME": self.name})

        with pkg_resources.path(triggerflow.templates, "makefile") as makefile_template_path:
            makefile_out_path = emulator_dir / "Makefile"
            self._render_template(makefile_template_path, makefile_out_path, {"MODEL_NAME": self.name})
        
    
    def save(self, path: str):
        """Save the complete model to an archive"""
        ModelSerializer.save(self.workspace_manager.workspace, path)
    
    @classmethod
    def load(cls, path: str) -> 'TriggerModel':
        """Load a model from an archive"""
        load_result = ModelSerializer.load(path)
        if load_result is None:
            return None
        
        workspace = load_result["workspace"]
        metadata = load_result["metadata"]
        
        obj = cls.__new__(cls)
        obj.workspace_manager = WorkspaceManager()
        obj.workspace_manager.workspace = workspace
        obj.workspace_manager.metadata = metadata
        obj.workspace_manager.artifacts = {"firmware": workspace / "firmware"}
        
        obj.name = metadata.get("name", "")
        obj.ml_backend = metadata.get("ml_backend")
        obj.compiler = metadata.get("compiler")
        
        obj.native_model = ModelSerializer.load_native_model(workspace, obj.ml_backend)
        
        obj.model_qonnx, obj.input_name = ModelSerializer.load_qonnx_model(workspace)
        
        if obj.compiler.lower() in ("hls4ml", "conifer"):
            obj.compiler_strategy = CompilerFactory.create_compiler(obj.ml_backend, obj.compiler)
            obj.firmware_model = obj.compiler_strategy.load_compiled_model(workspace)
        else:
            obj.firmware_model = None
            obj.compiler_strategy = None
        
        obj.converter = ConverterFactory.create_converter(obj.ml_backend, obj.compiler)
        obj.dataset_object = None 
        
        return obj