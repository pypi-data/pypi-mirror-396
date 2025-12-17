import os
import sys

import awkward as ak

# Add project src to path
sys.path.append('./src')

from trigger_loader.loader import TriggerLoader


def transform(events):

    jets = events.Jet
    pt  = ak.fill_none(ak.pad_none(jets.pt , 2, axis=1, clip=True), -9999.9)
    eta = ak.fill_none(ak.pad_none(jets.eta, 2, axis=1, clip=True), -9999.9)
    phi = ak.fill_none(ak.pad_none(jets.phi, 2, axis=1, clip=True), -9999.9)

    met = events.MET

    result = ak.zip({
        "jet_pt_1":  pt[:, 0],
        "jet_pt_2":  pt[:, 1],
        "jet_eta_1": eta[:, 0],
        "jet_eta_2": eta[:, 1],
        "jet_phi_1": phi[:, 0],
        "jet_phi_2": phi[:, 1],
        "met_pt":    met.pt,
        "met_phi":   met.phi,
    })

    return result

def transform_gpu(events):

    # 1. Force lazy data to be loaded into memory
    events = ak.materialize(events)

    # 2. Move the data to the GPU for processing
    gpu_events = ak.to_backend(events, "cuda")

    # 3. Perform all your calculations on the GPU
    # NOTE: Must fill None values to prevent errors on GPU
    jets = gpu_events.Jet
    pt  = ak.fill_none(ak.pad_none(jets.pt , 2, axis=1, clip=True), -9999.9)
    eta = ak.fill_none(ak.pad_none(jets.eta, 2, axis=1, clip=True), -9999.9)
    phi = ak.fill_none(ak.pad_none(jets.phi, 2, axis=1, clip=True), -9999.9)

    met = gpu_events.MET

    gpu_result = ak.zip({
        "jet_pt_1":  pt[:, 0],
        "jet_pt_2":  pt[:, 1],
        "jet_eta_1": eta[:, 0],
        "jet_eta_2": eta[:, 1],
        "jet_phi_1": phi[:, 0],
        "jet_phi_2": phi[:, 1],
        "met_pt":    met.pt,
        "met_phi":   met.phi,
    })

    # 4. Move the final result back to the CPU before returning
    cpu_result = ak.to_backend(gpu_result, "cpu")

    return cpu_result

def main():
    sample_json = './fileset.json'
    output_dir = './test_output'
    os.makedirs(output_dir, exist_ok=True)

    loader = TriggerLoader(
        sample_json=sample_json,
        transform=transform,
        output_path=output_dir
    )

    condor_config = {
        "log_directory": "./condor_logs",
        "cores": 2,
        "memory": "2GB",
        "disk": "2GB",
        "job_extra_directives": {
            "+JobFlavour": '"longlunch"',
            "getenv": "True",
        },
        "death_timeout": "60",
    }

    cuda_config = {
        "n_workers": 2, # Number of GPUs to use
        "device_memory_limit": "16GB",
    }


    loader.run_local(num_workers=4, chunksize=50000)
    loader.run_distributed(cluster_type="local", cluster_config={}, chunksize=100000)
    loader.run_distributed(cluster_type="condor", cluster_config=condor_config, chunksize=10000, jobs=4)
    loader.run_distributed(cluster_type="cuda", cluster_config=cuda_config, chunksize=400000)
    loader.run_distributed(cluster_type="kubernetes", cluster_config={}, chunksize=10000)

if __name__ == "__main__":
    main()
