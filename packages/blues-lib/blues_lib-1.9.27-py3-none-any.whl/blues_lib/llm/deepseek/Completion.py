import os,time,logging
from abc import ABC,abstractmethod
from openai import OpenAI
from blues_lib.type.output.STDOut import STDOut

class Completion(ABC):
  _BASE_URL = "https://api.deepseek.com"
  _API_KEY_ENV_NAME = 'DEEPSEEK_API_KEY'

  _MODEL_NAME = 'deepseek-chat'
  _TEMPERATURE = 1
  _STREAM = False
  _RESPONSE_FORMAT={
    'type': 'text'
  }
  
  def __init__(self,request_body:dict|None=None, api_key: str = '') -> None:
    self._request_body = request_body or {}
    self._api_key = api_key
    self._logger = logging.getLogger('airflow.task')

  def ask(self,messages:list[dict[str,str]])->STDOut:
    kwargs = self._get_kwargs(messages)
    try:
      client = self._get_client()
      self._console(messages)

      request_start = time.time()
      response = client.chat.completions.create(**kwargs)

      request_end = time.time()
      self._logger.info(f"API处理时间: {request_end - request_start:.2f}秒")

      stdout:STDOut = self._get_content(response)
      self._logger.info(f"llm output: {stdout}")
      return stdout
    except Exception as e:
      return self._get_error(e)
  
  def _get_kwargs(self,messages:list[dict[str,str]]):
    kwargs = {
      'stream':self._STREAM,
      'temperature':self._TEMPERATURE,
      'model':self._MODEL_NAME,
      'response_format':self._RESPONSE_FORMAT,
    }
    kwargs.update(self._request_body)
    # messages动态输入
    kwargs['messages'] = messages
    return kwargs
  
  def _console(self,messages:list[dict[str,str]]):
    system_prompt = messages[0]['content']
    user_prompt_len = len(messages[1]['content'])
    self._logger.info(f'llm prompt : {system_prompt.strip()[:50]}...({user_prompt_len} chars)')
    
  def _get_client(self):
    return OpenAI(
      # 优先使用客户端传入，再次使用环境变量
      api_key= self._api_key or os.environ.get(self._API_KEY_ENV_NAME,''),
      base_url=self._BASE_URL,
      timeout=120,  # 长文本处理需要更长时间
      max_retries=3,  # 添加重试机制
    )

  def _get_error(self,error)->STDOut:
    common_err:dict = {
      "code":"common_error",
      "type":"internal_error",
      "message":str(error)
    }

    std_err:dict|None = None 
    # 异常为OpenAIError对象，需要解析为字典使用
    if hasattr(error,'response'):
      response:dict = error.response.json()
      # 避免内部结构变动异常
      std_err = response.get('error')

    std_err = std_err or common_err
    return STDOut(
      500,
      f"{std_err.get('code')} - {std_err.get('type')} - {std_err.get('message')}",
    )

  @abstractmethod
  def _get_content(self,response)->STDOut:
    pass