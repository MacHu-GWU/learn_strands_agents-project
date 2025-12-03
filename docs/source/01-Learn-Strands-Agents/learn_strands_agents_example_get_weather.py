# -*- coding: utf-8 -*-

"""
https://strandsagents.com/latest/documentation/docs/examples/python/weather_forecaster/
"""

import random
import dataclasses

from boto_session_manager import BotoSesManager
import strands
from pydantic import BaseModel, Field
from rich import print as rprint


class GetWeatherInput(BaseModel):
    lat: float = Field(
        description="Latitude of the location",
    )
    lng: float = Field(
        description="Longitude of the location",
    )

class GetWeatherOutput(BaseModel):
    temperature: float = Field(
        description="Current temperature in Celsius",
    )

@strands.tool(
    name="get_weather",
)
def get_weather(
    input: GetWeatherInput,
) -> GetWeatherOutput:
    """
    Getting the weather in Celsius for a given latitude and longitude.
    """
    return GetWeatherOutput(
        temperature=random.randint(100, 300) / 10,
    )

bsm = BotoSesManager(profile_name="esc_app_dev_us_east_1")
# model_id="us.amazon.nova-pro-v1:0"
# model_id="us.amazon.nova-lite-v1:0"
model_id = "us.amazon.nova-micro-v1:0"

SYSTEM_PROMPT = """
You are a weather assistant.

Use the available weather tools to provide accurate, concise weather information.
"""

model = strands.models.BedrockModel(
    boto_session=bsm.boto_ses,
    model_id=model_id,
)
agent = strands.Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        get_weather,
    ],
)


def send(
    query: str,
):
    print("\n==================== Query ====================")
    print(query)
    print("\n--- Running agent ---")
    result = agent.__call__(query)
    print("\n--- Final Result ---")
    rprint(dataclasses.asdict(result))
    for ith, trace in enumerate(result.metrics.traces, start=1):
        print(f"\n--- Traces {ith} ---")
        rprint(trace.to_dict())
    return result

from strands.agent.agent import Agent
from strands.agent.agent_result import AgentResult

query_1 = "What's the weather at 38.9072, 77.0369?"
send(query_1)
# query_2 = "What is the temperature in Fahrenheit?"
# run(query_2)

