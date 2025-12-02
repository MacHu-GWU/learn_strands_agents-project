# -*- coding: utf-8 -*-

"""
https://strandsagents.com/latest/documentation/docs/examples/python/weather_forecaster/
"""

from boto_session_manager import BotoSesManager
import strands
from strands_tools import http_request

bsm = BotoSesManager(profile_name="esc_app_dev_us_east_1")
# model_id="us.amazon.nova-pro-v1:0"
# model_id="us.amazon.nova-lite-v1:0"
model_id = "us.amazon.nova-micro-v1:0"

# Define a weather-focused system prompt
WEATHER_SYSTEM_PROMPT = """You are a weather assistant with HTTP capabilities. You can:

1. Make HTTP requests to the National Weather Service API
2. Process and display weather forecast data
3. Provide weather information for locations in the United States

When retrieving weather information:
1. First get the coordinates or grid information using https://api.weather.gov/points/{latitude},{longitude} or https://api.weather.gov/points/{zipcode}
2. Then use the returned forecast URL to get the actual forecast

When displaying responses:
- Format weather data in a human-readable way
- Highlight important information like temperature, precipitation, and alerts
- Handle errors appropriately
- Convert technical terms to user-friendly language

Always explain the weather conditions clearly and provide context for the forecast.
"""

# Create an agent with HTTP capabilities
weather_agent = strands.Agent(
    model=strands.models.BedrockModel(
        boto_session=bsm.boto_ses,
        model_id=model_id,
    ),
    system_prompt=WEATHER_SYSTEM_PROMPT,
    tools=[http_request],  # Explicitly enable http_request tool
)
response = weather_agent("What's the weather like in Seattle?")
print(f"{type(response) = }")
print(f"{response = }")

