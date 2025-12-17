import warnings
from MEROAI import HfArgumentParser
from MEROAI.commands.add_fast_image_processor import AddFastImageProcessorCommand
from MEROAI.commands.add_new_model_like import AddNewModelLikeCommand
from MEROAI.commands.chat import ChatCommand
from MEROAI.commands.convert import ConvertCommand
from MEROAI.commands.download import DownloadCommand
from MEROAI.commands.env import EnvironmentCommand
from MEROAI.commands.run import RunCommand
from MEROAI.commands.serving import ServeCommand
def main_cli():
    warnings.warn(
        "`MEROAI-cli` is deprecated in favour of `MEROAI` directly and will be removed in v5.",
        DeprecationWarning,
    )
    main()
def main():
    parser = HfArgumentParser(prog="MEROAI CLI tool", usage="MEROAI <command> [<args>]")
    commands_parser = parser.add_subparsers(help="MEROAI command helpers")
    ChatCommand.register_subcommand(commands_parser)
    ConvertCommand.register_subcommand(commands_parser)
    DownloadCommand.register_subcommand(commands_parser)
    EnvironmentCommand.register_subcommand(commands_parser)
    RunCommand.register_subcommand(commands_parser)
    ServeCommand.register_subcommand(commands_parser)
    AddNewModelLikeCommand.register_subcommand(commands_parser)
    AddFastImageProcessorCommand.register_subcommand(commands_parser)
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        exit(1)
    service = args.func(args)
    service.run()
if __name__ == "__main__":
    main()