from chain_nhem_nhem.llm.registry import llm_driver_registry
from chain_nhem_nhem.llm.llm_driver import LLMDriver
from chain_nhem_nhem.config import settings

def get_llm_driver() -> LLMDriver:
    driver_name = settings.DRIVER
    return llm_driver_registry.create(driver_name)