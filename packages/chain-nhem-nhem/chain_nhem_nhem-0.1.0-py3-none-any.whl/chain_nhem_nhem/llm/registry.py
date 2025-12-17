import importlib
import importlib.util
import pkgutil
from pathlib import Path
from typing import Dict, Type

from chain_nhem_nhem.llm.llm_driver import LLMDriver
from chain_nhem_nhem.config import settings
from chain_nhem_nhem.logging import get_logger

logger = get_logger(__name__)


class LLMDriverRegistry:
    def __init__(self):
        self._drivers: Dict[str, Type[LLMDriver]] = {}

    def register(self, name: str, driver_cls: Type[LLMDriver]):
        self._drivers[name.lower()] = driver_cls

    def create(self, name: str) -> LLMDriver:
        name = name.lower()
        if name not in self._drivers:
            raise RuntimeError(f"LLM driver '{name}' not found in registry")
        return self._drivers[name]()


llm_driver_registry = LLMDriverRegistry()


# --------------------------------
# Load internal drivers (package)
# --------------------------------
def _load_internal_drivers():
    loaded_drivers = []
    package = "chain_nhem_nhem.llm.drivers"
    pkg = importlib.import_module(package)

    for _, module_name, _ in pkgutil.iter_modules(pkg.__path__):
        importlib.import_module(f"{package}.{module_name}")
        loaded_drivers.append(module_name)
    logger.info(f"Loaded internal drivers: {loaded_drivers}")


# --------------------------------
# Load app drivers (override)
# --------------------------------
def _load_app_drivers():
    loaded_drivers = []   
    drivers_dir = settings.APP_DRIVERS_PATH
    if not drivers_dir:
        return

    drivers_path = Path(drivers_dir).resolve()

    if not drivers_path.exists() or not drivers_path.is_dir():
        raise RuntimeError(
            f"APP_DRIVERS_PATH is invalid: {drivers_path}"
        )

    for file in drivers_path.iterdir():
        if file.is_file() and file.name.endswith("_driver.py"):
            module_name = f"app_driver_{file.stem}"

            spec = importlib.util.spec_from_file_location(
                module_name,
                file
            )

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            loaded_drivers.append(file.name)

    logger.info(f"Loaded external drivers: {loaded_drivers}")


# --------------------------------
# Public API
# --------------------------------
def load_drivers():
    # Internal drivers (default)
    _load_internal_drivers()

    # App drivers (override)
    _load_app_drivers()
