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
        self._loaded_modules_names = []
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
                self._loaded_modules_names.append(module.__name__)
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
            print(
                asciistuff.Cowsay(
                    "Master of puppets is pulling the strings: using "
                    + self.current_module
                )
            )
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
        """
        Picks a module and mark it for use by the framework.
        """
        if module != "":
            self._try_set_module(module)
        else:
            self.current_module = None
            self.current_module = None

    def do_exit(self, line):
        """
        Exits MOP
        """
        return True

    def do_shell(self, line):
        """
        Runs the command on the system default shell.
        The '$' character is an alias for this command.
        """
        os.system(line)

    def do_set(self, setting: str):
        """
        Sets a configuration setting for the current module.
        """
        if self._real_module is None:
            print("Set command depends on using a module. See 'use' for help.")
            return

        splitted_input = setting.split()
        if len(splitted_input) < 2:
            print("Invalid argument to split")
        else:
            key = splitted_input[0]
            value = " ".join(splitted_input[1:])
            self._real_module.set(key, value)

    def do_config(self, line: str):
        """
        Displays the current status of the selected
        module settings.
        """
        if self._real_module is None:
            print("'config' command depends on using a module. See 'use' for help.")
            return

        settings = self._real_module.params()
        if line != '':
            value = settings.get(line, None)
            if value is not None:
                print(value)
        else:
            print(settings)

    # endregion +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # region    +++++++++++++++++   Completion of commands   ++++++++++++++++++
    def complete_modules(
        self, text: str, line: str, begidx: int, endidx: int
    ) -> List[str]:
        return list(filter(lambda x: text in x, self._loaded_modules_names))

    def complete_use(self, text: str, line: str, begidx: int, endidx: int) -> List[str]:
        return list(filter(lambda x: text in x, self._loaded_modules_names))

    def complete_set(self, text: str, line: str, begidx: int, endidx: int) -> List[str]:
        if self._real_module is not None:
            settings = self._real_module.params()
            return (list(filter(lambda x: text in x, settings.keys())))
        else:
            return []

    # endregion +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
