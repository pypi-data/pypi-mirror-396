"""
Implements a simple decorator-based model registry for dynamically managing
different model classes.

This system allows concrete subclasses to register themselves
using a specific string key, enabling the application to instantiate the 
correct class based on a configuration setting without explicit imports.
"""

MODEL_REGISTRY = {}

def register_model(name):
    """
    A decorator factory used to register a subclass.

    The decorated class is stored in the global MODEL_REGISTRY dictionary
    under the provided `name`.

    Args:
        name (str): The string key used to reference the model class
                    in the configuration.

    Returns:
        Callable: A decorator function that takes a class and registers it.
    """
    def decorator(cls):
        MODEL_REGISTRY[name] = cls
        return cls
    return decorator


def get_model_class(config):
    """
    Retrieves and instantiates the correct class based on the
    configuration dictionary.

    It looks up the class in MODEL_REGISTRY using the key found in
    `config['model']`.

    Args:
        config (dict): The configuration dictionary, which must contain a
                       'model' key corresponding to a registered model name.

    Returns:
        BaseClass: An instantiated object of the registered generator class.

    Raises:
        KeyError: If the value of `config['model']` is not found in the
                  MODEL_REGISTRY.
    """
    ModelClass = MODEL_REGISTRY[config["model"]]
    model_object = ModelClass(config)

    return model_object