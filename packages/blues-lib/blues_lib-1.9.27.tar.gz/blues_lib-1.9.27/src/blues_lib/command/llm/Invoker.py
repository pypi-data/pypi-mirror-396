from blues_lib.llm.deepseek.JsonChat import JsonChat    
from blues_lib.llm.deepseek.ChatMessages import ChatMessages
from blues_lib.type.output.STDOut import STDOut
from blues_lib.model.Model import Model

class Invoker():

  @classmethod
  def invoke(cls,model:Model)->STDOut:
    
    prompt:dict = model.config.get('prompt') or {}
    request:dict = model.config.get('request') or {}
    messages = ChatMessages(prompt).create()
    body:dict|None = request.get("body")
    return JsonChat(body).ask(messages)