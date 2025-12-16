import sys
from analyst_klondike.features.data_context.arg_file_load.arg_load import (
    TooManyArgumentsException,
    process_args
)
from analyst_klondike.ui.runner_app import get_app


def analyst_klondike():
    try:
        app = get_app()
        process_args(sys.argv)
        app.run()
    except (FileNotFoundError, TooManyArgumentsException):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(f"Exception type: {exc_type}")
        print(f"Exception value: {exc_value}")
        print(f"Traceback object: {exc_traceback}")


if __name__ == "__main__":
    analyst_klondike()
