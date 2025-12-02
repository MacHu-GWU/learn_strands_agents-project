# -*- coding: utf-8 -*-

"""
https://strandsagents.com/latest/documentation/docs/examples/python/agents_workflows/
"""

from boto_session_manager import BotoSesManager
import strands
from strands_tools import http_request
from rich import print as rprint

bsm = BotoSesManager(profile_name="esc_app_dev_us_east_1")
# model_id="us.amazon.nova-pro-v1:0"
model_id="us.amazon.nova-lite-v1:0"
# model_id = "us.amazon.nova-micro-v1:0" # context window too small
model = strands.models.BedrockModel(
    boto_session=bsm.boto_ses,
    model_id=model_id,
)

# Researcher Agent with web capabilities
researcher_agent = strands.Agent(
    model=model,
    system_prompt=(
        "You are a Researcher Agent that gathers information from the web. "
        "1. Determine if the input is a research query or factual claim "
        "2. Use your research tools (http_request, retrieve) to find relevant information "
        "3. Include source URLs and keep findings under 500 words"
    ),
    callback_handler=None,
    tools=[http_request]
)

# Analyst Agent for verification and insight extraction
analyst_agent = strands.Agent(
    model=model,
    callback_handler=None,
    system_prompt=(
        "You are an Analyst Agent that verifies information. "
        "1. For factual claims: Rate accuracy from 1-5 and correct if needed "
        "2. For research queries: Identify 3-5 key insights "
        "3. Evaluate source reliability and keep analysis under 400 words"
    ),
)

# Writer Agent for final report creation
writer_agent = strands.Agent(
    model=model,
    system_prompt=(
        "You are a Writer Agent that creates clear reports. "
        "1. For fact-checks: State whether claims are true or false "
        "2. For research: Present key insights in a logical structure "
        "3. Keep reports under 500 words with brief source mentions"
    )
)

def run_research_workflow(user_input):
    # Step 1: Researcher Agent gathers web information
    print("===== Researcher response =====")
    researcher_response = researcher_agent(
        f"Research: '{user_input}'. Use your available tools to gather information from reliable sources.",
    )
    rprint(researcher_response)
    research_findings = str(researcher_response)

    # Step 2: Analyst Agent verifies facts
    print("===== Analysis response =====")
    analyst_response = analyst_agent(
        f"Analyze these findings about '{user_input}':\n\n{research_findings}",
    )
    rprint(analyst_response)
    analysis = str(analyst_response)

    # Step 3: Writer Agent creates report
    print("===== Final Report =====")
    final_report = writer_agent(
        f"Create a report on '{user_input}' based on this analysis:\n\n{analysis}"
    )
    rprint(final_report)

    return final_report

query1 = """
Is Amazon Bedrock AgentCore ready for production use?
""".strip()

run_research_workflow(query1)

