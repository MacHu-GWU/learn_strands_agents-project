# Strands Agents 调试指南：Trace、Message 和日志系统

See `learn_strands_agents-project/docs/source/01-Learn-Strands-Agents/learn_strands_agents_example_get_weather.py`

## 📋 问题背景

当使用 Strands Agents 开发 AI 代理时，我们需要理解：
1. **Agent 的内部思考过程**（thinking steps）
2. **每一轮与 LLM（如 Bedrock）的交互细节**
3. **所有的工具调用和结果**
4. **完整的对话历史**

虽然 Strands 默认会调用 `agent(query)` 并返回最终结果，但这个过程中发生的所有中间步骤都被隐藏了。本文档记录了如何系统地展示这些信息。

---

## 🔍 核心概念：Trace vs Log

### Log（日志）- 简单的事件记录

```
2025-12-03 00:51:22,229 - botocore.credentials - INFO - Found credentials in ~/.aws/credentials
2025-12-03 00:51:22,281 - strands.telemetry.metrics - INFO - Creating Strands MetricsClient
```

**特点：**
- 平面结构，无层级关系
- 只是记录"发生了什么"
- 时间线式，难以回溯对象状态
- 适合快速问题排查

### Trace（追踪）- 结构化的性能和流程记录

```python
{
    "id": "b648ad1c-86f4-4c2e-bf95-7a4695641e62",    # 唯一ID，可定位
    "name": "Cycle 1",                                 # 操作名称
    "parent_id": None,                                 # 层级关系
    "children": [                                      # 子操作
        {
            "id": "f172a99f-8e33-414f-96fd-4693ad63085f",
            "name": "stream_messages",
            "parent_id": "b648ad1c-86f4-4c2e-bf95-7a4695641e62",
            "duration": 0.8042969703674316,            # 精确耗时（秒）
            "message": { ... }                         # 该阶段的消息
        }
    ]
}
```

**特点：**
- 树形结构，层级关系清晰
- 记录"发生了什么、为什么、耗时多少"
- 支持因果关系追踪（parent-child ID）
- 适合性能分析和流程重现

### 对比总结

| 方面 | Log | Trace |
|-----|-----|-------|
| 结构 | 平面文本 | 树形/图形结构 |
| 用途 | 事件记录 | 性能分析 + 流程追踪 |
| 时间精度 | 秒级 | 毫秒/微秒级 |
| 因果关系 | 无 | 有（parent-child） |
| 可查询性 | 困难 | 容易（通过ID/名称） |

---

## 🏗️ Agent 执行流程 - Cycle 含义

### 多轮交互模式

当你调用 `agent(query)` 时，实际上发生了多个 **Cycle**（循环）：

```
CYCLE 1 - 第一次与 Bedrock 交互
  ├─ 🤖 Bedrock API 调用 (883ms)
  │  ├─ 输入：系统提示 + 用户问题 + 工具定义
  │  └─ 输出：thinking + tool_use (get_weather)
  ├─ ⚙️ 本地工具执行 (4.5ms)
  │  └─ 执行 get_weather(lat=38.9072, lng=77.0369)
  │     返回 temperature=19.2
  └─ 🔄 递归到下一个 cycle

CYCLE 2 - 第二次与 Bedrock 交互
  ├─ 🤖 Bedrock API 调用 (544ms)
  │  ├─ 输入：系统提示 + 对话历史 + tool_result
  │  └─ 输出：最终答案（无 tool_use）
  └─ ✅ 完成
```

**关键理解：**
- 每个 Cycle 代表一次完整的推理循环
- Trace 捕捉每个 Cycle 的所有子操作及其耗时
- `agent.messages` 保存完整的对话历史

---

## 📊 实现的功能

### 1. 完整对话历史展示

使用 `agent.messages` 展示所有的对话消息，包括：
- 👤 **USER 消息**：用户输入
- 🤖 **ASSISTANT 消息**：模型思考和工具调用
- ⚙️ **TOOL RESULT 消息**：工具执行结果

```python
📊 Total Messages: 4

┌─ MESSAGE 1: 👤 USER ─────────────────────────
│  Content Blocks: 1
│  [1] Block Type: ['text']
│      What's the weather at 38.9072, 77.0369?

┌─ MESSAGE 2: 🤖 ASSISTANT ─────────────────────
│  Content Blocks: 2
│  [1] Block Type: ['text']
│      <thinking> 用户提供了坐标...使用 get_weather 工具 </thinking>
│  [2] Block Type: ['toolUse']
│      Tool Name: get_weather
│      Tool Use ID: tooluse_nlPz0-5sTMCbe6G8LPiCIw
│      Input: {"input": {"lat": 38.9072, "lng": 77.0369}}

┌─ MESSAGE 3: 👤 USER ─────────────────────────
│  Content Blocks: 1
│  [1] Block Type: ['toolResult']
│      Tool Use ID: tooluse_nlPz0-5sTMCbe6G8LPiCIw
│      Status: success
│      Content: temperature=19.2

┌─ MESSAGE 4: 🤖 ASSISTANT ─────────────────────
│  Content Blocks: 1
│  [1] Block Type: ['text']
│      当前坐标的天气温度为 19.2°C...
```

