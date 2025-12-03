# -*- coding: utf-8 -*-

"""
https://strandsagents.com/latest/documentation/docs/examples/python/weather_forecaster/
"""

import random
import json
import logging

import strands
from strands.agent.agent_result import AgentResult
from boto_session_manager import BotoSesManager
from pydantic import BaseModel, Field

# Enable debug logging for strands to see detailed model interactions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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


def print_model_interactions(result: AgentResult):
    """Print detailed information about each model call cycle with Bedrock interactions."""
    print("\n" + "="*80)
    print("BEDROCK MODEL INTERACTION CYCLES")
    print("="*80)

    for cycle_num, trace in enumerate(result.metrics.traces, start=1):
        trace_dict = trace.to_dict()
        cycle_name = trace_dict.get('name', 'Unknown')

        # Get cycle timing information
        duration = trace_dict.get('duration', 'N/A')
        if duration:
            duration_ms = duration * 1000
            print(f"\n┌─ CYCLE {cycle_num}: {cycle_name} (Duration: {duration_ms:.2f}ms) ─────────────────")
        else:
            print(f"\n┌─ CYCLE {cycle_num}: {cycle_name} ─────────────────")

        # Process children to find stream_messages and tool calls
        children = trace_dict.get('children', [])

        for child_idx, child in enumerate(children, 1):
            child_name = child.get('name', '')
            child_message = child.get('message', {})
            child_duration = child.get('duration', 0)

            if 'stream_messages' in child_name:
                # This is a Bedrock API call
                duration_ms = child_duration * 1000 if child_duration else 0
                print(f"│")
                print(f"├─ 🤖 BEDROCK CALL (Duration: {duration_ms:.2f}ms)")
                print(f"│  Role: {child_message.get('role', 'assistant')}")

                content = child_message.get('content', [])

                # Extract and display thinking
                for block_idx, block in enumerate(content):
                    if 'text' in block:
                        text = block['text'].strip()
                        if '<thinking>' in text:
                            thinking_content = text.replace('<thinking>', '').replace('</thinking>', '').strip()
                            print(f"│")
                            print(f"│  💭 Thinking:")
                            for line in thinking_content.split('\n'):  # Show first 3 lines
                                print(f"│     {line}")
                            if len(thinking_content.split('\n')) > 3:
                                print(f"│     ...")
                        else:
                            print(f"│")
                            print(f"│  📝 Response:")
                            for line in text.split('\n'):
                                print(f"│     {line}")

                    # Display tool use
                    if 'toolUse' in block:
                        tool_use = block['toolUse']
                        tool_name = tool_use.get('name', 'Unknown')
                        tool_use_id = tool_use.get('toolUseId', '')
                        tool_input = tool_use.get('input', {})
                        print(f"│")
                        print(f"│  🔧 Tool Use: {tool_name}")
                        print(f"│     ID: {tool_use_id}")
                        print(f"│     Input:")
                        input_json = json.dumps(tool_input, indent=8)
                        for line in input_json.split('\n'):
                            print(f"│       {line}")

            elif 'Tool:' in child_name:
                print(f"│")
                print(f"├─ ⚙️  TOOL EXECUTION: {child_name}")
                tool_message = child.get('message', {})
                if tool_message:
                    content = tool_message.get('content', [])
                    for block in content:
                        if 'toolResult' in block:
                            tool_result = block['toolResult']
                            status = tool_result.get('status', 'unknown')
                            status_icon = '✅' if status == 'success' else '❌'
                            print(f"│  {status_icon} Status: {status}")
                            result_content = tool_result.get('content', [])
                            for res_block in result_content:
                                if 'text' in res_block:
                                    print(f"│  📤 Result: {res_block['text']}")

            elif 'Recursive call' in child_name:
                print(f"│")
                print(f"├─ 🔄 RECURSIVE CALL (continues to next cycle)")

        print(f"└─────────────────────────────────────────────────────────────────")

        # Show token usage if available
        if cycle_num == len(result.metrics.traces):
            print(f"\n📊 Total tokens used across all cycles:")
            print(f"   - Input: {result.metrics.accumulated_usage.get('inputTokens', 'N/A')}")
            print(f"   - Output: {result.metrics.accumulated_usage.get('outputTokens', 'N/A')}")


