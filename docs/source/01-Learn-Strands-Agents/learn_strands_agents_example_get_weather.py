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

    # Print detailed conversation history
    print("\n" + "─"*80)
    print("─"*80)
    print("COMPLETE CONVERSATION HISTORY")
    print("─"*80)
    print("─"*80)

    print(f"\n📊 Total Messages: {len(agent.messages)}")

    for msg_idx, message in enumerate(agent.messages, 1):
        msg_role = message.get('role', 'unknown')
        msg_content = message.get('content', [])

        # Role header with visual separator
        role_emoji = "👤" if msg_role == "user" else "🤖" if msg_role == "assistant" else "⚙️"
        print(f"\n┌─ MESSAGE {msg_idx}: {role_emoji} {msg_role.upper()} ─" + "─"*50)

        # Content blocks
        content_blocks = msg_content if isinstance(msg_content, list) else []
        print(f"│  Content Blocks: {len(content_blocks)}")

        for block_idx, block in enumerate(content_blocks, 1):
            print(f"│")
            print(f"│  [{block_idx}] Block Type: {list(block.keys())}")

            # Handle text content
            if 'text' in block:
                text = block['text']
                print(f"│      Type: text")
                lines = text.split('\n')
                for line_idx, line in enumerate(lines):
                    # Wrap long lines
                    if len(line) > 70:
                        # First part
                        print(f"│      {line[:70]}")
                        # Remaining parts
                        remaining = line[70:]
                        while remaining:
                            print(f"│      {remaining[:70]}")
                            remaining = remaining[70:]
                    else:
                        print(f"│      {line}")

            # Handle tool use content
            elif 'toolUse' in block:
                tool_use = block['toolUse']
                print(f"│      Type: toolUse")
                print(f"│      Tool Name: {tool_use.get('name', 'Unknown')}")
                print(f"│      Tool Use ID: {tool_use.get('toolUseId', 'N/A')}")
                print(f"│      Input:")
                tool_input = tool_use.get('input', {})
                input_json = json.dumps(tool_input, indent=6, ensure_ascii=False)
                for input_line in input_json.split('\n'):
                    print(f"│         {input_line}")

            # Handle tool result content
            elif 'toolResult' in block:
                tool_result = block['toolResult']
                print(f"│      Type: toolResult")
                print(f"│      Tool Use ID: {tool_result.get('toolUseId', 'N/A')}")
                print(f"│      Status: {tool_result.get('status', 'N/A')}")
                print(f"│      Content:")
                result_content = tool_result.get('content', [])
                for res_block in result_content:
                    if isinstance(res_block, dict) and 'text' in res_block:
                        res_text = res_block['text']
                        for res_line in res_text.split('\n'):
                            if res_line.strip():
                                print(f"│         {res_line}")

        print(f"└─" + "─"*76)

    print("\n" + "─"*80)
    print("─"*80)

    return result