"""
<thinking>
    To provide the weather information for Seattle, I need to first obtain the coordinates for Seattle using the National Weather Service API. Then, I will use these coordinates to get the weather forecast.
</thinking>
Tool #1: http_request
<thinking>
    I have successfully retrieved the coordinates for Seattle. Now, I need to use the forecast URL provided in the response to get the actual weather forecast for Seattle.
</thinking> 
Tool #2: http_request
<thinking>
    I have retrieved the weather forecast for Seattle. Now, I will format this information in a human-readable way, highlighting important details such as temperature, precipitation, and any alerts.
</thinking>

Here is the weather forecast for Seattle:

**Today (This Afternoon):**
- **Time:** 12:00 PM - 6:00 PM PDT
- **Temperature:** 63°F
- **Forecast:** Chance of light rain
- **Wind:** South southwest at 8 mph
- **Probability of Precipitation:** 13%

**Tonight:**
- **Time:** 6:00 PM - 6:00 AM PDT
- **Temperature:** Low of 54°F
- **Forecast:** Rain
- **Wind:** South at 6 to 13 mph
- **Probability of Precipitation:** 97%
- **Details:** Rain likely throughout the night. New rainfall amounts between a quarter and half of an inch possible.

**Friday:**
- **Time:** 6:00 AM - 6:00 PM PDT
- **Temperature:** High of 60°F
- **Forecast:** Rain
- **Wind:** South at 9 to 13 mph
- **Probability of Precipitation:** 100%
- **Details:** Rain likely throughout the day. New rainfall amounts between 1 and 2 inches possible.

**Friday Night:**
- **Time:** 6:00 PM - 6:00 AM PDT
- **Temperature:** Low of 48°F
- **Forecast:** Rain
- **Wind:** South at 10 mph
- **Probability of Precipitation:** 96%
- **Details:** Rain likely throughout the night. New rainfall amounts between a quarter and half of an inch possible.

**Saturday:**
- **Time:** 6:00 AM - 6:00 PM PDT
- **Temperature:** High of 55°F
- **Forecast:** Rain
- **Wind:** South southeast at 10 to 16 mph
- **Probability of Precipitation:** 98%
- **Details:** Rain likely throughout the day. New rainfall amounts between a half and three quarters of an inch possible.

**Saturday Night:**
- **Time:** 6:00 PM - 6:00 AM PDT
- **Temperature:** Low of 45°F
- **Forecast:** Rain
- **Wind:** South at 10 to 17 mph
- **Probability of Precipitation:** 96%
- **Details:** Rain likely throughout the night. New rainfall amounts between a quarter and half of an inch possible.

**Sunday:**
- **Time:** 6:00 AM - 6:00 PM PDT
- **Temperature:** High of 53°F
- **Forecast:** Light rain
- **Wind:** South at 7 to 10 mph
- **Probability of Precipitation:** 93%

**Sunday Night:**
- **Time:** 6:00 PM - 6:00 AM PDT
- **Temperature:** Low of 44°F
- **Forecast:** Light rain
- **Wind:** South southwest at 7 mph
- **Probability of Precipitation:** 87%

**Monday:**
- **Time:** 6:00 AM - 6:00 PM PDT
- **Temperature:** High of 53°F
- **Forecast:** Light rain likely
- **Wind:** South at 7 mph
- **Probability of Precipitation:** 72%

**Monday Night:**
- **Time:** 6:00 PM - 6:00 AM PDT
- **Temperature:** Low of 41°F
- **Forecast:** Light rain likely
- **Wind:** Southeast at 6 mph
- **Probability of Precipitation:** 62%

**Tuesday:**
- **Time:** 6:00 AM - 6:00 PM PDT
- **Temperature:** High of 54°F
- **Forecast:** Chance of light rain
- **Wind:** Northeast at 6 mph
- **Probability of Precipitation:** 53%

**Tuesday Night:**
- **Time:** 6:00 PM - 6:00 AM PDT
- **Temperature:** Low of 46°F
- **Forecast:** Light rain likely
- **Wind:** Southeast at 8 mph
- **Probability of Precipitation:** 59%

**Wednesday:**
- **Time:** 6:00 AM - 6:00 PM PDT
- **Temperature:** High of 57°F
- **Forecast:** Light rain likely
- **Wind:** South at 8 mph
- **Probability of Precipitation:** 69%

**Wednesday Night:**
- **Time:** 6:00 PM - 6:00 AM PDT
- **Temperature:** Low of 48°F
- **Forecast:** Light rain likely
- **Wind:** South at 8 mph
- **Probability of Precipitation:** 70%

Remember to check this forecast regularly for updates as weather conditions can change. Stay safe and prepared!type(response) = <class 'strands.agent.agent_result.AgentResult'>
response = AgentResult(
    stop_reason='end_turn', 
    message={
        'role': 'assistant', 
        'content': [
            {
                'text': '...',
            }
        ]
    }, 
    metrics=EventLoopMetrics(
        cycle_count=3, 
        tool_metrics={
            'http_request': ToolMetrics(
                tool={
                    'toolUseId': 'tooluse_IHyFdi-8Qp-xAtkSUpkllg', 
                    'name': 'http_request', 
                    'input': {
                        'method': 'GET', 
                        'url': 'https://api.weather.gov/gridpoints/SEW/125,68/forecast'
                    }
                }, 
                call_count=2, 
                success_count=2, 
                error_count=0, 
                total_time=31.14823317527771
            )
        }, 
        cycle_durations=[
            5.824352025985718
        ],
        traces=[
            <strands.telemetry.metrics.Trace object at 0x108129850>, 
            <strands.telemetry.metrics.Trace object at 0x108117a10>, 
            <strands.telemetry.metrics.Trace object at 0x10812a010>
        ], 
        accumulated_usage={
            'inputTokens': 10656, 
            'outputTokens': 1255, 
            'totalTokens': 11911,
        }, 
        accumulated_metrics={'latencyMs': 7371}
    ), 
    state={}, 
    interrupts=None
) 
"""