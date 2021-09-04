import cmd
from importlib.abc import Loader
import os
import sys
from importlib.util import module_from_spec, spec_from_file_location
from typing import Any, Dict, List, Optional

import asciistuff
import colorama
from termcolor2 import colored

colorama.init()


class MopShell(cmd.Cmd):
    """
    Implements the whole framework shell interaction.
    """

    def __init__(self, completekey="tab", stdin=None, stdout=None):
        super().__init__(completekey=completekey, stdin=stdin, stdout=stdout)

        if sys.platform == "win32":
            print("\t\tRunning PYMOP on Windows, autocompletion might not work")

        # load the banner
        self.intro = asciistuff.Lolcat(asciistuff.Banner("   M.O.P"))

        self.modules = []
        self.current_module = None
        self._real_module = None
        self.prompt = colored("puppeteer> ", "green")

        # Load framework resources
        self._load_modules()

    def precmd(self, line):
        command = line[:1]
        if command == "$":
            line = "shell " + line[1:]
        return super().precmd(line)

    def postcmd(self, stop, line):
        if self.current_module is not None:
            print(
                asciistuff.Cowsay(
                    "Master of puppets is pulling the strings: using "
                    + self.current_module
                )
            )
            self.prompt = colored(self.current_module + "> ", "red")
        else:
            self.prompt = self.prompt = colored("puppeteer> ", "green")
        return super().postcmd(stop, line)

    # region   ++++++++++++    Private utility methods     ++++++++++++++
    def _tree_walk(self, path: str):
        for dir_entry in os.scandir(path):
            if dir_entry.name != "__init__.py" and dir_entry.is_file():
                yield dir_entry.name, dir_entry.path
            elif dir_entry.is_dir():
                yield from self._tree_walk(dir_entry.path)

    def _load_modules(self):
        """
        Loads all modules under modules/**/*.
        In MOP, modules behaves like modules on metasploit,
        we should have a module for every security goal we might
        target. For example, modules for scanning, password brute-forcing,
        WAF-evasion, etc should be provided.
        Modules routes are conformed in a tree-walk, so adding new modules
        is straight forward.
        Like with metasploit, modules must follow a convention, so the framework
        can detect what it should do, the configuration it needs to run, and how to
        run it. For the moment, every module must define a description Doc-string,
        a params function which returns the state of the module config, a set function
        which configures the modules settings and a run function to run the module
        """
        modules_src = os.path.abspath("src/modules")

        # perform a tree walk over modules directory
        for file_name, file_path in self._tree_walk(modules_src):
            try:
                # try to find a spec for this file and construct a module
                # from it
                spec = spec_from_file_location(file_name, file_path)
                assert spec is not None
                module = module_from_spec(spec)
                assert spec.loader is not None
                spec.loader.exec_module(module)
                self.modules.append(module)
            except:
                pass

    def _display_available_modules(self):
        num_columns = 4
        modules = map(
            lambda mod: (mod.__name__, mod.revision, mod.__doc__), self.modules
        )

        print("{:<15} {:<80} {:<150}".format("Module", "Revision", "Description"))
        print("-" * 80)

        for name, rev, doc in modules:
            print("{:<15} {:<80} {:<150}".format(name, rev, doc))

    def _display_module(self, module: str):
        mod = next((x for x in self.modules if x.__name__ == module), None)
        if mod is None:
            print("No module named: {} available".format(module))
        else:
            print("\t\t\tDescription")
            print("-*80")
            print(mod.__doc__)

    def _try_set_module(self, module: str):
        """
        Search the list of loaded modules for one with
        the given name.
        """
        loaded_module = next((x for x in self.modules if x.__name__ == module), None)
        if loaded_module is not None:
            self.current_module = module
            self._real_module = loaded_module
        else:
            print("No module named {} available".format(module))

    # endregion  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # region    +++++++++++++++++       BUILT-IN COMMANDS    ++++++++++++++++++
    def do_modules(self, module: Optional[str] = None):
        """
        With no arguments, list available modules,
        if 1 or more arguments are passed, the help
        of those modules is concatenated and displayed.
        """
        if module is None or module == "":
            self._display_available_modules()
        else:
            self._display_module(module)

    def do_use(self, module: str):
        if module != "":
            self._try_set_module(module)
        else:
            self.current_module = None
            self.current_module = None

    def do_exit(self, line):
        return True

    def do_shell(self, line):
        os.system(line)

    # endregion +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
