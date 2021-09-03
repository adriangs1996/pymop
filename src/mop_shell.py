import cmd
from importlib.util import spec_from_file_location, module_from_spec
from typing import List, Dict, Any, Optional
import os
import sys

class MopShell(cmd.Cmd):
    """
    Implements the whole framework shell interaction.
    """
    def __init__(self, completekey='tab', stdin=None, stdout=None):
        super().__init__(completekey=completekey, stdin=stdin, stdout=stdout)

        if sys.platform == 'win32':
            print("Running PYMOP on Windows, autocompletion may not work")

        # load the banner
        with open("assets/mop_banner.txt", "r") as file:
            self.intro = file.read()

        self.modules = []

        # Load framework resources
        self._load_modules()

    #region   ++++++++++++    Private utility methods     ++++++++++++++
    def _tree_walk(self, path: str):
        for dir_entry in os.scandir(path):
            if dir_entry.name != '__init__.py' and dir_entry.is_file():
                yield dir_entry.name, dir_entry.path
            elif dir_entry.is_dir():
                yield from self._tree_walk(dir_entry.path)

    def _load_modules(self) -> List[Any]:
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
                module = module_from_spec(spec)
                self.modules.append(module)
            except:
                pass

    def _display_available_modules(self):
        num_columns = 4
        modules = map(lambda mod: (mod.__name__, mod.revision, mod.__doc__), self.modules)
        
        print("{:<15} {:<30} {:<100}".format("Module", "Revision", "Description"))
        print("-"*80)

        for name, rev, doc in modules:
            print("{:<15} {:<30} {:<100}".format(name, rev, doc))

    def _display_module(self, module: str):
        mod = next((x for x in self.modules if x.__name__ == module), None)
        if mod is None:
            print("No module named: {} available".format(module))
        else:
            print("\t\t\tDescription")
            print("-*80")
            print(mod.__doc__)

    #endregion  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # region    +++++++++++++++++       BUILT-IN COMMANDS    ++++++++++++++++++
    def do_modules(self, module: Optional[str] = None):
        """
        With no arguments, list available modules,
        if 1 or more arguments are passed, the help
        of those modules is concatenated and displayed.
        """
        if module is None or module == '':
            self._display_available_modules()
        else:
            self._display_module(module)
    # endregion +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
