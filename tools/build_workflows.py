import json
import uuid
from pathlib import Path

ROOT=Path("chatbot")
CORE="TA4CORE0000000001"
TEST="TA4TEST0000000001"
TELEGRAM="TA4TELE0000000001"


def node(name, kind, params, x, y=0, version=1, **extra):
    return {"id":str(uuid.uuid5(uuid.NAMESPACE_URL,kind+name)),"name":name,"type":"n8n-nodes-base."+kind,
            "typeVersion":version,"position":[x,y],"parameters":params,**extra}


def link(target, index=0):
    return {"node":target,"type":"main","index":index}


def execute(x):
    return node("Ejecutar CORE_CHATBOT","executeWorkflow",{
        "workflowId":{"__rl":True,"value":CORE,"mode":"id"},
        "options":{"waitForSubWorkflow":True}},x,version=1.2)


def write(name, wid, nodes, connections):
    workflow={"id":wid,"name":name,"active":False,"nodes":nodes,"connections":connections,
              "settings":{"executionOrder":"v1","saveDataErrorExecution":"all","saveDataSuccessExecution":"all",
                          "callerPolicy":"workflowsFromSameOwner","executionTimeout":180},
              "pinData":{},"tags":[]}
    (ROOT/"workflows"/(name+".json")).write_text(json.dumps(workflow,ensure_ascii=False,indent=2))


def main():
    knowledge=json.dumps(json.loads((ROOT/"conocimiento.json").read_text()),ensure_ascii=False)
    nodes=[node("Entrada CORE","executeWorkflowTrigger",{"inputSource":"passthrough"},0,version=1.1),
        node("Normalizar mensaje","code",{"jsCode":(ROOT/"normalizar.js").read_text()},220,version=2),
        node("Recuperar conocimiento","code",{"jsCode":(ROOT/"recuperar.js").read_text().replace("__KNOWLEDGE__",knowledge)},440,version=2),
        node("Requiere IA","if",{"conditions":{"options":{"caseSensitive":True,"leftValue":"","typeValidation":"strict","version":2},
             "conditions":[{"id":"use-ai","leftValue":"={{ $json.needs_ai }}","rightValue":True,"operator":{"type":"boolean","operation":"true","singleValue":True}}],"combinator":"and"},"options":{}},660,version=2.2),
        node("Invocar AI Gateway","httpRequest",{"method":"POST","url":"http://ai-gateway:8000/chat","sendBody":True,"specifyBody":"json",
            "jsonBody":"={{ JSON.stringify({message: $json.message, context: $json.context, conversation_id: $json.conversation_id}) }}",
            "options":{"timeout":150000,"response":{"response":{"neverError":True,"responseFormat":"json"}}}},900,-100,version=4.2,onError="continueRegularOutput"),
        node("Validar y cerrar","code",{"jsCode":(ROOT/"validar.js").read_text()},1150,version=2)]
    connections={"Entrada CORE":{"main":[[link("Normalizar mensaje")]]},"Normalizar mensaje":{"main":[[link("Recuperar conocimiento")]]},
        "Recuperar conocimiento":{"main":[[link("Requiere IA")]]},"Requiere IA":{"main":[[link("Invocar AI Gateway")],[link("Validar y cerrar")]]},
        "Invocar AI Gateway":{"main":[[link("Validar y cerrar")]]}}
    write("CORE_CHATBOT",CORE,nodes,connections)
    nodes=[node("Webhook local","webhook",{"httpMethod":"POST","path":"ta4-pruebas","responseMode":"responseNode","options":{}},0,version=2,webhookId="TA4-local-tests"),
        node("Trigger manual","manualTrigger",{},0,220),
        node("Mensaje manual","code",{"jsCode":"return [{json:{message:'¿Cuál es el horario?'}}];"},220,220,version=2),
        execute(440),node("Responder webhook","respondToWebhook",{"respondWith":"json","responseBody":"={{ JSON.stringify($json) }}","options":{}},680,version=1.4)]
    write("PRUEBAS_CHATBOT",TEST,nodes,{"Webhook local":{"main":[[link("Ejecutar CORE_CHATBOT")]]},
        "Trigger manual":{"main":[[link("Mensaje manual")]]},"Mensaje manual":{"main":[[link("Ejecutar CORE_CHATBOT")]]},
        "Ejecutar CORE_CHATBOT":{"main":[[link("Responder webhook")]]}})
    # Sin referencias a credenciales inexistentes: se asignan en la interfaz.
    nodes=[node("Telegram Trigger","telegramTrigger",{"updates":["message"],"additionalFields":{}},0,version=1.2,webhookId="ta4-telegram-85f1ba71-5746-49f0-91ca-8f030cfa258b"),
        node("Validar mensaje Telegram","if",{"conditions":{"options":{"caseSensitive":True,"leftValue":"","typeValidation":"strict","version":2},
            "conditions":[{"id":"text","leftValue":"={{ typeof $json.message?.text === 'string' }}","rightValue":True,"operator":{"type":"boolean","operation":"true","singleValue":True}}],"combinator":"and"},"options":{}},220,version=2.2),
        node("Extraer texto y Chat ID","code",{"jsCode":"const m=$json.message; return [{json:{message:m.text,chat_id:m.chat.id,conversation_id:String(m.chat.id)}}];"},440,version=2),
        execute(660),node("Telegram Send Message","telegram",{"resource":"message","operation":"sendMessage",
            "chatId":"={{ $('Extraer texto y Chat ID').first().json.chat_id }}","text":"={{ $json.response }}","additionalFields":{"appendAttribution":False}},900,version=1.2)]
    write("CHATBOT_TELEGRAM",TELEGRAM,nodes,{"Telegram Trigger":{"main":[[link("Validar mensaje Telegram")]]},
        "Validar mensaje Telegram":{"main":[[link("Extraer texto y Chat ID")],[]]},"Extraer texto y Chat ID":{"main":[[link("Ejecutar CORE_CHATBOT")]]},
        "Ejecutar CORE_CHATBOT":{"main":[[link("Telegram Send Message")]]}})
    print("Tres workflows generados; sin credenciales ni Chat ID fijo.")


if __name__=="__main__":
    main()
