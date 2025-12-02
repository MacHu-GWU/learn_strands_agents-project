# -*- coding: utf-8 -*-

from boto_session_manager import BotoSesManager
import strands

bsm = BotoSesManager(profile_name="esc_app_dev_us_east_1")
# model_id="us.amazon.nova-pro-v1:0"
# model_id="us.amazon.nova-lite-v1:0"
model_id = "us.amazon.nova-micro-v1:0"


# Create an agent with default settings
agent = strands.Agent(
    model=strands.models.BedrockModel(
        boto_session=bsm.boto_ses,
        model_id=model_id,
    ),
)

# Ask the agent a question
print("\n===== 1 =====")
agent("Memorize that my name is Julek Vatslav.")
# Ask the agent again to see if it remembers. NO, it doesn't!
print("\n===== 2 =====")
agent("Now tell me what is my name?")
