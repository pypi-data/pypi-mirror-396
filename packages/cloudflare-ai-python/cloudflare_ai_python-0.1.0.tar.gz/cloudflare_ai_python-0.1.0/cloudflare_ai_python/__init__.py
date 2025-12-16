import requests

# Static list of available models based on Cloudflare documentation
AVAILABLE_MODELS = [
    {
        "name": "@cf/meta/llama-3.1-8b-instruct",
        "description": (
            "The Meta Llama 3.1 collection of multilingual large language models "
            "(LLMs) is a collection of pretrained and instruction tuned generative "
            "models. The Llama 3.1 instruction tuned text only models are optimized "
            "for multilingual dialogue use cases and outperform many of the available "
            "open source and closed chat models on common industry benchmarks."
        ),
        "task": "Text Generation",
        "provider": "Meta"
    },
    {
        "name": "@cf/meta/llama-3.1-70b-instruct",
        "description": (
            "The Meta Llama 3.1 collection of multilingual large language models "
            "(LLMs) is a collection of pretrained and instruction tuned generative "
            "models. The Llama 3.1 instruction tuned text only models are optimized "
            "for multilingual dialogue use cases and outperform many of the available "
            "open source and closed chat models on common industry benchmarks."
        ),
        "task": "Text Generation",
        "provider": "Meta"
    },
    {
        "name": "@cf/openai/whisper-large-v3-turbo",
        "description": (
            "Whisper is a pre-trained model for automatic speech recognition "
            "(ASR) and speech translation."
        ),
        "task": "Automatic Speech Recognition",
        "provider": "OpenAI"
    },
    {
        "name": "@cf/blackforestlabs/flux-1-schnell",
        "description": (
            "FLUX.1 [schnell] is a 12 billion parameter rectified flow transformer "
            "capable of generating images from text descriptions."
        ),
        "task": "Text-to-Image",
        "provider": "Black Forest Labs"
    },
    {
        "name": "@cf/deepgram/nova-3",
        "description": "Transcribe audio using Deepgram's speech-to-text model",
        "task": "Automatic Speech Recognition",
        "provider": "Deepgram"
    },
    # Add more models as needed from the documentation
]


class CloudflareAI:
    """
    A client for interacting with Cloudflare Workers AI.
    """

    def __init__(self, account_id, api_token):
        """
        Initialize the Cloudflare AI client.

        :param account_id: Your Cloudflare Account ID
        :param api_token: Your Cloudflare API Token
        """
        self.account_id = account_id
        self.api_token = api_token
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai"

    def list_models(self):
        """
        Retrieve the list of available models.

        :return: A dictionary with 'result' key containing the list of model dictionaries
        """
        # Since there's no public API to list models dynamically, return static list
        return {"result": AVAILABLE_MODELS, "success": True}

    def run_model(self, model, prompt, **kwargs):
        """
        Run a model with the given prompt and additional parameters.

        :param model: The model identifier, e.g., '@cf/meta/llama-3.1-8b-instruct'
        :param prompt: The prompt to send to the model
        :param kwargs: Additional parameters for the model (e.g., max_tokens, temperature)
        :return: The JSON response from the API
        """
        url = f"{self.base_url}/run/{model}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        data = {"prompt": prompt}
        data.update(kwargs)
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()


# For backward compatibility, keep the old function
def call_cloudflare_ai(account_id, api_token, model, prompt):
    """
    Call Cloudflare Worker AI model with the given parameters.

    :param account_id: Your Cloudflare Account ID
    :param api_token: Your Cloudflare API Token
    :param model: The model identifier, e.g., '@cf/meta/llama-3.1-8b-instruct'
    :param prompt: The prompt to send to the model
    :return: The JSON response from the API
    """
    client = CloudflareAI(account_id, api_token)
    return client.run_model(model, prompt)
