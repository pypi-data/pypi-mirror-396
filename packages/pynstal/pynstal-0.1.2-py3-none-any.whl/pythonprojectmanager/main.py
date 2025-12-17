import argparse
import sys
import os
import json
import importlib.resources as pkg_resources
import subprocess
from pathlib import Path
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

def cprint(msg: str, color: str = Fore.WHITE) -> None:
    print(f"{color}{msg}{Style.RESET_ALL}")

from .create_venv import create_venv, install_packages_in_venv, install_packages
from .handle_data import interpreters_data


def cmd_add_interpreter(args):
    path = args.path
    if interpreters_data.interpreters is None:
        interpreters_data.interpreters = []
    if path in interpreters_data.interpreters:
        print("Interpreter already exists in .pynstal.")
        return
    interpreters_data.interpreters.append(path)
    interpreters_data.save()
    cprint(f"Added interpreter: {path}", Fore.GREEN)


def cmd_set_default_interpreter(args):
    path = args.path
    if not os.path.isfile(path):
        print(f"Interpreter not found: {path}")
        return 2
    interpreters_data.default_interpreter = path
    # ensure it's in the interpreters list as well
    if interpreters_data.interpreters is None:
        interpreters_data.interpreters = [path]
    elif path not in interpreters_data.interpreters:
        interpreters_data.interpreters.insert(0, path)
    interpreters_data.save()
    print(f"Set default interpreter: {path}")
    return 0


def cmd_list(args):
    cprint("Interpreters:", Fore.CYAN)
    if interpreters_data.interpreters:
        for p in interpreters_data.interpreters:
            print(f" - {p}")
    else:
        cprint(" - (none)", Fore.YELLOW)
    cprint("Default interpreter:", Fore.CYAN)
    print(f" - {interpreters_data.default_interpreter}")


def load_templates():
    # prefer project .pynstal/templates.json if present, fall back to bundled resource
    tpl_path = os.path.join(".pynstal", "templates.json")
    if os.path.exists(tpl_path):
        with open(tpl_path, "r", encoding="utf-8") as f:
            return json.load(f)

    try:
        text = pkg_resources.files(__package__).joinpath("templates.json").read_text(encoding="utf-8")
        return json.loads(text)
    except Exception:
        return {"templates": {}}