### 2. Trace 性能分析 - 5 个实用例子

#### 例子 1：找出最慢的操作
```
Slowest operation: stream_messages
  Parent cycle: Cycle 1
  Duration: 883.20ms
```
**用途**：诊断哪个环节最慢，找出优化方向

#### 例子 2：验证 Trace 层级关系
```
🔗 Parent Trace: Cycle 1 (ID: 98e2bc5c-c44...)
   └─ ✓ Child 1: stream_messages
      ID: e043e6e3-4d3...
      Parent ID: 98e2bc5c-c44... (匹配✓)
      Duration: 883.20ms
   └─ ✓ Child 2: Tool: get_weather
      Duration: 4.54ms
```
**用途**：调试时验证因果关系是否正确

#### 例子 3：延迟分解（成本分析）
```
Cycle 2:
  Total Duration: 543.83ms
    - stream_messages: 543.64ms (100.0%)
```
**用途**：分析每一步的成本占比，找出主要消耗

#### 例子 4：按条件查询
```
Found 2 Bedrock API calls:
  1. Duration: 883.20ms, ID: e043e6e3-4d32-44...
  2. Duration: 543.64ms, ID: fc95bbe2-dfb5-45...
```
**用途**：快速查找特定类型的操作

#### 例子 5：Trace 元数据
```
Trace 1 Metadata: (empty)
  Child 2 Metadata: {'toolUseId': 'tooluse_mwsX...', 'tool_name': 'get_weather'}
```
**用途**：追踪额外的上下文信息（工具ID、自定义属性等）

---

## 🔧 使用示例

```python
# 1. 创建自定义 callback handler 捕捉事件
class LoggingCallbackHandler:
    def __init__(self):
        self.events = []

    def __call__(self, **kwargs):
        self.events.append(kwargs)
        # 实时日志输出
        if kwargs.get("reasoningText"):
            print(f"[THINKING] {kwargs['reasoningText']}")

# 2. 创建 Agent，使用自定义 handler
callback_handler = LoggingCallbackHandler()
agent = strands.Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_weather],
    callback_handler=callback_handler,
)

# 3. 调用 agent（等待完成）
result = agent("What's the weather at 38.9072, 77.0369?")

# 4. 分析 Trace 数据
for trace in result.metrics.traces:
    trace_dict = trace.to_dict()
    print(f"Cycle: {trace_dict['name']}")
    print(f"Duration: {trace_dict['duration']*1000:.2f}ms")

    # 查找最慢的子操作
    for child in trace_dict['children']:
        print(f"  - {child['name']}: {child['duration']*1000:.2f}ms")

# 5. 查看完整对话历史
for msg in agent.messages:
    print(f"Role: {msg['role']}")
    for block in msg['content']:
        if 'text' in block:
            print(f"  Text: {block['text'][:100]}...")
```

---

## 📚 官方调研结果

### Strands 官方工具现状

#### ✅ 官方提供的功能

1. **OpenTelemetry 导出** - 支持导出到外部平台
   ```python
   from strands.telemetry import StrandsTelemetry
   StrandsTelemetry().setup_console_exporter()
   ```
   - 支持导出到 **Jaeger**、**Langfuse**、**AWS X-Ray** 等
   - 但这些都需要单独部署和配置

2. **Debug 日志** - 可以启用详细日志
   ```python
   logging.getLogger("strands").setLevel(logging.DEBUG)
   ```

3. **Agent 内置输出** - 默认 `PrintingCallbackHandler`
   - 流式输出 thinking 和响应
   - 可用 `callback_handler=None` 关闭

#### ❌ 官方没有提供的功能

| 功能 | Strands 官方 | 你的实现 |
|-----|-----------|--------|
| **本地展示完整 trace** | ❌ 需要外部工具 | ✅ 纯 Python 实现 |
| **展示完整对话历史** | ❌ 无现成方法 | ✅ 结构化显示 |
| **性能分析工具** | ❌ 需要自己实现 | ✅ 5 种分析方法 |
| **无需外部依赖** | ❌ 需要 OTLP 端点 | ✅ 开箱即用 |
| **开发调试友好** | ❌ 格式不够清晰 | ✅ 彩色输出 + 树形结构 |

