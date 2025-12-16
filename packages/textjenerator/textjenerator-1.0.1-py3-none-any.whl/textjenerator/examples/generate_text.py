from textjenerator.models import registry
from textjenerator.config import config

text_generator = registry.get_model_class(config)
response = text_generator.generate_text()
print(response)

