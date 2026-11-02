import json
from pathlib import Path


def test_all_connections_and_subworkflow_ids():
    workflows=[json.loads(p.read_text()) for p in Path("chatbot/workflows").glob("*.json")]
    assert len(workflows)==3
    ids={w["id"] for w in workflows}
    for w in workflows:
        names={n["name"] for n in w["nodes"]}
        for origin,types in w["connections"].items():
            assert origin in names
            for branch in types["main"]:
                for edge in branch: assert edge["node"] in names
        for n in w["nodes"]:
            if n["type"]=="n8n-nodes-base.executeWorkflow":assert n["parameters"]["workflowId"]["value"] in ids
            assert not n.get("credentials")


def test_telegram_dynamic_chat_id():
    w=json.loads(Path("chatbot/workflows/CHATBOT_TELEGRAM.json").read_text())
    send=next(n for n in w["nodes"] if n["name"]=="Telegram Send Message")
    assert send["parameters"]["chatId"].startswith("={{")


def test_business_coherence():
    kb=json.loads(Path("chatbot/conocimiento.json").read_text())
    assert kb["ficticio"]
    assert all(p["precio"]>0 for p in kb["menu"])
    assert len(kb["menu"])>=5