def save_templates(data):
    """Persist templates to .pynstal/templates.json."""
    tpl_path = os.path.join(".pynstal", "templates.json")
    os.makedirs(".pynstal", exist_ok=True)
    with open(tpl_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def detect_interpreters(verbose: bool = False) -> list[dict]:
    """
    Scan system for Python installations.
    Returns list of dicts with {'path': str, 'version': str}.
    """
    candidates = set()
    
    if sys.platform == "win32":
        # Windows: Registry, common paths, pyenv-win
        candidates.update(_scan_windows_python())
    else:
        # Unix/Linux/Mac
        candidates.update(_scan_unix_python())
    
    # Add current interpreter
    candidates.add(sys.executable)
    
    # Scan conda environments
    candidates.update(_scan_conda_envs())
    
    # Scan pyenv
    candidates.update(_scan_pyenv())
    
    # Verify each candidate and extract version
    found = []
    for candidate in sorted(candidates):
        if candidate and os.path.isfile(candidate):
            try:
                version = _get_python_version(candidate)
                if version:
                    found.append({
                        'path': str(candidate),
                        'version': version
                    })
                    if verbose:
                        print(f"  Found: {candidate} (Python {version})")
            except Exception as e:
                if verbose:
                    print(f"  Skipped: {candidate} ({e})")
    
    # Remove duplicates based on path
    seen = set()
    unique = []
    for item in found:
        if item['path'] not in seen:
            seen.add(item['path'])
            unique.append(item)
    
    return unique


def _scan_windows_python() -> set:
    """Scan Windows common paths for Python."""
    paths = set()
    
    # Check common installation directories
    common_paths = [
        r"C:\Python310",
        r"C:\Python311",
        r"C:\Python312",
        r"C:\Python313",
    ]
    for base in common_paths:
        exe = os.path.join(base, "python.exe")
        if os.path.isfile(exe):
            paths.add(exe)
    
    # Check AppData\Local\Programs\Python
    appdata = os.getenv("APPDATA")
    if appdata:
        base = os.path.join(appdata, "..", "Local", "Programs", "Python")
        if os.path.isdir(base):
            for d in os.listdir(base):
                exe = os.path.join(base, d, "python.exe")
                if os.path.isfile(exe):
                    paths.add(exe)
    
    # Check pyenv-win
    pyenv_root = os.getenv("PYENV_ROOT", os.path.expanduser("~\\.pyenv"))
    versions_dir = os.path.join(pyenv_root, "versions")
    if os.path.isdir(versions_dir):
        for ver in os.listdir(versions_dir):
            exe = os.path.join(versions_dir, ver, "python.exe")
            if os.path.isfile(exe):
                paths.add(exe)
    
    return paths


def _scan_unix_python() -> set:
    """Scan Unix/Linux/Mac common paths for Python."""
    paths = set()
    
    common_dirs = [
        "/usr/bin",
        "/usr/local/bin",
        "/opt/python",
        os.path.expanduser("~/.local/bin"),
    ]
    
    for d in common_dirs:
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.startswith("python"):
                    full_path = os.path.join(d, f)
                    if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                        paths.add(full_path)
    
    return paths


def _scan_conda_envs() -> set:
    """Scan conda environments for Python."""
    paths = set()
    
    conda_roots = [
        os.path.expanduser("~/anaconda3"),
        os.path.expanduser("~/miniconda3"),
        os.path.expanduser("~/mambaforge"),
        os.getenv("CONDA_PREFIX"),
    ]
    
    for conda_root in conda_roots:
        if conda_root and os.path.isdir(conda_root):
            envs_dir = os.path.join(conda_root, "envs")
            if os.path.isdir(envs_dir):
                for env in os.listdir(envs_dir):
                    if sys.platform == "win32":
                        exe = os.path.join(envs_dir, env, "python.exe")
                    else:
                        exe = os.path.join(envs_dir, env, "bin", "python")
                    if os.path.isfile(exe):
                        paths.add(exe)
            
            # Also check root python
            if sys.platform == "win32":
                exe = os.path.join(conda_root, "python.exe")
            else:
                exe = os.path.join(conda_root, "bin", "python")
            if os.path.isfile(exe):
                paths.add(exe)
    
    return paths


def _scan_pyenv() -> set:
    """Scan pyenv for Python versions."""
    paths = set()
    
    pyenv_root = os.getenv("PYENV_ROOT", os.path.expanduser("~/.pyenv"))
    versions_dir = os.path.join(pyenv_root, "versions")
    
    if os.path.isdir(versions_dir):
        for ver in os.listdir(versions_dir):
            if sys.platform == "win32":
                exe = os.path.join(versions_dir, ver, "python.exe")
            else:
                exe = os.path.join(versions_dir, ver, "bin", "python")
            if os.path.isfile(exe):
                paths.add(exe)
    
    return paths


def _get_python_version(python_exe: str) -> str | None:
    """Get Python version from executable."""
    try:
        result = subprocess.run(
            [python_exe, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Output is "Python 3.12.4"
            return result.stdout.strip().replace("Python ", "")
    except Exception:
        pass
    return None


def cmd_create(args):
    interpreter = args.interpreter
    if not interpreter:
        interpreter = interpreters_data.default_interpreter
        if not interpreter and interpreters_data.interpreters:
            interpreter = interpreters_data.interpreters[0]
    venv_dir = args.venv_dir
    dry_run = args.dry_run
    success = create_venv(interpreter, venv_dir, dry_run=dry_run)
    sys.exit(0 if success else 1)


def cmd_create_from_template(args):
    template = args.template
    venv_dir = args.venv_dir
    dry_run = args.dry_run
    interpreter = args.interpreter

    data = load_templates()
    templates = data.get("templates", {})
    if template not in templates:
        cprint(f"Template '{template}' not defined. Available: {', '.join(templates.keys())}", Fore.RED)
        return 2

    packages = templates[template]

    # determine interpreter to use
    if not interpreter:
        interpreter = interpreters_data.default_interpreter
        if not interpreter and interpreters_data.interpreters:
            interpreter = interpreters_data.interpreters[0]

    if not interpreter:
        cprint("No interpreter specified and no interpreter configured in .pynstal.", Fore.RED)
        return 2

    # create venv
    created = create_venv(interpreter, venv_dir, dry_run=dry_run)
    if not created:
        cprint("Failed to create venv; aborting package installation.", Fore.RED)
        return 1

    ok, out, err = install_packages_in_venv(venv_dir, packages, dry_run=dry_run)
    if ok:
        cprint("Packages installed successfully." if not dry_run else out, Fore.GREEN)
        return 0
    else:
        cprint(f"Failed installing packages. Error:\n{err}", Fore.RED)
        return 1


def cmd_template_list(args):
    data = load_templates()
    templates = data.get("templates", {})
    if not templates:
        print("No templates defined.")
        return 0
    print("Available templates:")
    for name, packages in templates.items():
        print(f"  {name}:")
        if isinstance(packages, list):
            for pkg in packages:
                if isinstance(pkg, str):
                    print(f"    - {pkg}")
                elif isinstance(pkg, dict):
                    pkgs = pkg.get("packages", [])
                    args_list = pkg.get("args", [])
                    print(f"    - {', '.join(pkgs)} (args: {' '.join(args_list)})")


def cmd_template_add(args):
    name = args.name
    packages_str = args.packages

    data = load_templates()
    templates = data.get("templates", {})

    if name in templates:
        cprint(f"Template '{name}' already exists.", Fore.YELLOW)
        return 2

    # Simple packages as a list
    templates[name] = packages_str.split()
    data["templates"] = templates
    save_templates(data)
    cprint(f"Template '{name}' added with packages: {', '.join(packages_str.split())}", Fore.GREEN)
    return 0


def cmd_template_add_complex(args):
    name = args.name
    packages = args.packages if isinstance(args.packages, list) else [args.packages]
    # args_str could be a list or a string; handle both
    if hasattr(args, 'args_str') and args.args_str:
        pip_args = args.args_str.split() if isinstance(args.args_str, str) else args.args_str
    else:
        pip_args = []

    data = load_templates()
    templates = data.get("templates", {})

    if name in templates:
        cprint(f"Template '{name}' already exists.", Fore.YELLOW)
        return 2

    # Create dict entry with packages and args
    templates[name] = {
        "packages": packages,
        "args": pip_args
    }
    data["templates"] = templates
    save_templates(data)
    cprint(f"Template '{name}' added with packages: {', '.join(packages)}", Fore.GREEN)
    if pip_args:
        cprint(f"  Install args: {' '.join(pip_args)}", Fore.CYAN)
    return 0


def cmd_template_add_complex_wrapper(args):
    """Wrapper that converts packages_str to packages list."""
    args.packages = args.packages_str.split()
    return cmd_template_add_complex(args)


def cmd_template_remove(args):
    name = args.name
    data = load_templates()
    templates = data.get("templates", {})

    if name not in templates:
        cprint(f"Template '{name}' not found.", Fore.YELLOW)
        return 2

    del templates[name]
    data["templates"] = templates
    save_templates(data)
    cprint(f"Template '{name}' removed.", Fore.GREEN)
    return 0


def cmd_template_show(args):
    name = args.name
    data = load_templates()
    templates = data.get("templates", {})

    if name not in templates:
        cprint(f"Template '{name}' not found.", Fore.YELLOW)
        return 2

    packages = templates[name]
    cprint(f"Template '{name}':", Fore.CYAN)
    if isinstance(packages, list):
        for pkg in packages:
            if isinstance(pkg, str):
                print(f"  {pkg}")
            elif isinstance(pkg, dict):
                print(f"  {json.dumps(pkg, indent=4)}")
    return 0


def cmd_interpreter_detect(args):
    """Detect Python installations on the system."""
    cprint("Scanning for Python installations...", Fore.CYAN)
    found = detect_interpreters(verbose=False)
    
    if not found:
        cprint("No Python installations found.", Fore.YELLOW)
        return 1
    
    cprint(f"\nFound {len(found)} Python installation(s):\n", Fore.CYAN)
    for idx, item in enumerate(found, 1):
        print(f"  [{idx}] {item['path']}")
        print(f"      Version: {item['version']}")
    
    if args.add_all:
        # Add all without confirmation
        added_count = 0
        for item in found:
            if interpreters_data.interpreters is None:
                interpreters_data.interpreters = []
            if item['path'] not in interpreters_data.interpreters:
                interpreters_data.interpreters.append(item['path'])
                added_count += 1
        interpreters_data.save()
        print(f"\nAdded {added_count} interpreter(s) to .pynstal/interpreters.json")
        return 0
    
    elif args.add:
        # Interactive selection
        print("\nEnter the numbers of interpreters to add (comma-separated, e.g., 1,2,3):")
        print("Or press Enter to skip.")
        choice = input("> ").strip()
        
        if not choice:
            print("Skipped.")
            return 0
        
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(",")]
            if interpreters_data.interpreters is None:
                interpreters_data.interpreters = []
            
            added_count = 0
            for idx in indices:
                if 0 <= idx < len(found):
                    path = found[idx]['path']
                    if path not in interpreters_data.interpreters:
                        interpreters_data.interpreters.append(path)
                        added_count += 1
                        print(f"  Added: {path}")
            
            interpreters_data.save()
            print(f"\nAdded {added_count} interpreter(s) to .pynstal/interpreters.json")
            return 0
        except (ValueError, IndexError) as e:
            print(f"Invalid input: {e}")
            return 1
    
    else:
        # Just list, don't add
        return 0


def cmd_install(args):
    """Install packages from a template into the current or specified interpreter."""
    template = args.template
    dry_run = args.dry_run
    interpreter = args.interpreter

    data = load_templates()
    templates = data.get("templates", {})
    if template not in templates:
        print(f"Template '{template}' not defined. Available: {', '.join(templates.keys())}")
        return 2

    packages = templates[template]

    # Determine interpreter to use
    if not interpreter:
        interpreter = interpreters_data.default_interpreter
        if not interpreter:
            interpreter = sys.executable

    if not interpreter:
        print("No interpreter specified and no default interpreter configured in .pynstal.")
        return 2

    # Install packages into the specified interpreter
    ok, out, err = install_packages(interpreter, packages, dry_run=dry_run)
    if ok:
        print("Packages installed successfully." if not dry_run else out)
        return 0
    else:
        print(f"Failed installing packages. Error:\n{err}")
        return 1


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pynstal")
    sub = parser.add_subparsers(dest="cmd")

    a_add = sub.add_parser("add-interpreter", help="Add interpreter path to data/interpreters.json")
    a_add.add_argument("path", help="Path to python interpreter executable")
    a_add.set_defaults(func=cmd_add_interpreter)

    a_set_default = sub.add_parser("set-default-interpreter", help="Set the default interpreter for the project")
    a_set_default.add_argument("path", help="Path to python interpreter executable")
    a_set_default.set_defaults(func=cmd_set_default_interpreter)

    a_list = sub.add_parser("list", help="List configured interpreters")
    a_list.set_defaults(func=cmd_list)

    a_detect = sub.add_parser("interpreter", help="Manage interpreters")
    a_detect_sub = a_detect.add_subparsers(dest="interpreter_cmd")
    
    a_detect_detect = a_detect_sub.add_parser("detect", help="Auto-detect Python installations on system")
    a_detect_detect.add_argument("--add", action="store_true", help="Interactively select interpreters to add")
    a_detect_detect.add_argument("--add-all", action="store_true", help="Add all detected interpreters without confirmation")
    a_detect_detect.set_defaults(func=cmd_interpreter_detect)

    a_create = sub.add_parser("create-venv", help="Create virtualenv using specified interpreter")
    a_create.add_argument("venv_dir", help="Directory to create venv in")
    a_create.add_argument("--interpreter", help="Interpreter path to use")
    a_create.add_argument("--dry-run", action="store_true", help="Do not actually run venv creation; show command")
    a_create.set_defaults(func=cmd_create)

    a_tpl = sub.add_parser("create-from-template", help="Create venv and install packages from a named template")
    a_tpl.add_argument("template", help="Template name (see bundled templates.json)")
    a_tpl.add_argument("venv_dir", help="Directory to create venv in")
    a_tpl.add_argument("--interpreter", help="Interpreter path to use (overrides data)")
    a_tpl.add_argument("--dry-run", action="store_true", help="Do not actually run commands; show what would run")
    a_tpl.set_defaults(func=cmd_create_from_template)

    a_install = sub.add_parser("install", help="Install packages from a template (without creating venv)")
    a_install.add_argument("template", help="Template name")
    a_install.add_argument("--interpreter", help="Interpreter path to use (defaults to default_interpreter or current Python)")
    a_install.add_argument("--dry-run", action="store_true", help="Do not actually run commands; show what would run")
    a_install.set_defaults(func=cmd_install)

    # Template management subcommands
    a_tm = sub.add_parser("template", help="Manage templates")
    tm_sub = a_tm.add_subparsers(dest="template_cmd")

    tm_list = tm_sub.add_parser("list", help="List all templates")
    tm_list.set_defaults(func=cmd_template_list)

    tm_add = tm_sub.add_parser("add", help="Add a new template")
    tm_add.add_argument("name", help="Template name")
    tm_add.add_argument("packages", help="Space-separated package names")
    tm_add.set_defaults(func=cmd_template_add)

    tm_add_complex = tm_sub.add_parser("add-complex", help="Add a template with special pip args")
    tm_add_complex.add_argument("name", help="Template name")
    tm_add_complex.add_argument("packages_str", help="Space-separated package names")
    tm_add_complex.add_argument("--args-str", dest="args_str", help="Pip install args as a string (e.g., '--index-url https://...')")
    tm_add_complex.set_defaults(func=cmd_template_add_complex_wrapper)

    tm_remove = tm_sub.add_parser("remove", help="Remove a template")
    tm_remove.add_argument("name", help="Template name")
    tm_remove.set_defaults(func=cmd_template_remove)

    tm_show = tm_sub.add_parser("show", help="Show template details")
    tm_show.add_argument("name", help="Template name")
    tm_show.set_defaults(func=cmd_template_show)

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 2
    return args.func(args)


def cli():
    raise SystemExit(main())
