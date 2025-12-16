import pytest
from cloudflare_ai_python import CloudflareAI, call_cloudflare_ai

def test_cloudflare_ai_init():
    """Test CloudflareAI initialization"""
    client = CloudflareAI("test_account", "test_token")
    assert client.account_id == "test_account"
    assert client.api_token == "test_token"
    assert client.base_url == "https://api.cloudflare.com/client/v4/accounts/test_account/ai"

def test_list_models():
    """Test list_models returns expected structure"""
    client = CloudflareAI("test_account", "test_token")
    models = client.list_models()
    assert "result" in models
    assert "success" in models
    assert isinstance(models["result"], list)
    assert len(models["result"]) > 0

def test_backward_compatibility():
    """Test backward compatibility function exists"""
    # This just tests that the function can be imported and called
    # In real tests, you'd mock the HTTP requests
    assert callable(call_cloudflare_ai)