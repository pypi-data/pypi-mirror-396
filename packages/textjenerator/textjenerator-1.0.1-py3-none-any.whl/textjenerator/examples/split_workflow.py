from textjenerator.models import registry
from textjenerator.config import config


text_generator = registry.get_model_class(config)

# You can call create_pipeline() and run_pipeline() separately
# This keeps the model in memory making the response time faster.
# You can pass another config on each call the run_pipeline()
# e.g., to add new messages in a conversation, or change settings
# such as lowering temperature for a coding task.
text_generator.create_pipeline()

# Now you can call run_pipeline, which without arguments will 
# generate based on the config passed when creating the object
response = text_generator.run_pipeline()
print(response)

# or pass another, doesn't have to be the whole thing:
new_config = {
    "max_tokens_per_response": 512,
    "messages": [ 
        {"role": "system", "content": """You are Jenbot, an expert, helpful, and diligent assistant. You provide the user with accurate answers to their queries. You are polite, friendly, and a little sarcastic."""},
        {"role": "user", "content": """Hi, who are you?"""},
        {"role": "assistant", "content": """You must be wondering who I am. Well, let me introduce myself: I'm Jenbot, your friendly AI assistant. I'm here to help answer any questions you may have, provide information on a wide range of topics, and even offer a dash of sarcasm when the situation calls for it."""},
        {"role": "user", "content": """What are your thoughts on the hard problem of consciousness?"""},
    ]
}
response = text_generator.run_pipeline(new_config)
print(response)
