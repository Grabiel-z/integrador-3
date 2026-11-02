import json
import httpx
import pytest
from fastapi.testclient import TestClient
from gateway.app import app, build_request, parse_response, configuration


@pytest.mark.parametrize("provider",["openai","gemini","anthropic"])
def test_external_requires_explicit_credentials(monkeypatch,provider):
    monkeypatch.setenv("LLM_PROVIDER",provider)
    monkeypatch.delenv(provider.upper()+"_API_KEY",raising=False)
    monkeypatch.delenv(provider.upper()+"_MODEL",raising=False)
    with pytest.raises(ValueError,match="Faltan"):configuration()
    assert TestClient(app).post("/chat",json={"message":"Hola","context":"negocio"}).status_code==503


def test_default_local(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER",raising=False)
    assert configuration()[0]=="ollama"


@pytest.mark.parametrize("provider",["ollama","openai","gemini","anthropic"])
def test_official_adapter_contract(provider):
    url,headers,body=build_request(provider,"model-test","dummy-fixture-key","Hola","hechos")
    assert "dummy-fixture-key" not in url
    assert "hechos" in json.dumps(body)
    assert "No inventes" in json.dumps(body,ensure_ascii=False)
    if provider=="ollama":
        assert body["options"]["num_ctx"]==2048
        assert body["think"] is False
    elif provider=="openai":assert url=="https://api.openai.com/v1/responses"
    elif provider=="gemini":assert url.startswith("https://generativelanguage.googleapis.com/")
    else:assert url=="https://api.anthropic.com/v1/messages"


@pytest.mark.parametrize("provider,payload",[
    ("ollama",{"message":{"content":'resultado'},"eval_count":2}),
    ("openai",{"output":[{"type":"reasoning","summary":[]},{"type":"message","content":[{"type":"output_text","text":"resultado"}]}]}),
    ("gemini",{"candidates":[{"content":{"parts":[{"text":"resultado"}]}}]}),
    ("anthropic",{"content":[{"type":"text","text":"resultado"}]})])
def test_response_parsers(provider,payload):
    assert parse_response(provider,payload)[0]=="resultado"


@pytest.mark.parametrize("message",["","a"*1201,123])
def test_request_validation(message):
    assert TestClient(app).post("/chat",json={"message":message,"context":"hechos"}).status_code==422


def test_network_error_is_handled(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER","ollama")
    async def fail(*args,**kwargs):raise httpx.ConnectError("fixture sin red")
    monkeypatch.setattr(httpx.AsyncClient,"post",fail)
    assert TestClient(app).post("/chat",json={"message":"Hola","context":"hechos"}).status_code==502


def test_timeout_is_handled(monkeypatch):
    async def fail(*args,**kwargs):raise httpx.ReadTimeout("fixture timeout")
    monkeypatch.setattr(httpx.AsyncClient,"post",fail)
    assert TestClient(app).post("/chat",json={"message":"Hola","context":"hechos"}).status_code==504
