import importlib.metadata
import sys
from argparse import ArgumentParser

from silx import config

try:
    from ewoksorange.canvas.main import arg_parser
    from ewoksorange.canvas.main import main as ewoksorange_main
except ImportError as e:
    error_msg = f"ERROR: {e.msg}.\n"
    error_msg += "To use `darfix` command, please use the full installation of darfix:\npip install darfix[full]\n"
    sys.stdout.write(error_msg)
    exit()


def main(argv=None):

    config._MPL_TIGHT_LAYOUT = True

    parser = ArgumentParser(parents=[arg_parser()], add_help=False)

    parser.add_argument(
        "--version",
        action="store_true",
        help="Display version",
    )

    parser.add_argument(
        "--use-opengl-plot",
        action="store_true",
        help="Use opengl as default backend for all plots. Faster but some limitations : https://www.silx.org/doc/silx/2.2.1/troubleshooting.html",
    )

    if argv is None:
        argv = sys.argv
    options, _ = parser.parse_known_args(argv[1:])

    if options.use_opengl_plot:
        config.DEFAULT_PLOT_BACKEND = "gl"
        argv.pop(argv.index("--use-opengl-plot"))

    if options.version:
        print(f"Darfix version: {importlib.metadata.version('darfix')}")
        return
    if ewoksorange_main is None:
        raise ImportError("Install darfix[full] to use the Orange canvas.")
    ewoksorange_main()


if __name__ == "__main__":
    sys.exit(main())
