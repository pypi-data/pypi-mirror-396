import argparse
from pathlib import Path
from typing import Tuple

from selcraft.generate import build, config
from selcraft.logger import LogLevel
from selcraft.spec import schema
from selcraft.validation.config_validation import (
    NoDuplicateUDSPathRule,
    validate_config,
)
from selcraft.version import version


def parse_log_level_option(option: str) -> LogLevel:
    return LogLevel.from_string(option)


def parse_arguments() -> Tuple[argparse.Namespace, argparse.ArgumentParser]:
    parser = argparse.ArgumentParser(
        description="selcraft - Generate custom selinux-policies",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("--version", action="version", version=version())
    parser.add_argument(
        "--log-level",
        dest="log_level",
        default=LogLevel.INFO,
        type=parse_log_level_option,
        help="Set log level used by the application",
    )
    parser.add_argument(
        "--log-file",
        dest="log_file",
        type=Path,
        help="Path to the log file. If not given, logs will be printed to stderr.",
    )

    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.required = False

    add_version_parser(subparsers)
    add_generate_parser(subparsers)

    return parser.parse_args(), parser


def add_version_parser(parent_parser: argparse._SubParsersAction):
    version_parser = parent_parser.add_parser(
        "version", help="Diplay version of selcraft"
    )
    version_parser.set_defaults(func=lambda _: print(version()))


def add_generate_parser(parent_parser: argparse._SubParsersAction):
    generate_parser = parent_parser.add_parser(
        "generate", help="Generate a custom selinux policy"
    )
    generate_parser.set_defaults(func=cli_generate)

    generate_parser.add_argument(
        "--config",
        help="The configuration file used to build the selinux-policy for",
        required=True,
        type=str,
    )

    generate_parser.add_argument(
        "--template-dir",
        help="The directory containing available templates used to build the policies",
        required=False,
        type=str,
        default=Path(__file__).parent.resolve() / "templates",
    )

    generate_parser.add_argument(
        "--output-dir",
        help="The directory to save the generated files to",
        required=False,
        type=str,
        default="./out",
    )


def cli_generate(args: argparse.Namespace):

    conf = schema.load_file(Path(args.config))

    # TODO: replace path with installed path (needs packaging)
    spec = schema.load_file(
        Path(__file__).parent.resolve() / "spec" / "schema.1-0-0.json"
    )

    schema.validate_spec(conf, spec)
    validate_config(conf, rules=[NoDuplicateUDSPathRule()])

    jinja_data = config.build_jinja_data(conf)
    build.generate_new_policy(jinja_data, args.template_dir, args.output_dir)
