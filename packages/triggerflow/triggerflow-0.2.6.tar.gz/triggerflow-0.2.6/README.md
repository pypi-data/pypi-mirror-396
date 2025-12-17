# Machine Learning for Hardware Triggers

`triggerflow` provides a set of utilities for Machine Learning models targeting FPGA deployment. 
The `TriggerModel` class consolidates several Machine Learning frontends and compiler backends to construct a "trigger model". MLflow utilities are for logging, versioning, and loading of trigger models.

## Installation

```bash
pip install triggerflow
```

## Usage

```python

from triggerflow.core import TriggerModel


scales = {'offsets': np.array([18, 0, 72, 7, 0, 73, 4, 0, 73, 4, 0, 72, 3, 0, 72, 6, -0, 286, 3, -2, 285, 3, -2, 282, 3, -2, 286, 29, 0, 72, 22, 0, 72, 18, 0, 72, 14, 0, 72, 11, 0, 72, 10, 0, 72, 10, 0, 73, 9, 0], dtype='int'),
'shifts': np.array([3, 0, 6, 2, 5, 6, 0, 5, 6, 0, 5, 6, -1, 5, 6, 2, 7, 8, 0, 7, 8, 0, 7, 8, 0, 7, 8, 4, 6, 6, 3, 6, 6, 3, 6, 6, 3, 6, 6, 3, 6, 6, 3, 6, 6, 3, 6, 6, 3, 6], dtype='int')}


trigger_model = TriggerModel(
    config="triggermodel_config.yaml",
    native_model=model, #Native XGboost/Keras model
    scales=scales
)

trigger_model() #Vivado requird on $PATH for Firmware build.

# then:
output_software = trigger_model.software_predict(input_data)
output_firmware = trigger_model.firmware_predict(input_data)
output_qonnx = trigger_model.qonnx_predict(input_data)

# save and load trigger models:
trigger_model.save("triggerflow.tar.xz")

# in a separate session:
from triggerflow.core import TriggerModel
triggerflow = TriggerModel.load("triggerflow.tar.xz")
```

## The Config file:

Use this `.yaml` template and change as needed. 

```yaml
compiler:
  name: "AXO"
  ml_backend: "keras"
  compiler: "hls4ml"
  fpga_part: "xc7vx690t-ffg1927-2"
  clock_period: 25
  n_outputs: 1
  project_name: "AXO_project"
  namespace: "AXO"
  io_type: "io_parallel"
  backend: "Vitis"
  write_weights_txt: false

subsystem:
  name: "uGT"
  n_inputs: 50
  offset_type: "ap_fixed<10,10>"
  shift_type: "ap_fixed<10,10>"

  objects:
    muons:
      size: 4
      features: [pt, eta_extrapolated, phi_extrapolated]

    jets:
      size: 4
      features: [et, eta, phi]

    egammas:
      size: 4
      features: [et, eta, phi]

    taus:
      size: 4
      features: [et, eta, phi]

  global_features:
    #- et.et
    #- ht.et
    - etmiss.et
    - etmiss.phi
    #- htmiss.et
    #- htmiss.phi
    #- ethfmiss.et
    #- ethfmiss.phi
    #- hthfmiss.et
    #- hthfmiss.phi

  muon_size: 4
  jet_size: 4
  egamma_size: 4
  tau_size: 4
```

## Logging with MLflow

```python
# logging with MLFlow:
import mlflow
from triggerflow.mlflow_wrapper import log_model

mlflow.set_tracking_uri("https://ngt.cern.ch/models")
experiment_id = mlflow.create_experiment("example-experiment")

with mlflow.start_run(run_name="trial-v1", experiment_id=experiment_id):
    log_model(triggerflow, registered_model_name="TriggerModel")
```

### Note: This package doesn't install dependencies so it won't disrupt specific training environments or custom compilers. For a reference environment, see `environment.yml`.


# Creating a kedro pipeline

This repository also comes with a default pipeline for trigger models based on kedro.
One can create a new pipeline via:

NOTE: no "-" and upper cases!

```bash
# Create a conda environment & activate it
conda create -n triggerflow python=3.11
conda activate triggerflow

# install triggerflow
pip install triggerflow

# Create a pipeline
triggerflow new demo_pipeline

# NOTE: since we dont install dependency one has to create a
# conda env based on the environment.yml file of the pipeline
# this file can be changed to the needs of the indiviual project
cd demo_pipeline
conda env update -n triggerflow --file environment.yml

# Run Kedro
kedro run
```