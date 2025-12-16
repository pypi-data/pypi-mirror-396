import sys
import logging


import confclasses
from ssm_cli.config import CONFIG
from ssm_cli.xdg import get_conf_file, get_log_file
from ssm_cli.commands import COMMANDS
from ssm_cli.cli_args import CliArgumentParser, ARGS
from ssm_cli.aws import AWSAuthError, AWSAccessDeniedError
from ssm_cli.console import console
from ssm_cli.logging import setup_logging, configure_log_level
from rich.markup import escape

logger = logging.getLogger(__name__)

def cli(argv: list = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    # Initialize logging
    setup_logging()

    # Manually set the log level now, so we get accurate logging during argument parsing
    for i, arg in enumerate(argv):
        if arg == '--log-level':
            configure_log_level(argv[i+1])
        if arg.startswith('--log-level='):
            configure_log_level(arg.split('=')[1])

    logger.debug(f"CLI called with {argv}")

    parser = CliArgumentParser()

    for name, command in COMMANDS.items():
        command_parser = parser.add_command_parser(name, command.HELP)
        command.add_arguments(command_parser)

    parser.parse_args(argv)

    logger.debug(f"Arguments: {ARGS}")

    if not ARGS.command:
        parser.print_help()
        return 1
    
    # Setup is a special case, we cannot load config if we dont have any.
    if ARGS.command == "setup":
        return _run()
    
    try:
        with open(get_conf_file(), 'r') as file:
            confclasses.load(CONFIG, file)
            ARGS.update_config()
            logger.debug(f"Config: {CONFIG}")
    except EnvironmentError as e:
        console.print(f"Invalid config: {e}", style="red")
        return 1
    
    configure_log_level(CONFIG.log.level)

    
    for logger_name, level in CONFIG.log.loggers.items():
        logger.debug(f"setting logger {logger_name} to {level}")
        configure_log_level(level, name=logger_name)


    if ARGS.command not in COMMANDS:
        console.print(f"failed to find action {ARGS.action}", style="red")
        return 1
    
    return _run()

def _run():
    """
    Run a command, better exceptions and logging
    """
    try:
        COMMANDS[ARGS.command].run()
        logger.info(f"Command {ARGS.command} completed successfully")
        return 0
    except AWSAuthError as e:
        console.print(f"AWS Authentication error: {e}", style="red")
        return 1
    except AWSAccessDeniedError as e:
        logger.error(f"access denied: {e}")
        console.print(f"Access denied, see README for details on required permissions", style="bold red")
        console.print(escape(str(e.__cause__)), style="grey50")
        return 1
    except Exception as e:
        logger.error(f"Unhandled exception in {ARGS.command}")
        log_path = str(get_log_file())
        console.print(f"Unhandled exception, check [link=file://{log_path}]{log_path}[/link] for more information", style="red")
        console.print(f"Error: {e}", style="red bold")
        logger.exception(e, stack_info=True, stacklevel=20)
        return 1