"""
==================== Query ====================
What's the weather at 38.9072, 77.0369?

--- Running agent ---
<thinking> The user has provided a latitude and longitude, which I can use to call the get_weather tool to retrieve the current weather information at that location. </thinking>

Tool #1: get_weather
The current weather at the specified location (38.9072, 77.0369) shows a temperature of approximately 25.9 degrees Celsius. For more detailed weather information, such as humidity, wind speed, and forecast, additional calls to the tool might be required.
--- Final Result ---
{
    'stop_reason': 'end_turn',
    'message': {
        'role': 'assistant',
        'content': [
            {
                'text': 'The current weather at the specified location (38.9072,
77.0369) shows a temperature of approximately 25.9 degrees Celsius. For more 
detailed weather information, such as humidity, wind speed, and forecast, 
additional calls to the tool might be required.'
            }
        ]
    },
    'metrics': {
        'cycle_count': 2,
        'tool_metrics': {
            'get_weather': {
                'tool': {
                    'toolUseId': 'tooluse_DRrjiQBBSIejccCSFDIciQ',
                    'name': 'get_weather',
                    'input': {'input': {'lat': 38.9072, 'lng': 77.0369}}
                },
                'call_count': 1,
                'success_count': 1,
                'error_count': 0,
                'total_time': 0.0010581016540527344
            }
        },
        'cycle_durations': [0.7253127098083496],
        'traces': [
            <strands.telemetry.metrics.Trace object at 0x10792ffe0>,
            <strands.telemetry.metrics.Trace object at 0x1084b5cd0>
        ],
        'accumulated_usage': {
            'inputTokens': 1165,
            'outputTokens': 137,
            'totalTokens': 1302
        },
        'accumulated_metrics': {'latencyMs': 1231}
    },
    'state': {},
    'interrupts': None,
    'structured_output': None
}

--- Traces 1 ---
{
    'id': 'b648ad1c-86f4-4c2e-bf95-7a4695641e62',
    'name': 'Cycle 1',
    'raw_name': None,
    'parent_id': None,
    'start_time': 1764730209.3232808,
    'end_time': None,
    'duration': None,
    'children': [
        {
            'id': 'f172a99f-8e33-414f-96fd-4693ad63085f',
            'name': 'stream_messages',
            'raw_name': None,
            'parent_id': 'b648ad1c-86f4-4c2e-bf95-7a4695641e62',
            'start_time': 1764730209.323311,
            'end_time': 1764730210.127608,
            'duration': 0.8042969703674316,
            'children': [],
            'metadata': {},
            'message': {
                'role': 'assistant',
                'content': [
                    {
                        'text': '<thinking> The user has provided a latitude and
longitude, which I can use to call the get_weather tool to retrieve the current 
weather information at that location. </thinking>\n'
                    },
                    {
                        'toolUse': {
                            'toolUseId': 'tooluse_DRrjiQBBSIejccCSFDIciQ',
                            'name': 'get_weather',
                            'input': {
                                'input': {'lat': 38.9072, 'lng': 77.0369}
                            }
                        }
                    }
                ]
            }
        },
        {
            'id': 'd8f8ea5d-9f24-481d-abe7-c44b8ab01b48',
            'name': 'Tool: get_weather',
            'raw_name': 'get_weather - tooluse_DRrjiQBBSIejccCSFDIciQ',
            'parent_id': 'b648ad1c-86f4-4c2e-bf95-7a4695641e62',
            'start_time': 1764730210.128263,
            'end_time': 1764730210.1293561,
            'duration': 0.001093149185180664,
            'children': [],
            'metadata': {
                'toolUseId': 'tooluse_DRrjiQBBSIejccCSFDIciQ',
                'tool_name': 'get_weather'
            },
            'message': {
                'role': 'user',
                'content': [
                    {
                        'toolResult': {
                            'toolUseId': 'tooluse_DRrjiQBBSIejccCSFDIciQ',
                            'status': 'success',
                            'content': [{'text': 'temperature=25.9'}]
                        }
                    }
                ]
            }
        },
        {
            'id': '7d827dbe-d422-4dfe-a473-4885a0557c60',
            'name': 'Recursive call',
            'raw_name': None,
            'parent_id': 'b648ad1c-86f4-4c2e-bf95-7a4695641e62',
            'start_time': 1764730210.1296692,
            'end_time': 1764730210.855105,
            'duration': 0.725435733795166,
            'children': [],
            'metadata': {},
            'message': None
        }
    ],
    'metadata': {},
    'message': None
}

--- Traces 2 ---
{
    'id': 'b70e535f-d042-47cb-bfcb-928bca916275',
    'name': 'Cycle 2',
    'raw_name': None,
    'parent_id': None,
    'start_time': 1764730210.129722,
    'end_time': 1764730210.8550348,
    'duration': 0.7253127098083496,
    'children': [
        {
            'id': 'ca5a5290-9d04-4c9d-8b53-1f8f77a0d7a5',
            'name': 'stream_messages',
            'raw_name': None,
            'parent_id': 'b70e535f-d042-47cb-bfcb-928bca916275',
            'start_time': 1764730210.129879,
            'end_time': 1764730210.854955,
            'duration': 0.7250759601593018,
            'children': [],
            'metadata': {},
            'message': {
                'role': 'assistant',
                'content': [
                    {
                        'text': 'The current weather at the specified location 
(38.9072, 77.0369) shows a temperature of approximately 25.9 degrees Celsius. 
For more detailed weather information, such as humidity, wind speed, and 
forecast, additional calls to the tool might be required.'
                    }
                ]
            }
        }
    ],
    'metadata': {},
    'message': None
}
"""
