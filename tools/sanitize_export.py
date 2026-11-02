import json
from pathlib import Path

target=Path("chatbot/exportados");target.mkdir(exist_ok=True)
for path in Path("evidencias/privadas").glob("TA4*.json"):
    data=json.loads(path.read_text())
    workflows=data if isinstance(data,list) else [data]
    for workflow in workflows:
        for node in workflow.get("nodes",[]):node.pop("credentials",None)
        workflow.pop("pinData",None)
        workflow.pop("staticData",None)
        workflow["active"]=False
    clean=[{key:w[key] for key in ('id','name','nodes','connections','settings','active') if key in w} for w in workflows]
    (target/path.name).write_text(json.dumps(clean,ensure_ascii=False,indent=2))
