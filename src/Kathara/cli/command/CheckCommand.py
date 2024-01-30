import argparse
import os
import platform
import sys
from typing import List

from rich.console import Console

from ..ui.utils import create_panel
from ... import utils
from ... import version
from ...foundation.cli.command.Command import Command
from ...manager.Kathara import Kathara
from ...model.Lab import Lab
from ...setting.Setting import Setting
from ...strings import strings, wiki_description


class CheckCommand(Command):
    def __init__(self) -> None:
        Command.__init__(self)

        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(
            prog='kathara check',
            description=strings['check'],
            epilog=wiki_description,
            add_help=False
        )

        self.parser.add_argument(
            '-h', '--help',
            action='help',
            default=argparse.SUPPRESS,
            help='Show a help message and exit.'
        )

    def run(self, current_path: str, argv: List[str]) -> None:
        self.parse_args(argv)

        console = Console()
        console.print(create_panel("System Check", style="blue bold", justify="center"))
        console.print(f"Current Manager is:\t\t[cyan bold]{Kathara.get_instance().get_formatted_manager_name()}")
        console.print(f"Manager version is:\t\t[cyan bold]{Kathara.get_instance().get_release_version()}")
        console.print("Python version is:\t\t[cyan bold]%s" % sys.version.replace("\n", "- "))
        console.print(f"Kathara version is:\t\t[cyan bold]{version.CURRENT_VERSION}")

        def linux_platform_info():
            info = os.uname()
            return "%s-%s-%s" % (info.sysname, info.release, info.machine)

        platform_info = utils.exec_by_platform(
            linux_platform_info, lambda: platform.platform(), lambda: platform.platform()
        )
        console.print(f"Operating System version is:\t[cyan bold]{str(platform_info)}")

        with console.status(
                f"Trying to run container with `{Setting.get_instance().image}` image...",
                spinner="dots"
        ) as status:
            Setting.get_instance().open_terminals = False

            lab = Lab("kathara_test")
            lab.add_option('hosthome_mount', False)

            machine = lab.get_or_new_machine("hello_world")
            try:
                Kathara.get_instance().deploy_machine(machine)
                Kathara.get_instance().undeploy_machine(machine)
                console.print("[bold green]\u2713 Container run successfully.")
            except Exception as e:
                console.print(f"[bold red]\u00d7 Running container failed: {str(e)}")
