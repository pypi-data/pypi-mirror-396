
class ChatMessages:
  
  def __init__(self,prompt_def:dict) -> None:
    self._user_def:dict = prompt_def.get('user') or {}
    self._system_def:dict = prompt_def.get('system') or {}
    self._max_chars:int = int(prompt_def.get('max_chars') or 4000)
  
  def _get_system_message(self)->list[dict[str,str]]:
    system_content:str = self._system_def.get('content')
    if not system_content:
      return []

    return [
      {
        "role": "system",
        "content": system_content,
      }
    ]
  
  def _get_user_message(self) -> list[dict[str,str]]:
    user_content:str = self._user_def.get('content') or ''
    user_prefix:str = self._user_def.get('prefix') or ''
    user_suffix:str = self._user_def.get('suffix') or ''

    if not user_content:
      raise ValueError(f'{self.__class__.__name__} : no user_content')

    if len(user_content) > self._max_chars:
      user_content = user_content[:self._max_chars]

    content:str = f"{user_prefix}{user_content}{user_suffix}"

    return [
      {
        "role": "user",
        "content": content,
      }
    ]
  
  def create(self) -> list[dict[str,str]]:
    system_message:list[dict[str,str]] = self._get_system_message()
    user_message:list[dict[str,str]] = self._get_user_message()
    return system_message + user_message
  