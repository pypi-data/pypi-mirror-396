from dotenv import load_dotenv

from chain_nhem_nhem.tools.registry import tool_registry, load_tools
from chain_nhem_nhem.llm.registry import load_drivers, llm_driver_registry
from chain_nhem_nhem.agent.agent import Agent
from chain_nhem_nhem.config import settings
from chain_nhem_nhem.logging import get_logger

logger = get_logger(__name__)


def create_agent(
    driver_name: str | None = None,
    max_steps: int = 5
) -> Agent:
    logger.info("Creating agent instance.")
    load_dotenv()
    load_drivers()
    load_tools()

    driver_name = driver_name or settings.DRIVER

    driver = llm_driver_registry.create(driver_name)
    logger.info(f"Using LLM driver: {driver_name} with {settings.MODEL} model.")
    return Agent(
        driver=driver,
        tool_registry=tool_registry,
        driver_name=driver_name,
        max_steps=max_steps
    )
