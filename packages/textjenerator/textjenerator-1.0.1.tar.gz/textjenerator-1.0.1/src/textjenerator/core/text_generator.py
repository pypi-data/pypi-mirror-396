import copy

from abc import ABC, abstractmethod
import torch

from textjenerator.config import config


class TextGenerator(ABC):
    """
    Abstract base class for text generation. This class handles the generic configuration and execution flow and manages device (CPU/CUDA) /data type (e.g., bfloat16) setup.
    
    Subclasses must implement create_pipeline() and run_pipeline()

    Attributes:
        config (dict): Configuration dictionary containing model parameters, paths, and settings. 
        DTYPES_MAP (dict): A mapping from string names (e.g., "bfloat16") to torch.dtype objects.
        Add: pipe (Any): The initialized model pipeline (to be set by subclasses).
        Add: response (str/Any): The generated text or model output (to be set by subclasses).
    """

    def __init__(self, config = config):
        """
        Initializes the object with a config.

        Args:
            config (dict): A dictionary containing configuration parameters. Default config comes from textjenerator.config
        """
        self.config = config
        self.pipe = None
        self.response = None
        self.dtype = None
        self.device = None
        self.DTYPES_MAP = {
            "bfloat16": torch.bfloat16,
            "float16": torch.float16,
            "float32": torch.float32,
        }
        self.detect_device_and_dtype()


    def detect_device_and_dtype(self):
        """
        If 'device' or 'dtype' in config are set to "detect", this method attempts
        to choose the optimal settings based on hardware availability (e.g., CUDA).
        This method modifies self.device and self.dtype based on hardware availability and configuration settings.
        """
        if self.config["device"] == "detect":
            self.set_device()
        else:
            self.device = self.config["device"]

        self.set_dtype()
        

    def set_device(self):
        """
        Sets the computation device based on CUDA availability.

        Sets `self.device` to 'cuda' if available, otherwise defaults to 'cpu'.
        """
        if torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"


    def set_dtype(self):
        """
        Sets the torch data type based on the device and configuration.

        If config['dtype'] is "detect":
            - Sets to torch.bfloat16 if device is 'cuda'.
            - Sets to torch.float32 otherwise.
        Otherwise, maps the string config to the actual torch.dtype object in self.DTYPES_MAP.
        """
        if self.config["dtype"] == "detect":
            if self.device == "cuda":
                self.dtype = torch.bfloat16
                self.config["dtype"] = "bfloat16"
            else:
                self.dtype = torch.float32
                self.config["dtype"] = "float32"
            return
        
        self.dtype = self.DTYPES_MAP[self.config["dtype"]]


    def merge_config(self, config):
        merged_config = merged_config = copy.deepcopy(self.config)
        merged_config.update(config)

        return merged_config


    @abstractmethod
    def create_pipeline(self):
        """
        Abstract method to initialize the model pipeline.
        
        Subclasses must implement this to load the specific model and tokenizer/pipeline object, assigning it to self.pipe (e.g., a Hugging Face Pipeline object).
        """
        pass


    @abstractmethod
    def run_pipeline(self):
        """
        Abstract method to execute the model pipeline.

        Subclasses must implement this to execute the model using self.pipe and store the final generated text in self.response (str).
        """
        pass
    

    def generate_text(self):
        """
        Generates text by orchestrating the pipeline creation and execution. This is the primary public method for text generation.

        Steps:
            1. Creates the pipeline.
            2. Runs the pipeline implementation.

        Returns: str: The generated text, which is the value of self.response after the pipeline runs.
        """
        self.create_pipeline()
        self.run_pipeline()
        return self.response

