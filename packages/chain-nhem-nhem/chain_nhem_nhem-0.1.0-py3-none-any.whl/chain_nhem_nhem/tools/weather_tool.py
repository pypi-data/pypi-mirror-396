from pydantic import BaseModel, Field
from chain_nhem_nhem.tools.base import Tool
from chain_nhem_nhem.tools.registry import tool_registry

#----------------------------
# Args Schemas
#----------------------------
class TemperatureArgs(BaseModel):
    location: str = Field(..., description="Location to check the weather.")
    unit: str = Field("celsius", description="Temperature unit (celsius/fahrenheit).")

class HotiestCityArgs(BaseModel):
    country: str = Field(..., description="Country to find the hottest city in.")

class CityForecastArgs(BaseModel):
    city: str = Field(..., description="City to get the weather forecast for.")


#----------------------------
# Tool Implementation
#----------------------------
class TemperatureTool(Tool):
    def __init__(self):
        self.name = "get_temperature"
        self.description = "Get the temperature for a given location."
        self.args_schema = TemperatureArgs

    def __call__(self, args: TemperatureArgs) -> dict:
        return {
            "location": args.location,
            "temperature": 22 if args.unit == "celsius" else 72,
            "unit": args.unit
        }

class HottestCityTool(Tool):
    def __init__(self):
        self.name = "get_hottest_city"
        self.description = "Get the hottest city in a given country and state."
        self.args_schema = HotiestCityArgs

    def __call__(self, args: HotiestCityArgs) -> dict:
        return {
            "country": args.country,
            "hottest_city": "Rio de Janeiro",
            "temperature": 45
        }

class CityForecastTool(Tool):
    def __init__(self):
        self.name = "get_city_forecast"
        self.description = "Get the weather forecast for a given city."
        self.args_schema = CityForecastArgs

    def __call__(self, args: CityForecastArgs) -> dict:
        return {
            "city": args.city,
            "forecast": [
                {"day": "Monday", "condition": "Sunny", "high": 25, "low": 15},
                {"day": "Tuesday", "condition": "Rain", "high": 20, "low": 12},
                {"day": "Wednesday", "condition": "Cloudy", "high": 22, "low": 14},
            ]
        }

#----------------------------
# Tools Registration
# ---------------------------    
tool_registry.register(TemperatureTool())
tool_registry.register(HottestCityTool())
tool_registry.register(CityForecastTool())