def analyze_trace_performance(result: AgentResult):
    """Example: Use trace data for performance analysis."""
    print("\n" + "="*80)
    print("TRACE ANALYSIS EXAMPLES - How to use Trace data")
    print("="*80)

    print("\n🔍 Example 1: Find slowest operation")
    print("─"*80)
    slowest_duration = 0
    slowest_trace = None
    slowest_parent = None

    for cycle_num, trace in enumerate(result.metrics.traces, start=1):
        trace_dict = trace.to_dict()
        cycle_name = trace_dict.get('name', '')

        for child in trace_dict.get('children', []):
            child_duration = child.get('duration', 0)
            if child_duration > slowest_duration:
                slowest_duration = child_duration
                slowest_trace = child
                slowest_parent = cycle_name

    if slowest_trace:
        print(f"Slowest operation: {slowest_trace.get('name')}")
        print(f"  Parent cycle: {slowest_parent}")
        print(f"  Duration: {slowest_duration*1000:.2f}ms")

    print("\n🔍 Example 2: Track trace hierarchy (parent-child relationships)")
    print("─"*80)
    for trace in result.metrics.traces:
        trace_dict = trace.to_dict()
        trace_id = trace_dict.get('id', 'N/A')
        trace_name = trace_dict.get('name', 'Unknown')
        print(f"\n🔗 Parent Trace: {trace_name} (ID: {trace_id[:12]}...)")

        for child_idx, child in enumerate(trace_dict.get('children', []), 1):
            child_id = child.get('id', 'N/A')
            child_name = child.get('name', 'Unknown')
            child_parent = child.get('parent_id', 'N/A')
            child_duration = child.get('duration', 0)

            # 验证parent_id指向正确的parent
            parent_match = "✓" if child_parent == trace_id else "✗"
            print(f"   └─ {parent_match} Child {child_idx}: {child_name}")
            print(f"      ID: {child_id[:12]}...")
            print(f"      Parent ID: {child_parent[:12]}...")
            print(f"      Duration: {child_duration*1000:.2f}ms")

    print("\n🔍 Example 3: Calculate latency breakdown")
    print("─"*80)
    for cycle_num, trace in enumerate(result.metrics.traces, start=1):
        trace_dict = trace.to_dict()
        cycle_name = trace_dict.get('name', '')
        cycle_duration = trace_dict.get('duration', 0)

        print(f"\n{cycle_name}:")
        if cycle_duration:
            print(f"  Total Duration: {cycle_duration*1000:.2f}ms")

            children = trace_dict.get('children', [])
            for child in children:
                child_name = child.get('name', '')
                child_duration = child.get('duration', 0)
                if child_duration:
                    percentage = (child_duration / cycle_duration) * 100
                    print(f"    - {child_name}: {child_duration*1000:.2f}ms ({percentage:.1f}%)")

    print("\n🔍 Example 4: Query specific trace by ID and name")
    print("─"*80)
    # Find all traces with 'stream_messages' in the name
    bedrock_calls = []
    for trace in result.metrics.traces:
        trace_dict = trace.to_dict()
        for child in trace_dict.get('children', []):
            if 'stream_messages' in child.get('name', ''):
                bedrock_calls.append(child)

    print(f"Found {len(bedrock_calls)} Bedrock API calls:")
    for idx, call in enumerate(bedrock_calls, 1):
        call_duration = call.get('duration', 0)
        call_id = call.get('id', 'N/A')
        print(f"  {idx}. Duration: {call_duration*1000:.2f}ms, ID: {call_id[:16]}...")

    print("\n🔍 Example 5: Trace metadata and custom attributes")
    print("─"*80)
    for idx, trace in enumerate(result.metrics.traces, start=1):
        trace_dict = trace.to_dict()
        metadata = trace_dict.get('metadata', {})
        print(f"Trace {idx} Metadata: {metadata if metadata else '(empty)'}")

        for child_idx, child in enumerate(trace_dict.get('children', []), 1):
            child_metadata = child.get('metadata', {})
            if child_metadata:
                print(f"  Child {child_idx} Metadata: {child_metadata}")

    print("\n" + "="*80)


if __name__ == "__main__":
    query_1 = "What's the weather at 38.9072, 77.0369?"
    result = send(query_1)

    # 在输出完对话后，分析trace数据
    analyze_trace_performance(result)

    # query_2 = "What is the temperature in Fahrenheit?"
    # send(query_2)

