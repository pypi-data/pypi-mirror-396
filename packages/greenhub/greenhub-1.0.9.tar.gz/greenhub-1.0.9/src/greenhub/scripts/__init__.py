import os
import sys
import inspect
import importlib


def greenhub_cli_script():
    """
    This method is registered as an Entry Point (console script) during the package installation,
    allowing the user to execute the command `greenhub <command>` in the terminal
    (more details: https://setuptools.pypa.io/en/latest/userguide/entry_point.html).
    Here, the provided `<command>` is parsed, and the corresponding functionality to be executed is called.
    """

    request_action = sys.argv[1]
    if request_action in ['help', '-h', '--help']:
        print_cli_description()
        return
    if request_action == 'test':
        run_implementation_test()
        return

    print(f"Error: given command `{request_action}` is not known by greenhub. "
          f"Please checkout the official greenhub.ai documentation.")


def print_cli_description():
    """
    Print a textual description of the `greenhub` command-line interface.
    """

    sections = []
    sections.append(
        "Welcome to the command-line interface of the `greenhub` package."
        "\nThe following describes the available command-line functionalities. "
        "\nFor more information, please visit docs.greenhub.ai."
    )
    sections.append(
        "Usage:"
        "\n  greenhub <command>"
    )
    sections.append(
        "Commands:"
        "\n  help     Show help for commands."
        "\n  test     Test if the current directory meets all requirements to be uploaded "
        "as a zip file (model) to greenhub.ai."
    )
    print('\n'.join(sections))


def run_implementation_test():
    """
    Test if the current directory meets all requirements to be uploaded as a zip file (model) to greenhub.ai.
    For now, it is only tested if the current directory contains a `run.py` file with a `run` with a specific signature.
    """

    RUN_FILE_NAME = 'run.py'
    RUN_FUNCTION_NAME = 'run'

    # check if a 'run.py' file exists in the current directory
    run_file_path = os.path.join(os.getcwd(), RUN_FILE_NAME)
    if not os.path.exists(run_file_path) or not os.path.isfile(run_file_path):
        print("FAILURE: no 'run.py' file found in the current directory. "
              "Please checkout the official greenhub.ai documentation.")
        return

    # check 'run.py' file for 'run' function implementation -> load function if exists
    # load 'run.py' module
    spec = importlib.util.spec_from_file_location(RUN_FILE_NAME[:-3], run_file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # check if 'run' exists and load it
    if hasattr(module, 'run'):
        run_func = getattr(module, RUN_FUNCTION_NAME)
    else:
        print("FAILURE: found no 'run' function implementation in 'run.py'. "
              "For more information please checkout the official greenhub.ai documentation.")
        return

    # check 'run' function parameter names and types
    run_signature = inspect.signature(run_func)
    params = run_signature.parameters.values()
    param_names = [p.name for p in params]
    param_types = [p.annotation.__name__ for p in params]
    # expected signatures
    EXPECTED_SIGNATURE = {
        'names': ['year', 'month'],
        'types': ['int', 'int'],
        'signature': 'run(year: int, month: int)'
    }
    # check
    if param_names != EXPECTED_SIGNATURE['names']:
        print(f"FAILURE: 'run' function implementation does not expect the right parameters. "
              f"The 'run' function signature should look like: '{EXPECTED_SIGNATURE['signature']}' "
              f"For more information please checkout the official greenhub.ai documentation.")
        return
    if param_types != EXPECTED_SIGNATURE['types']:
        print(f"FAILURE: 'run' function implementation required parameters are of the wrong type. "
              f"The 'run' function signature should look like: '{EXPECTED_SIGNATURE['signature']}' "
              f"For more information please checkout the official greenhub.ai documentation.")
        return

    # success
    print("SUCCESS: the 'run' implementation was checked successfully and can now be uploaded to greenhub.ai. "
          "For more information and step by step tutorials, please checkout greenhub.ai.")
