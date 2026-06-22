import json

class APISimulator:
    """Simulates external API consumption for weather data securely."""
    def __init__(self):
        self.connection_protocol = "TLS 1.3"

    def get_secure_weather_data(self, injected_weather: int) -> dict:
        """Fetches and strictly sanitizes JSON weather data to prevent injection."""
        try:
            raw_json = f'{{"weather_condition": {injected_weather}, "malicious_code": "<script>alert(1)</script>"}}'
            parsed_data = json.loads(raw_json)
            
            sanitized = {
                "weather": int(parsed_data.get("weather_condition", 1))
            }
            if not (1 <= sanitized["weather"] <= 5):
                raise ValueError("External API data out of logical bounds.")
            return sanitized
        except Exception:
            return {"weather": 1}