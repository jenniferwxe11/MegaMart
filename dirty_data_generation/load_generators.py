import importlib
import pkgutil

import dirty_data_generation.generators as pkg


def load_all_generators():
    """
    Dynamically imports all generator modules so that decorators execute
    and register functions into REGISTRY.
    """
    for _, module_name, _ in pkgutil.iter_modules(pkg.__path__):

        importlib.import_module(f"dirty_data_generation.generators.{module_name}")
