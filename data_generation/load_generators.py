import importlib
import pkgutil

import data_generation.generators


def load_all_generators():
    """
    Dynamically imports all generator modules so that decorators execute
    and register functions into REGISTRY.
    """
    package = data_generation.generators

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):

        importlib.import_module(f"data_generation.generators.{module_name}")