### 第三方方案对比

#### Langfuse（最成熟的方案）
- ✅ 交互式 Dashboard
- ✅ Latency 分解
- ✅ Token 统计
- ✅ Tool 调用追踪
- ❌ 需要付费或自建
- ❌ 需要网络连接

#### Jaeger（开源方案）
- ✅ 开源免费
- ✅ 支持本地部署
- ❌ 需要 Docker 部署
- ❌ 学习成本较高

#### 你的实现（本文档方案）
- ✅ 纯 Python，无需部署
- ✅ 直接输出到控制台
- ✅ 代码简单易维护
- ✅ 适合快速开发和调试
- ❌ 不支持持久化存储
- ❌ 不支持分布式追踪

---

## 💡 建议：开源发布

### 项目潜力

你的实现**填补了一个空白**，Strands 官方没有提供现成的本地调试工具。这个库可以：

1. **解决开发痛点** - 让开发者快速理解 Agent 执行过程
2. **降低学习成本** - 提供友好的可视化输出
3. **支持本地开发** - 无需配置外部工具

### 建议的开源方案

#### 项目结构
```
strands-debug-toolkit/
├── strands_debug/
│   ├── __init__.py
│   ├── trace_visualizer.py     # Trace 展示和分析
│   ├── message_formatter.py     # 对话历史展示
│   ├── performance_analyzer.py  # 性能分析（5 个例子）
│   └── interactive_viewer.py    # 可选：交互式查看
├── examples/
│   ├── weather_agent.py         # 天气 Agent 示例
│   └── debug_output.py          # 调试输出示例
├── tests/
│   ├── test_trace_visualizer.py
│   └── test_message_formatter.py
├── README.md
├── pyproject.toml
└── setup.py
```

#### 命名选项
- `strands-trace-viewer` - 强调 trace 可视化
- `strands-debug` - 通用调试工具
- `agent-trace-pretty` - 强调友好输出
- `strands-debugger` - 类似 IDE debugger

### 可能的功能扩展

1. **交互式 REPL** - 在 Python REPL 中查询 trace
   ```python
   viewer = TraceViewer(result)
   viewer.find_slowest()
   viewer.show_cycle(1)
   viewer.export_json("trace.json")
   ```

2. **HTML 报告** - 生成可视化 HTML 报告
   ```python
   viewer.export_html("agent_run_report.html")
   ```

3. **实时监控** - 多次调用的对比
   ```python
   viewer.compare_runs([result1, result2, result3])
   ```

4. **成本计算** - Token 使用统计
   ```python
   viewer.estimate_cost(model="nova-micro", pricing={"input": 0.35, "output": 1.4})
   ```

### 发布到 PyPI

```bash
# 1. 安装工具
pip install build twine

# 2. 构建包
python -m build

# 3. 发布到 PyPI
twine upload dist/*
```

使用时：
```bash
pip install strands-debug
```

```python
from strands_debug import TraceViewer, MessageFormatter

result = agent("What's the weather?")
viewer = TraceViewer(result)
viewer.print_summary()

formatter = MessageFormatter(agent.messages)
formatter.print_conversation()
```

---

## 📖 相关官方文档

- [Strands Agents Trace 文档](https://strandsagents.com/latest/documentation/docs/user-guide/observability-evaluation/traces/)
- [Strands Agents Observability 文档](https://strandsagents.com/latest/documentation/docs/user-guide/observability-evaluation/observability/)
- [Langfuse 集成指南](https://langfuse.com/integrations/frameworks/strands-agents)
- [Strands Agents GitHub Discussions](https://github.com/strands-agents/sdk-python/discussions)

---

## 🎯 总结

### 关键收获

1. **Trace 的价值** - 不只是记录发生了什么，而是记录完整的执行图谱，包括因果关系、耗时、元数据
2. **多轮推理的可视化** - 理解 Cycle 和 Message 的对应关系，能够清晰地看到每一轮与 LLM 的交互
3. **官方空白** - Strands 官方没有提供本地、友好的 trace/message 展示工具
4. **社区机会** - 这是一个可以开源发布的有用工具

### 实践建议

- **开发调试** → 使用你的实现（本地、快速、无依赖）
- **生产监控** → 使用 Langfuse 或 Jaeger（持久化、分布式、专业）
- **团队协作** → 考虑开源发布，得到社区反馈和贡献

---

**文档创建时间**：2025-12-03
**Strands Agents 版本**：最新
**作者**：Claude AI
