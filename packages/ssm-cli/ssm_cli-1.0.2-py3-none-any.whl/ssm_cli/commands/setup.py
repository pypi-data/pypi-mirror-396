import argparse
import paramiko
from ssm_cli.commands.base import BaseCommand
from ssm_cli.xdg import get_conf_root, get_conf_file, get_ssh_hostkey
from ssm_cli.cli_args import ARGS
from ssm_cli.config import CONFIG
from confclasses import from_dict, save
from ssm_cli.console import console
from rich.markup import escape

GREY = "grey50"

import logging
logger = logging.getLogger(__name__)

class SetupCommand(BaseCommand):
    HELP = "Setups up ssm-cli"
    
    def add_arguments(parser):
        parser.add_argument("--replace-config", action=argparse.BooleanOptionalAction, default=False, help="if we should replace existing config file")
        parser.add_argument("--replace-hostkey", action=argparse.BooleanOptionalAction, default=False, help="if we should replace existing hostkey file (bare careful with this option)")

    def run():
        # Create the root config directory
        root = get_conf_root(False)
        logger.debug(f"Checking if {root} exists")
        if root.exists():
            logger.debug(f"{root} exists")
            if not root.is_dir():
                logger.error(f"{root} already exists and is not a directory. Manual cleanup is likely needed.")
                console.print(f"{root} already exists and is not a directory. Manual cleanup is likely needed.", style="red bold")
                return
            console.print(f"{root} - skipping (already exists)", style=GREY)
        else:
            root.mkdir(511, True, True)
            console.print(f"{root} created", style="green")


        # Create the config file
        path = get_conf_file(False)
        logger.debug(f"Checking if {path} exists")
        create_config = False
        if path.exists():
            logger.debug(f"{path} exists")
            if ARGS.replace_config:
                logger.info(f"{path} exists and --replace-config was set, unlink {path}")
                console.print(f"{path} removing", style="green")
                path.unlink(True)
                create_config = True
        else:
            logger.debug(f"{path} does not exist")
            create_config = True

        if create_config:
            logger.info(f"{path} creating")
            console.print(f"{path} creating", style="green")
            from_dict(CONFIG, {})

            text = escape(f"What tag to use to split up the instances [{CONFIG.group_tag_key}]: ")
            tag_key = console.input(text)
            CONFIG.group_tag_key = tag_key or CONFIG.group_tag_key
            console.print(f"Using '{CONFIG.group_tag_key}' as the group tag", style=GREY)
            logger.info(f"Writing config to {path}")

            with path.open("w+") as f:
                save(CONFIG, f)
                console.print(f"{path} created", style="green")

        # Create the ssh hostkey
        path = get_ssh_hostkey(False)
        create_key = False
        if path.exists():
            logger.debug(f"{path} exists")
            console.print(f"{path} skipping (already exists)")
            if ARGS.replace_hostkey:
                logger.info(f"{path} exists and --replace-hostkey was set, unlink {path}")
                console.print(f"{path} removing", style="green")
                path.unlink(True)
                create_key = True
        else:
            logger.debug(f"{path} does not exist")
            create_key = True
        
        if create_key:
            logger.info(f"{path} creating")
            host_key = paramiko.RSAKey.generate(1024)
            host_key.write_private_key_file(path)
            console.print(f"{path} created")