def send(
    query: str,
):
    print("\n==================== Query ====================")
    print(query)
    print("\n--- Running agent ---")
    result = agent.__call__(query)

    # Print detailed model interactions from traces
    print_model_interactions(result)

    print("\n" + "="*80)
    print("FINAL RESULT")
    print("="*80)
    print(f"\n---------- Stop Reason: {result.stop_reason}")
    print(f"\n---------- Message Content:")
    for content_block in result.message.get('content', []):
        if 'text' in content_block:
            print(content_block['text'])

    print(f"\n---------- Metrics:")
    print(f"  - Total Cycles: {result.metrics.cycle_count}")
    print(f"  - Input Tokens: {result.metrics.accumulated_usage.get('inputTokens', 'N/A')}")
    print(f"  - Output Tokens: {result.metrics.accumulated_usage.get('outputTokens', 'N/A')}")
    print(f"  - Total Tokens: {result.metrics.accumulated_usage.get('totalTokens', 'N/A')}")
    print(f"  - Latency: {result.metrics.accumulated_metrics.get('latencyMs', 'N/A')}ms")

    return result


if __name__ == "__main__":
    query_1 = "What's the weather at 38.9072, 77.0369?"
    send(query_1)
    # query_2 = "What is the temperature in Fahrenheit?"
    # send(query_2)

"""
2025-12-02 23:48:37,641 - botocore.credentials - INFO - Found credentials in shared credentials file: ~/.aws/credentials

==================== Query ====================
What's the weather at 38.9072, 77.0369?

--- Running agent ---
2025-12-02 23:48:37,671 - strands.telemetry.metrics - INFO - Creating Strands MetricsClient
<thinking> To provide the weather information for the given coordinates, I will use the get_weather tool. The required parameters are the latitude and longitude, which have been provided. I will pass these coordinates to the tool to get the weather details.</thinking>

Tool #1: get_weather
The current weather at the coordinates 38.9072, 77.0369 is 19.6°C. For more detailed weather information such as humidity, wind speed, and precipitation, additional queries may be necessary.
================================================================================
BEDROCK MODEL INTERACTION CYCLES
================================================================================

┌─ CYCLE 1: Cycle 1 ─────────────────
│
├─ 🤖 BEDROCK CALL (Duration: 811.62ms)
│  Role: assistant
│
│  💭 Thinking:
│     To provide the weather information for the given coordinates, I will use the get_weather tool. The required parameters are the latitude and longitude, which have been provided. I will pass these coordinates to the tool to get the weather details.
│
│  🔧 Tool Use: get_weather
│     ID: tooluse_BGMMLn4rSdqYewqWtE2Veg
│     Input:
│       {
│               "input": {
│                       "lat": 38.9072,
│                       "lng": 77.0369
│               }
│       }
│
├─ ⚙️  TOOL EXECUTION: Tool: get_weather
│  ✅ Status: success
│  📤 Result: temperature=19.6
│
├─ 🔄 RECURSIVE CALL (continues to next cycle)
└─────────────────────────────────────────────────────────────────

┌─ CYCLE 2: Cycle 2 (Duration: 470.34ms) ─────────────────
│
├─ 🤖 BEDROCK CALL (Duration: 470.06ms)
│  Role: assistant
│
│  📝 Response:
│     The current weather at the coordinates 38.9072, 77.0369 is 19.6°C. For more detailed weather information such as humidity, wind speed, and precipitation, additional queries may be necessary.
└─────────────────────────────────────────────────────────────────

📊 Total tokens used across all cycles:
   - Input: 1197
   - Output: 143

================================================================================
FINAL RESULT
================================================================================

Stop Reason: end_turn

Message Content:
The current weather at the coordinates 38.9072, 77.0369 is 19.6°C. For more detailed weather information such as humidity, wind speed, and precipitation, additional queries may be necessary.

Metrics:
  - Total Cycles: 2
  - Input Tokens: 1197
  - Output Tokens: 143
  - Total Tokens: 1340
  - Latency: 1135ms
"""
