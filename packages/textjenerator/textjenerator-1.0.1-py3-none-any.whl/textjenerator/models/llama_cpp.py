from llama_cpp import Llama

from textjenerator.models.registry import register_model
from textjenerator.core.text_generator import TextGenerator


@register_model("llama-cpp")
class LlamaCPP(TextGenerator):
    """
    Concrete implementation of TextGenerator using the llama-cpp-python library
    for running GGUF-formatted LLMs (e.g., Llama 3, Mistral) efficiently on CPU.

    It implements the core abstract methods:
    1. create_pipeline: Initializes the llama_cpp.Llama object.
    2. run_pipeline: Executes text generation via the create_chat_completion API.
    """

    def __init__(self, config):
        """
        Initializes the text generator.

        Args:
            config (dict): Configuration dictionary. Must include standard TextGenerator
                           keys plus model-specific keys.
            llm (llama_cpp.Llama | None): The initialized Llama CPP model object.
        """
        super().__init__(config)
        self.llm = None


    def create_pipeline(self):
        """
        Loads the pipeline using llama_cpp.Llama and applies configurations.

        Note that llama-cpp-python handles its own hardware acceleration, so the device
        config (cpu/CUDA) in the parent class is not used here.

        Requires the following keys in self.config:
        * model_path (str): Path to the GGUF model file.
        * max_context_size (int): The context window size (n_ctx).
        * number_of_threads (int): The number of threads to use (n_threads).
        * verbose_warnings (bool): Enable/disable verbose warnings.
        * n_gpu_layers (int): Number of layers to offload to the GPU (optional, defaults to 0).

        Raises:
            KeyError: If specific config keys (like model_path) are missing.
        """
        self.llm = Llama(
            model_path=self.config["model_path"],
            n_ctx=self.config["max_context_size"],
            n_threads=self.config["number_of_threads"],
            verbose=self.config["verbose_warnings"],
            n_gpu_layers=self.config["n_gpu_layers"]
        )


    def run_pipeline(self, config=None):
        """
        Executes the inference using the chat completion API.

        Args:
       config (dict | None): A dictionary containing temporary overrides for
                            this specific inference call (e.g., the next message). 
                            These settings are merged with and override the permanent 
                            self.config for this run only. If None, self.config is used directly.

        Requires the following keys in onfig:
        * messages (list): The chat history in the expected Llama format.
        * max_tokens_per_response (int): Max new tokens to generate.
        * temperature (float): Sampling temperature.
        * top_p (float): Top-p sampling value.
        * top_k (int): Top-k sampling value.
        
        The final generated text is stored in self.response and returned.
        """
        if config:
            config = self.merge_config(config)
        else:
            config = self.config

        output = self.llm.create_chat_completion(
            messages=config["messages"],
            max_tokens=config["max_tokens_per_response"],
            temperature=config["temperature"],
            top_p=config["top_p"],
            top_k=config["top_k"],
        )
        choice = output["choices"][0]["message"]
        output_text = (choice.get("content") or "").strip()
        if not output_text:
            output_text = "[No response generated.]"
        self.response = output_text

        return self.response

