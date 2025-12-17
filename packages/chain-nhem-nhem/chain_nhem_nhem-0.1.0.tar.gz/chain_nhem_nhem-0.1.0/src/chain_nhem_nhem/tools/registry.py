import importlib
import importlib.util
import pkgutil
from pathlib import Path

from chain_nhem_nhem.tools.base import Tool
from chain_nhem_nhem.config import settings
from chain_nhem_nhem.logging import get_logger

logger = get_logger(__name__)


class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, tool: Tool):
        # Tool name is the key → automatic override
        self._tools[tool.name] = tool

    def get(self, name: str):
        return self._tools.get(name)

    def all(self):
        return list(self._tools.values())

    def for_driver(self, driver_name: str):
        if driver_name == "gemini":
            return [
                tool.to_gemini_tool()
                for tool in self._tools.values()
                if isinstance(tool, Tool)
            ]

        raise RuntimeError(f"Driver '{driver_name}' does not support tools")


tool_registry = ToolRegistry()

# --------------------------------
# Load internal tools (package)
# --------------------------------
def _load_internal_tools():
    loaded_tools = []
    import chain_nhem_nhem.tools  # internal package

    for _, module_name, _ in pkgutil.iter_modules(chain_nhem_nhem.tools.__path__):
        if module_name.endswith("_tool"):
            importlib.import_module(f"chain_nhem_nhem.tools.{module_name}")
            loaded_tools.append(module_name)
    logger.info(f"Loaded internal tools: {loaded_tools}")

# --------------------------------
# Load app tools (override)
# --------------------------------
def _load_app_tools():
    loaded_tools = []
    tools_dir = settings.APP_TOOLS_PATH
    if not tools_dir:
        return  # external tools are optional

    tools_path = Path(tools_dir).resolve()

    if not tools_path.exists() or not tools_path.is_dir():
        raise RuntimeError(
            f"Invalid APP_TOOLS_PATH: {tools_path}"
        )

    for file in tools_path.iterdir():
        if file.is_file() and file.name.endswith("_tool.py"):
            module_name = f"app_tool_{file.stem}"

            spec = importlib.util.spec_from_file_location(
                module_name,
                file
            )

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            loaded_tools.append(file.name)
    logger.info(f"Loaded external tools: {loaded_tools}")


# --------------------------------
# Public API
# --------------------------------
def load_tools():
    # Internal Tools (default)
    _load_internal_tools()

    # App Tools (override)
    _load_app_tools()
