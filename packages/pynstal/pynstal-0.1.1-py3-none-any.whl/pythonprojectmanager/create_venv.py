from .handle_data import interpreters_data
import os
import subprocess
import sys

def _create_venv(interpreter_path, venv_dir, dry_run: bool = False):
    abs_interpreter = os.path.abspath(interpreter_path)
    abs_venv = os.path.abspath(venv_dir)
    cmd = [abs_interpreter, "-m", "venv", abs_venv]

    if dry_run:
        stdout = f"DRY RUN: would run: {cmd}"
        return True, stdout, ""

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        universal_newlines=True,
    )

    stdout, stderr = process.communicate()
    return process.returncode == 0, stdout, stderr


def create_venv(interpreter_path, venv_dir, dry_run: bool = False):
    if interpreters_data.interpreters is None:
        print("Warning: no interpreters configured in .pynstal; proceeding with provided interpreter.")

    success, stdout, stderr = _create_venv(interpreter_path, venv_dir, dry_run=dry_run)
    if success:
        if dry_run:
            print(stdout)
            return True
        print(f"Virtual environment created successfully at {venv_dir}.")

        # Configure the newly-created venv as the project's global interpreter
        try:
            if sys.platform.startswith("win"):
                venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
            else:
                venv_python = os.path.join(venv_dir, "bin", "python")

            venv_python = os.path.abspath(venv_python)
            if os.path.exists(venv_python):
                # ensure interpreters list exists and contains venv python
                if interpreters_data.interpreters is None:
                    interpreters_data.interpreters = [venv_python]
                else:
                    if venv_python not in interpreters_data.interpreters:
                        interpreters_data.interpreters.insert(0, venv_python)

                interpreters_data.global_interpreter = venv_python
                interpreters_data.save()
                print(f"Configured project global interpreter: {venv_python}")
        except Exception:
            pass

        return True
    else:
        print(f"Failed to create virtual environment. Error:\n{stderr}")
        return False


def install_packages_in_venv(venv_dir: str, packages: list, dry_run: bool = False):
    """Install packages into the venv's Python using pip.

    Each entry in `packages` may be either:
      - a simple string: "numpy"
      - a dict: {"packages": ["torch","torchvision"], "args": ["--index-url", "https://download.pytorch.org/whl/cu130"]}

    Returns (success: bool, stdout: str, stderr: str).
    """
    if sys.platform.startswith("win"):
        py_exe = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        py_exe = os.path.join(venv_dir, "bin", "python")

    all_stdout = []
    all_stderr = []

    for entry in packages:
        if isinstance(entry, str):
            pkg_list = [entry]
            extra_args = []
        elif isinstance(entry, dict):
            pkg_list = entry.get("packages") or entry.get("package") or []
            if isinstance(pkg_list, str):
                pkg_list = [pkg_list]
            extra_args = entry.get("args", []) or []
        else:
            # unsupported type; skip
            continue

        cmd = [os.path.abspath(py_exe), "-m", "pip", "install"] + pkg_list + extra_args
        if dry_run:
            all_stdout.append(f"DRY RUN: would run: {cmd}")
            continue

        if not os.path.exists(py_exe):
            return False, "", f"Python executable not found in venv: {py_exe}"

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            universal_newlines=True,
        )
        stdout, stderr = process.communicate()
        all_stdout.append(stdout)
        all_stderr.append(stderr)
        if process.returncode != 0:
            return False, "\n".join(all_stdout), "\n".join(all_stderr)

    return True, "\n".join(all_stdout), "\n".join(all_stderr)
