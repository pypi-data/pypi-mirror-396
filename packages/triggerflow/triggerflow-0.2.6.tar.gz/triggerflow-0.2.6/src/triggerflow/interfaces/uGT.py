from pathlib import Path
import shutil, warnings
import pkg_resources
from jinja2 import Template
import re


def _render_template(template_name: str, output_file: Path, context: dict):
    template_bytes = pkg_resources.resource_string(
        "triggerflow" , template_name
    )
    template_text = template_bytes.decode('utf-8')

    template = Template(template_text)
    rendered = template.render(**context)

    with open(output_file, "w") as f:
        f.write(rendered)

def build_ugt_model(
    templates_dir: Path,
    firmware_dir: Path,
    compiler: str,
    model_name: str,
    n_inputs: int,
    n_outputs: int,
    nn_offsets: list,
    nn_shifts: list,
    muon_size: int,
    jet_size: int,
    egamma_size: int,
    tau_size: int,
    output_type: str = "result_t",
    offset_type: str = "ap_fixed<10,10>",
    shift_type: str = "ap_fixed<10,10>",
    object_features: dict = None,
    global_features: list = None
):
    """
    Render uGT top func.
    """


    if object_features is None:
        object_features = {
            "muons": ["pt", "eta_extrapolated", "phi_extrapolated"],
            "jets": ["et", "eta", "phi"],
            "egammas": ["et", "eta", "phi"],
            "taus": ["et", "eta", "phi"]
        }

    if global_features is None:
        global_features = [
            "et.et",
            "ht.et",
            "etmiss.et", "etmiss.phi",
            "htmiss.et", "htmiss.phi",
            "ethfmiss.et", "ethfmiss.phi",
            "hthfmiss.et", "hthfmiss.phi"
        ]

    header_path = firmware_dir / "firmware" / f"{model_name}_project.h"
    if compiler.lower() == "conifer":
        output_layer = "score"
        output_type = "score_arr_t"
        header_path = firmware_dir / "firmware" / f"{model_name}_project.h"
        removal_pattern = re.compile(
            r',\s*score_t\s+tree_scores\[BDT::fn_classes\(n_classes\)\s*\*\s*n_trees\]', 
            re.DOTALL
        )
        modified_content = removal_pattern.sub('', header_path.read_text(encoding='utf-8'))
        header_path.write_text(modified_content, encoding='utf-8')
        out = output_layer
    else:
        header_content = header_path.read_text(encoding='utf-8')
        layer_pattern = re.compile(
            r'result_t\s+(\w+)\[\d+\]\s*\)', 
            re.DOTALL
        )
        match = layer_pattern.search(header_content)
        layer_name = match.group(1) 
        output_layer = f"{layer_name}[{n_outputs}]"
        out = layer_name

        
    context = {
    "MODEL_NAME": model_name,
    "N_INPUTS": n_inputs,
    "N_OUTPUTS": n_outputs,
    "NN_OFFSETS": ", ".join(map(str, nn_offsets)),
    "NN_SHIFTS": ", ".join(map(str, nn_shifts)),
    "MUON_SIZE": muon_size,
    "JET_SIZE": jet_size,
    "EGAMMA_SIZE": egamma_size,
    "TAU_SIZE": tau_size,
    "OUTPUT_TYPE": output_type,
    "OUTPUT_LAYER": output_layer,
    "OUT": out,
    "OFFSET_TYPE": offset_type,
    "SHIFT_TYPE": shift_type,
    "MUON_FEATURES": object_features["muons"],
    "JET_FEATURES": object_features["jets"],
    "EGAMMA_FEATURES": object_features["egammas"],
    "TAU_FEATURES": object_features["taus"],
    "GLOBAL_FEATURES": global_features
    }

    context_tcl = {
    "MODEL_NAME": model_name,
    }

    out_path = firmware_dir / "firmware/model-gt.cpp"
    
    _render_template("templates/model-gt.cpp", out_path, context)

    out_path = firmware_dir / "firmware/build_ugt.tcl"
    _render_template("templates/build_ugt.tcl", out_path, context_tcl)

    shutil.copy(
        pkg_resources.resource_filename("triggerflow", "templates/data_types.h"), 
        firmware_dir / "firmware"
    )

    if shutil.which("vivado") is not None:
        subprocess.run(
            ["vitis_hls", "-f", "build_ugt.tcl"],
            cwd=firmware_dir/"firmware",
            check=True
        )
    else:
            warnings.warn(
                "Vivado executable not found on the system PATH. "
                "Skipping FW build. ",
                UserWarning
            )




