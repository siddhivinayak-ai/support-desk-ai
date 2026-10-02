import os

# The OpenAI client reads the key when each module is imported; tests never call the API.
os.environ.setdefault("OPENAI_API_KEY", "test-key-not-used")
