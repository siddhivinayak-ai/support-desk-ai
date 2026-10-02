import json
from types import SimpleNamespace
from unittest import mock

from desk import search, summarize, triage, visuals


def _chat_reply(text):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])


def test_summary_uses_the_pinned_model_and_system_prompt():
    with mock.patch.object(summarize, "client") as client:
        client.chat.completions.create.return_value = _chat_reply("- broken login")
        assert summarize.summarize_ticket("Login", "Can't sign in") == "- broken login"
        kwargs = client.chat.completions.create.call_args.kwargs
        assert kwargs["model"] == summarize.SUMMARY_MODEL
        assert kwargs["messages"][0]["content"] == summarize.SYSTEM_PROMPT


def test_triage_falls_back_to_normal_for_unknown_labels():
    with mock.patch.object(triage, "client") as client:
        client.chat.completions.create.return_value = _chat_reply(json.dumps({"urgency": "urgent"}))
        assert triage.classify_urgency("Down", "Site is down") == "urgent"
        client.chat.completions.create.return_value = _chat_reply(json.dumps({"urgency": "meh"}))
        assert triage.classify_urgency("Hi", "Question") == "normal"


def test_embeddings_keep_input_order():
    with mock.patch.object(search, "client") as client:
        client.embeddings.create.return_value = SimpleNamespace(
            data=[SimpleNamespace(embedding=[0.1]), SimpleNamespace(embedding=[0.2])]
        )
        assert search.embed(["a", "b"]) == [[0.1], [0.2]]


def test_illustration_returns_base64():
    with mock.patch.object(visuals, "client") as client:
        client.images.generate.return_value = SimpleNamespace(data=[SimpleNamespace(b64_json="aGk=")])
        assert visuals.illustrate_article("Resetting your password") == "aGk="
