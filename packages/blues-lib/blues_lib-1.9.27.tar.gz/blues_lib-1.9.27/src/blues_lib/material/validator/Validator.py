import math
from blues_lib.material.MatHandler import MatHandler
from blues_lib.type.output.STDOut import STDOut

class Validator(MatHandler):

  def _calculate(self)->STDOut:
    valid_entities = []
    invalid_entities = []

    for entity in self._entities:
      entity['mat_stat'] = 'available'
      has_image,error = self._has_image(entity)
      if not has_image:
        entity['mat_stat'] = 'invalid'
        entity['mat_remark'] = error
        invalid_entities.append(entity)
        continue

      if not self._rule:
        valid_entities.append(entity)
        continue

      is_valid,error = self._is_valid_entity(entity)
      if is_valid:
        entity['mat_stat'] = 'available'
        valid_entities.append(entity)
        continue

      entity['mat_stat'] = 'invalid'
      entity['mat_remark'] = error
      invalid_entities.append(entity)

    # insert invalid entities to db
    self._insert_trash(invalid_entities)

    message:str = f"valid {len(valid_entities)} ; invalid {len(invalid_entities)}" 
    return STDOut(200,message,valid_entities,invalid_entities)
  
  def _has_image(self,entity:dict)->tuple[bool,str]:
    paras:list[dict] = entity.get('mat_paras',[])
    if not paras:
      return (True,'not detail entity')

    for para in paras:
      if para.get('type') == 'image':
        return (True,'ok')
    return (False,'no image')
  
  def _is_valid_entity(self,entity:dict)->tuple[bool,str]:
    required_fields:dict = self._rule.get('required',{})
    for field,rule in required_fields.items():
      if field not in entity:
        return (False,f"{field} is missing")

      # 如果是字典才有更多配置
      if not rule or not isinstance(rule,dict):
        continue
      
      # 只有有属性才是必填，值为对象进一步添加规则
      field_value:any = entity.get(field)

      min_length = rule.get('min_length')
      max_length = rule.get('max_length')
      field_len:int = self._get_field_length(field,field_value)

      if min_length and field_len<min_length:
        return (False,f"{field} is too short : {field_len}, at least {min_length}")

      if max_length and field_len>max_length:
        return (False,f"{field} is too long : {field_len}, at most {max_length}")

    return (True,'ok')
  
  def _get_len(self, text: str) -> int:
    """
    计算字符串长度，中文按长度1计算；英文和符号按0.5计算，结果向上取整
    """
    length = 0
    for char in text:
      # 判断是否为中文字符
      if '\u4e00' <= char <= '\u9fff':
        length += 1
      else:
        length += 0.5
    # 向上取整，确保返回整数
    return math.ceil(length)

  def _get_field_length(self,field:str,field_value:any)->int:

    if field == 'mat_paras':
      size = 0
      paras:list[str] = field_value
      for para in paras:
        p_type = para.get('type')
        p_value = para.get('value')  or '' # must be a str
        if p_type == 'text':
          size += self._get_len(p_value)
      return size
    
    return self._get_len(str(field_value))
    
    



     