import argparse
import sys
from argparse import Namespace


class CustomFormatter(argparse.HelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings:
            (metavar,) = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            # change to
            #    -s, --long ARGS
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    # parts.append('%s %s' % (option_string, args_string))
                    parts.append("%s" % option_string)
                parts[-1] += " %s" % args_string
            return ", ".join(parts)


def get_command_line_arguments() -> Namespace:
    """Setup command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="refcheck",
        usage="refcheck [OPTIONS] [PATH ...]",
        formatter_class=CustomFormatter,
    )  # type: ignore
    parser.add_argument(
        "paths",
        metavar="PATH",
        type=str,
        nargs="*",
        help="Markdown files or directories to check",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        metavar="",
        type=str,
        nargs="*",
        default=[],
        help="Files or directories to exclude",
    )  # type: ignore
    parser.add_argument(
        "-cm",
        "--check-remote",
        action="store_true",
        help="Check remote references (HTTP/HTTPS links)",
    )  # type: ignore
    parser.add_argument("-nc", "--no-color", action="store_true", help="Turn off colored output")  # type: ignore
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")  # type: ignore
    parser.add_argument(
        "--allow-absolute",
        action="store_true",
        help="Allow absolute path references like [ref](/path/to/file.md)",
    )  # type: ignore

    # Check if the user has provided any files or directories
    args = parser.parse_args()
    if not args.paths:
        parser.print_help()
        sys.exit(0)

    return args
