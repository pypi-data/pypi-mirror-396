class GeminiHelper:
    REMOVE_KEYS = {"title", "examples", "default"}

    @staticmethod
    def strip_schema(schema):
        """Remove campos incompatíveis com Gemini Tool Schemas"""
        if isinstance(schema, dict):
            return {
                key: GeminiHelper.strip_schema(value)
                for key, value in schema.items()
                if key not in GeminiHelper.REMOVE_KEYS
            }
        elif isinstance(schema, list):
            return [GeminiHelper.strip_schema(item) for item in schema]
        return schema