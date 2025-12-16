from ssm_cli.commands.ssh_proxy.server import SshServer
from ssm_cli.instances import Instances
from ssm_cli.config import CONFIG
from ssm_cli.commands.base import BaseCommand
from ssm_cli.cli_args import ARGS

import logging
logger = logging.getLogger(__name__)


class SshProxyCommand(BaseCommand):
    HELP="SSH ProxyCommand feature"
    def add_arguments(parser):
        parser.add_argument("group", type=str, help="group to run against")

    def run():
        logger.info("running proxycommand action")


        instances = Instances()
        instance = instances.select_instance(ARGS.group, CONFIG.actions.proxycommand.selector)

        if instance is None:
            logger.error("failed to select host")
            raise RuntimeError("failed to select host")

        logger.info(f"connecting to {repr(instance)}")
        
        server = SshServer(instance)
        server.start()
