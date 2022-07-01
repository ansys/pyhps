import argparse
import logging
import os
import subprocess
import sys

log = logging.getLogger(__name__)

file_formatter = logging.Formatter("[%(asctime)s/%(levelname)5.5s]  %(message)s")
stream_formatter = logging.Formatter(
    "[%(asctime)s/%(levelname)5.5s]  %(message)s", datefmt="%H:%M:%S"
)
file_handler = logging.FileHandler("bootstrap.log")
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_formatter)
stream_handler.setLevel(logging.DEBUG)

log.addHandler(file_handler)
log.addHandler(stream_handler)
log.setLevel(logging.DEBUG)


class Context(object):
    pip_index_url = "https://pypi.python.org/simple"
    pip_trusted_host = "pypi.python.org"

    def __init__(self, args):
        self.args = args
        self.venv_name = args.venv_name
        self.using_docker = os.environ.get("DEFAULT_DOCKCROSS_IMAGE", None) is not None

        if sys.platform == "win32":
            system_python_binary = f'"{sys.executable}"'
            python_binary = os.path.join(self.args.venv_name, "Scripts", "python.exe")
        else:
            if self.using_docker:
                # When running inside of our dockcross container python3 is actually Ansys python
                log.info("Running inside dockcross container")
                system_python_binary = "python3"
            else:
                system_python_binary = sys.executable
            python_binary = os.path.join(self.args.venv_name, "bin", "python")

        self.system_python_binary = system_python_binary
        self.python_binary = os.path.abspath(python_binary)
        log.debug(f"Python at: {self.system_python_binary}")
        log.debug(f"Virtual Env Python at: {self.python_binary}")


def _do_venv(context):
    log.info("### Preparing venv %s" % context.venv_name)

    subprocess.run(
        f"{context.system_python_binary} -m venv {context.venv_name}", shell=True, check=True
    )

    pip_conf_path = (
        os.path.join(context.venv_name, "pip.ini")
        if sys.platform == "win32"
        else os.path.join(context.venv_name, "pip.conf")
    )

    pip_conf = "[global]"
    pip_conf += "\ntimeout = 60"
    pip_conf += "\nindex-url = " + context.pip_index_url
    pip_conf += "\ntrusted-host = " + context.pip_trusted_host

    log.debug("Writing %s" % pip_conf_path)
    with open(pip_conf_path, "w") as f:
        f.write(pip_conf)

    log.info("### Installing base modules")

    pip_options = []
    if context.args.verbose:
        pip_options.append(" -v")

    log.info("### Updating pip")
    subprocess.run(f"{context.python_binary} -m pip install --upgrade pip", shell=True, check=True)

    # Install requirements
    build_reqs = os.path.join(os.path.dirname(__file__), "requirements", "requirements_build.txt")
    subprocess.run(
        f"{context.python_binary} -m pip install -r {build_reqs}", shell=True, check=True
    )
    test_reqs = os.path.join(os.path.dirname(__file__), "requirements", "requirements_tests.txt")
    subprocess.run(f"{context.python_binary} -m pip install -r {test_reqs}", shell=True, check=True)

    # Install client
    subprocess.run(f"{context.python_binary} -m pip install -e .", shell=True, check=True)


def _do_wheel(context):
    log.info("### Build python client wheel")
    subprocess.run(f"{context.python_binary} setup.py sdist bdist_wheel", shell=True, check=True)


def _do_documentation(context):
    log.info("### Preparing python client documentation")

    docs_directory = os.path.join(os.path.dirname(__file__), "doc", "source")
    target_directory = os.path.join(os.path.dirname(__file__), "build", "sphinx", "html")
    doc_requirements = os.path.join(
        os.path.dirname(__file__), "requirements", "requirements_doc.txt"
    )
    subprocess.run(f"{context.python_binary} -m pip install -r {doc_requirements}")
    subprocess.run(f"{context.python_binary} prepare_documentation.py", shell=True, check=True)
    subprocess.run(
        f"{context.python_binary} -m sphinx -b html {docs_directory} {target_directory}",
        shell=True,
        check=True,
    )


def _run_tests(context):
    cmd = (
        f"{context.python_binary} -m pytest -v --junitxml test_results.xml "
        + "--cov=ansys --cov-report=xml --cov-report=html"
    )
    subprocess.run(f"{cmd}", shell=True, check=True)


steps = [
    ("venv", _do_venv),
    ("wheel", _do_wheel),
    ("documentation", _do_documentation),
    ("tests", _run_tests),
]


def main(context):
    steps_to_run = set(context.args.selected_steps)
    steps_to_run.difference_update(context.args.disabled_steps)

    ordered_steps_to_run = [v[0] for v in steps if v[0] in steps_to_run]
    log.debug("Running steps: %s" % ", ".join(ordered_steps_to_run))
    for step_name, step_impl in steps:
        if step_name not in steps_to_run:
            continue
        log.info(f"Running step: {step_name}")
        step_impl(context)

    log.info(f"All done!")

    if "venv" in steps_to_run:
        log.info("Remember to activate the venv ...")


if __name__ == "__main__":
    step_names = [v[0] for v in steps]

    parser = argparse.ArgumentParser(description="Build")
    parser.add_argument(
        "selected_steps",
        nargs="*",
        default="all",
        choices=step_names + ["all"],
        help="Steps selected to run",
    )
    parser.add_argument(
        "-n",
        "--no",
        dest="disabled_steps",
        action="append",
        help="Disable selected steps",
        default=[],
        choices=step_names,
    )
    parser.add_argument("-V", "--venv-name", default="dev_env", help="Name of venv to create")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase verbosity")

    args = parser.parse_args()

    if args.selected_steps == "all":
        args.selected_steps = list(step_names)

    context = Context(args)

    main(context)
