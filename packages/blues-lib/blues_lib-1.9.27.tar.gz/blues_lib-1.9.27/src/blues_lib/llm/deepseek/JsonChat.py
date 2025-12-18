import json
from blues_lib.type.output.STDOut import STDOut
from .Chat import Chat

class JsonChat(Chat):

  _RESPONSE_FORMAT={
    'type': 'json_object'
  }

  def _get_output(self,response)->STDOut:
    content:str = response.choices[0].message.content
    data = json.loads(content)
    return STDOut(
      200,
      'success',
      data,
      response.usage,
    )