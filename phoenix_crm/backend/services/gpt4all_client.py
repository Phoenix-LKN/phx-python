from gpt4all import GPT4All
import os
from functools import lru_cache

@lru_cache()
def get_gpt4all_client():
    model_path = os.getenv("GPT4ALL_MODEL_PATH", "/models/gpt4all-model.bin")
    
    try:
        model = GPT4All(model_path)
        return model
    except Exception as e:
        # Fallback to downloading a model if path doesn't exist
        print(f"Could not load model from {model_path}, downloading default model...")
        model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")
        return model