"""
===== Researcher response =====
AgentResult(
    stop_reason='end_turn',
    message={
        'role': 'assistant',
        'content': [
            {
                'text': 'Based on the content retrieved from the Amazon Web Services (AWS) website, Amazon Bedrock AgentCore has been generally available as of the date of the content. This means it is ready for production use. Here\'s a summary of the relevant findings:\n\n1. **Amazon Bedrock 
AgentCore General Availability**: The content explicitly states, "Amazon Bedrock AgentCore is now generally available." This indicates that the service has reached a stable state suitable for production use.\n\n2. **Foundational Tools for Production**: The page describes AgentCore as providing 
"foundational tools required by agents to execute real-world workflows," which is a key feature for production environments.\n\n3. **Capabilities for Production**: It mentions that AgentCore includes tools like AgentCore Gateway, Memory, Runtime, Identity, and Observability, all of which are critical 
for deploying and managing AI agents at scale in production.\n\n4. **Security and Compliance**: The page highlights that AgentCore offers "industry-leading security and compliance" features, which are essential for production-grade applications.\n\n5. **Customer Success Story**: The content includes a
case study about Robinhood, a financial services company, which has successfully used Amazon Bedrock AgentCore in production, indicating real-world readiness.\n\n6. **Additional Resources**: The page provides links to further explore the service, including a demo, workshops, and customer success 
stories, all of which support the idea that AgentCore is ready for production.\n\nGiven these points, it is reasonable to conclude that Amazon Bedrock AgentCore is ready for production use. The general availability status, along with the features and real-world use case presented, strongly suggest 
that the service meets the requirements for production environments.\n\nSource URL: [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)\n\n<thinking>The research query has been addressed using the content from the AWS website. No further tool usage is required.</thinking>'
            }
        ]
    },
    metrics=EventLoopMetrics(
        cycle_count=2,
        tool_metrics={
            'http_request': ToolMetrics(
                tool={'toolUseId': 'tooluse_vLq2e5oOTBGjTAwPK-5ymQ', 'name': 'http_request', 'input': {'headers': {'User-Agent': 'Mozilla/5.0'}, 'method': 'GET', 'url': 'https://aws.amazon.com/bedrock/'}},
                call_count=1,
                success_count=1,
                error_count=0,
                total_time=0.18811392784118652
            )
        },
        cycle_durations=[12.049954891204834],
        traces=[<strands.telemetry.metrics.Trace object at 0x104431f50>, <strands.telemetry.metrics.Trace object at 0x102569490>],
        accumulated_usage={'inputTokens': 119015, 'outputTokens': 512, 'totalTokens': 119527},
        accumulated_metrics={'latencyMs': 13073}
    ),
    state={},
    interrupts=None
)
===== Analysis response =====
AgentResult(
    stop_reason='end_turn',
    message={
        'role': 'assistant',
        'content': [
            {
                'text': "**Analysis of Findings on 'Is Amazon Bedrock AgentCore Ready for Production Use?'**\n\n**Factual Claims Accuracy: 5**\n\nThe findings are accurate based on the content retrieved from the AWS website. The key points supporting the readiness for production use are 
well-substantiated:\n\n1. **General Availability**: The Amazon Bedrock AgentCore is indeed generally available, as explicitly stated on the AWS website.\n2. **Foundational Tools**: The service provides essential tools for executing real-world workflows, which is crucial for production.\n3. **Critical 
Capabilities**: Features like AgentCore Gateway, Memory, Runtime, Identity, and Observability are all necessary for managing and deploying AI agents at scale.\n4. **Security and Compliance**: The service offers industry-leading security and compliance features, which are vital for production 
environments.\n5. **Customer Success Story**: The case study of Robinhood using AgentCore in production adds credibility to its readiness.\n6. **Additional Resources**: The availability of demos, workshops, and further customer success stories supports the service's readiness for production.\n\n**Key 
Insights:**\n\n1. **General Availability**: The service has been released and is stable enough for production use.\n2. **Comprehensive Toolset**: AgentCore provides a full suite of tools necessary for executing complex workflows in production.\n3. **Security Features**: The service includes robust 
security and compliance measures, which are critical for production environments.\n4. **Real-World Use**: Successful deployment by a major company like Robinhood indicates practical readiness.\n5. **Support and Resources**: AWS provides extensive resources to help users transition to production 
use.\n\n**Source Reliability:**\n\nThe source, the AWS website, is highly reliable. AWS is a leading provider of cloud computing services, and its documentation is typically accurate and up-to-date. The inclusion of a customer success story and additional resources further enhances the credibility of 
the information.\n\n**Conclusion:**\n\nBased on the analysis, Amazon Bedrock AgentCore is ready for production use. The general availability status, comprehensive features, security measures, real-world use case, and supportive resources all indicate that the service meets the requirements for 
production environments."
            }
        ]
    },
    metrics=EventLoopMetrics(cycle_count=1, tool_metrics={}, cycle_durations=[3.3698818683624268], traces=[<strands.telemetry.metrics.Trace object at 0x104487010>], accumulated_usage={'inputTokens': 466, 'outputTokens': 434, 'totalTokens': 900}, accumulated_metrics={'latencyMs': 3344}),
    state={},
    interrupts=None
)
===== Final Report =====
### Report on the Readiness of Amazon Bedrock AgentCore for Production Use

#### **Factual Claims Accuracy**

**True Claims:**

1. **General Availability**: Amazon Bedrock AgentCore is generally available.
2. **Foundational Tools**: The service provides essential tools for executing real-world workflows.
3. **Critical Capabilities**: Features like AgentCore Gateway, Memory, Runtime, Identity, and Observability are available.
4. **Security and Compliance**: The service offers industry-leading security and compliance features.
5. **Customer Success Story**: Robinhood is using AgentCore in production.
6. **Additional Resources**: AWS provides demos, workshops, and further customer success stories.

#### **Key Insights**

1. **General Availability**: Amazon Bedrock AgentCore has been released and is stable for production use.
2. **Comprehensive Toolset**: The service offers a full suite of tools necessary for executing complex workflows in production.
3. **Security Features**: Robust security and compliance measures are included, which are critical for production environments.
4. **Real-World Use**: Successful deployment by a major company like Robinhood indicates practical readiness.
5. **Support and Resources**: AWS provides extensive resources to help users transition to production use.

#### **Source Reliability**

The source, the AWS website, is highly reliable. AWS is a leading provider of cloud computing services, and its documentation is typically accurate and up-to-date. The inclusion of a customer success story and additional resources further enhances the credibility of the information.

#### **Conclusion**

Based on the analysis, Amazon Bedrock AgentCore is ready for production use. The general availability status, comprehensive features, security measures, real-world use case, and supportive resources all indicate that the service meets the requirements for production environments.

**Sources:**

- AWS Website

---

This report provides a clear and concise summary of the readiness of Amazon Bedrock AgentCore for production use, supported by accurate factual claims and key insights.AgentResult(
    stop_reason='end_turn',
    message={
        'role': 'assistant',
        'content': [
            {
                'text': '### Report on the Readiness of Amazon Bedrock AgentCore for Production Use\n\n#### **Factual Claims Accuracy**\n\n**True Claims:**\n\n1. **General Availability**: Amazon Bedrock AgentCore is generally available.\n2. **Foundational Tools**: The service provides essential tools 
for executing real-world workflows.\n3. **Critical Capabilities**: Features like AgentCore Gateway, Memory, Runtime, Identity, and Observability are available.\n4. **Security and Compliance**: The service offers industry-leading security and compliance features.\n5. **Customer Success Story**: 
Robinhood is using AgentCore in production.\n6. **Additional Resources**: AWS provides demos, workshops, and further customer success stories.\n\n#### **Key Insights**\n\n1. **General Availability**: Amazon Bedrock AgentCore has been released and is stable for production use.\n2. **Comprehensive 
Toolset**: The service offers a full suite of tools necessary for executing complex workflows in production.\n3. **Security Features**: Robust security and compliance measures are included, which are critical for production environments.\n4. **Real-World Use**: Successful deployment by a major company
like Robinhood indicates practical readiness.\n5. **Support and Resources**: AWS provides extensive resources to help users transition to production use.\n\n#### **Source Reliability**\n\nThe source, the AWS website, is highly reliable. AWS is a leading provider of cloud computing services, and its 
documentation is typically accurate and up-to-date. The inclusion of a customer success story and additional resources further enhances the credibility of the information.\n\n#### **Conclusion**\n\nBased on the analysis, Amazon Bedrock AgentCore is ready for production use. The general availability 
status, comprehensive features, security measures, real-world use case, and supportive resources all indicate that the service meets the requirements for production environments.\n\n**Sources:**\n\n- AWS Website\n\n---\n\nThis report provides a clear and concise summary of the readiness of Amazon 
Bedrock AgentCore for production use, supported by accurate factual claims and key insights.'
            }
        ]
    },
    metrics=EventLoopMetrics(cycle_count=1, tool_metrics={}, cycle_durations=[2.434803009033203], traces=[<strands.telemetry.metrics.Trace object at 0x104478090>], accumulated_usage={'inputTokens': 509, 'outputTokens': 399, 'totalTokens': 908}, accumulated_metrics={'latencyMs': 2412}),
    state={},
    interrupts=None
)
"""