"""
2025-12-03 00:51:22,229 - botocore.credentials - INFO - Found credentials in shared credentials file: ~/.aws/credentials

==================== Query ====================
What's the weather at 38.9072, 77.0369?

--- Running agent ---
2025-12-03 00:51:22,281 - strands.telemetry.metrics - INFO - Creating Strands MetricsClient
<thinking> The User has provided a latitude and longitude. To provide the weather information, I will use the "get_weather" tool with the provided coordinates. </thinking>

Tool #1: get_weather
The current weather at the coordinates 38.9072, 77.0369 is 19.2°C. If you need more detailed weather information or have any other questions, feel free to ask!
================================================================================
BEDROCK MODEL INTERACTION CYCLES
================================================================================

┌─ CYCLE 1: Cycle 1 ─────────────────
│
├─ 🤖 BEDROCK CALL (Duration: 914.42ms)
│  Role: assistant
│
│  💭 Thinking:
│     The User has provided a latitude and longitude. To provide the weather information, I will use the "get_weather" tool with the provided coordinates.
│
│  🔧 Tool Use: get_weather
│     ID: tooluse_rH-YEfUNQpmstbA40PavOw
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
│  📤 Result: temperature=19.2
│
├─ 🔄 RECURSIVE CALL (continues to next cycle)
└─────────────────────────────────────────────────────────────────

┌─ CYCLE 2: Cycle 2 (Duration: 556.65ms) ─────────────────
│
├─ 🤖 BEDROCK CALL (Duration: 556.52ms)
│  Role: assistant
│
│  📝 Response:
│     The current weather at the coordinates 38.9072, 77.0369 is 19.2°C. If you need more detailed weather information or have any other questions, feel free to ask!
└─────────────────────────────────────────────────────────────────

📊 Total tokens used across all cycles:
   - Input: 1181
   - Output: 124

================================================================================
FINAL RESULT
================================================================================

---------- Stop Reason: end_turn

---------- Message Content:
The current weather at the coordinates 38.9072, 77.0369 is 19.2°C. If you need more detailed weather information or have any other questions, feel free to ask!

---------- Metrics:
  - Total Cycles: 2
  - Input Tokens: 1181
  - Output Tokens: 124
  - Total Tokens: 1305
  - Latency: 1190ms

────────────────────────────────────────────────────────────────────────────────
────────────────────────────────────────────────────────────────────────────────
COMPLETE CONVERSATION HISTORY
────────────────────────────────────────────────────────────────────────────────
────────────────────────────────────────────────────────────────────────────────

📊 Total Messages: 4

┌─ MESSAGE 1: 👤 USER ───────────────────────────────────────────────────
│  Content Blocks: 1
│
│  [1] Block Type: ['text']
│      Type: text
│      What's the weather at 38.9072, 77.0369?
└─────────────────────────────────────────────────────────────────────────────

┌─ MESSAGE 2: 🤖 ASSISTANT ───────────────────────────────────────────────────
│  Content Blocks: 2
│
│  [1] Block Type: ['text']
│      Type: text
│      <thinking> The User has provided a latitude and longitude. To provide 
│      the weather information, I will use the "get_weather" tool with the pr
│      ovided coordinates. </thinking>
│      
│
│  [2] Block Type: ['toolUse']
│      Type: toolUse
│      Tool Name: get_weather
│      Tool Use ID: tooluse_rH-YEfUNQpmstbA40PavOw
│      Input:
│         {
│               "input": {
│                     "lat": 38.9072,
│                     "lng": 77.0369
│               }
│         }
└─────────────────────────────────────────────────────────────────────────────

┌─ MESSAGE 3: 👤 USER ───────────────────────────────────────────────────
│  Content Blocks: 1
│
│  [1] Block Type: ['toolResult']
│      Type: toolResult
│      Tool Use ID: tooluse_rH-YEfUNQpmstbA40PavOw
│      Status: success
│      Content:
│         temperature=19.2
└─────────────────────────────────────────────────────────────────────────────

┌─ MESSAGE 4: 🤖 ASSISTANT ───────────────────────────────────────────────────
│  Content Blocks: 1
│
│  [1] Block Type: ['text']
│      Type: text
│      The current weather at the coordinates 38.9072, 77.0369 is 19.2°C. If 
│      you need more detailed weather information or have any other questions
│      , feel free to ask!
└─────────────────────────────────────────────────────────────────────────────

────────────────────────────────────────────────────────────────────────────────
────────────────────────────────────────────────────────────────────────────────
"""
