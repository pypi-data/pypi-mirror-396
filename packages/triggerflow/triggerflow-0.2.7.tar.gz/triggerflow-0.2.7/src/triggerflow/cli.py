import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from cookiecutter.main import cookiecutter

try:
    from importlib.resources import as_file
    from importlib.resources import files as ir_files
except ImportError:
    import importlib_resources
    ir_files = importlib_resources.files  # type: ignore
    as_file = importlib_resources.as_file  # type: ignore

logger = logging.getLogger(__name__)


def echo(cmd): logger.info(f"$ {' '.join(str(c) for c in cmd)}", flush=True)
def which_or_die(cmd):
    if shutil.which(cmd) is None:
        logger.info(f"Error: '{cmd}' not found on PATH.", file=sys.stderr); sys.exit(127)

def packaged_starter_root() -> Path:
    """Real FS path to packaged starter folder."""
    base = ir_files("triggerflow")
    with as_file(base / "starter") as p:
        p = Path(p)
        if p.exists():
            return p
    with as_file(base) as p:
        logger.info("Error: starter not found. Contents of package:", file=sys.stderr)
        for child in Path(p).iterdir(): logger.info(" -", child.name, file=sys.stderr)
    sys.exit(2)

def render_starter(project: str, out_dir: Path) -> Path:
    """Render cookiecutter starter into out_dir; returns project path."""
    starter = packaged_starter_root()
    extra = {
        "project_name": project,
        "repo_name": project.replace("-", "_").lower(),
        "python_package": project.replace("-", "_").lower(),
    }

    # cookiecutter.json expects bare keys, not cookiecutter.* here
    out_dir.mkdir(parents=True, exist_ok=True)
    proj_path = Path(cookiecutter(
        template=str(starter),
        no_input=True,
        output_dir=str(out_dir),
        extra_context=extra,
    ))
    return proj_path

def find_env_yml(project_dir: Path) -> Path:
    # Prefer root environment.yml; else find under src/**/
    candidates = []
    root = project_dir / "environment.yml"
    if root.exists(): candidates.append(root)
    candidates += list((project_dir / "src").rglob("environment.yml"))
    if not candidates:
        logger.info(f"Error: environment.yml not found under {project_dir}", file=sys.stderr); sys.exit(3)
    # stable preference
    candidates.sort(key=lambda p: (0 if p.parent.name != "src" else 1, len(str(p))))
    return candidates[0]

def conda_env_create_or_update(env_yml: Path) -> int:
    which_or_die("conda")
    # If YAML has 'name', override it to 'env_name' so updates are consistent
    data = yaml.safe_load(env_yml.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        tmp = env_yml.with_suffix(".rendered.yml")
        tmp.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        env_yml = tmp

    update = ["conda", "env", "update", "-f", str(env_yml), "--prune"]

    echo(update); rc = subprocess.call(update)
    if rc != 0: return rc

    verify = ["conda", "run", "python", "-c", "import sys; logger.info(sys.executable)"]
    echo(verify); subprocess.call(verify)
    return 0

def cmd_new(project: str, output: Path) -> int:
    proj_dir = render_starter(project, output)
    return 0

def cmd_setup(project: str, output: Path) -> int:
    # If project dir doesn’t exist yet, render it first
    target = output / project
    if not target.exists():
        logger.info(f"Project '{project}' not found under {output}. Rendering starter first...")
        render_starter(project, output)
    env_yml = find_env_yml(target)
    logger.info(f"Using environment file: {env_yml}")
    return conda_env_create_or_update(env_yml)

def main():
    parser = argparse.ArgumentParser(prog="triggerflow", description="Triggerflow CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_new = sub.add_parser("new", help="Render a new project from the packaged starter (Cookiecutter)")
    p_new.add_argument("project", help="Project name")
    p_new.add_argument("--out", default=".", help="Output directory (default: .)")

    p_setup = sub.add_parser("setup", help="Create/update conda env from the rendered project's environment.yml")
    p_setup.add_argument("project", help="Project/env name")
    p_setup.add_argument("--out", default=".", help="Project parent directory (default: .)")

    args = parser.parse_args()
    out = Path(getattr(args, "out", ".")).resolve()
    if args.cmd == "new":
        sys.exit(cmd_new(args.project, out))
    else:  # setup
        sys.exit(cmd_setup(args.project, out))

if __name__ == "__main__":
    main()
