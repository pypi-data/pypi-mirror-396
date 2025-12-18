import json

from blues_lib.type.output.SQLSTDOut import SQLSTDOut
from blues_lib.dao.sql.BluesSQLIO import BluesSQLIO

class TableMutator():

  _SQL_IO = None

  def __init__(self,table:str,should_encode:bool=True)->None:
    self._table = table
    self._should_encode = should_encode

  @property
  def _io(self)->BluesSQLIO:
    if not self._SQL_IO:
      self._SQL_IO = BluesSQLIO()
    return self._SQL_IO
  
  def post(self,fields:list[str],values:list[list[any]])->SQLSTDOut:
    '''
    Insert one more multi rows
    Parameter:
      fields {list<str>} : the table fields 
      values {list<list<str>>} : two-dim list, every list is a row field value
        the fields' length must be equal to the values row list's length
    Return:
      {dict} : the standard sql output,like:
         {'code': 200, 'count': 1, 'sql': 'insert xxx'}
    '''
    self._encode_entities(values)
    return self._io.post(self._table,fields,values)
  
  def insert(self,entities:list[dict])->SQLSTDOut:
    '''
    Insert one more multi rows
    Parameter:
      entities {dict | list<dict>} : every dict contains field:value
    Return:
      {dict} : the standard sql output,like:
         {'code': 200, 'count': 1, 'sql': 'insert xxx'}
    '''
    self._encode_entities(entities)
    return self._io.insert(self._table,entities)

  def put(self,fields:list[str],values:list[any],conditions:dict|list[dict])->SQLSTDOut:
    '''
    Update one or multi rows
    Parameter:
      fields {list<str>} : the table fields 
      values {list<any>} : the updated value
        the value's list length should be equal to the field's list length
      conditions {dict | list<dict>} : the standard condition value ,like:
        {'field':'material_id','comparator':'=','value':'id2'} 
        [{'field':'material_id','comparator':'=','value':'id2'}]
    Return:
      {dict} : the standard sql output,like:
         {'code': 200, 'count': 1, 'sql': 'update xxx'}
    '''
    self._encode_entity(values)
    return self._io.put(self._table,fields,values,conditions)

  def update(self,entity:dict,conditions:dict|list[dict])->SQLSTDOut:
    '''
    Update one or multi rows
    Parameter:
      entity {dict} : every dict contains field:value
      conditions {dict | list<dict>} : the standard condition value ,like:
        {'field':'material_id','comparator':'=','value':'id2'} 
        [{'field':'material_id','comparator':'=','value':'id2'}]
    Return:
      {dict} : the standard sql output,like:
         {'code': 200, 'count': 1, 'sql': 'update xxx'}
    '''
    self._encode_entity(entity)
    return self._io.update(self._table,entity,conditions)

  def delete(self,conditions:dict|list[dict])->SQLSTDOut:
    '''
    Delete one or multi rows
    Parameter:
      conditions {dict | list<dict>} : the standard condition value ,like:
        {'field':'material_id','comparator':'=','value':'id2'} 
        [{'field':'material_id','comparator':'=','value':'id2'}]
    Return:
      {dict} : the standard sql output,like:
         {'code': 200, 'count': 1, 'sql': 'delete xxx'}
    '''
    return self._io.delete(self._table,conditions)
  
  def _encode_entities(self,entities:list[any])->None:
    if self._should_encode and isinstance(entities,list):
      for entity in entities:
        self._encode_entity(entity)

  def _encode_entity(self,entity:dict|list[any])->None:
    if self._should_encode:
      self._encode(entity)

  def _encode(self, entity: dict|list[any]) -> None:
    """
    Encodes non-MySQL-native types in a dictionary or list to JSON strings (single level).
    Ignores inputs that are not dictionaries or lists.
    
    Args:
        entity: A dictionary or list representing data to be written to the database.
    
    Returns:
        The encoded entity (modified in-place for dictionaries, new list for lists),
        or the original input if it's not a dictionary or list.
    """
    mysql_types = {int, float, str, bool, type(None)}
    
    if isinstance(entity, dict):
      for key, value in entity.items():
        if type(value) in mysql_types:
          continue

        try:
          entity[key] = json.dumps(value, ensure_ascii=False)
        except json.JSONDecodeError as e:
          entity[key] = str(e)

    if isinstance(entity, list):
      for index,item in enumerate(entity):
        if type(item) in mysql_types:
          continue

        try:
          entity[index] = json.dumps(item, ensure_ascii=False)
        except json.JSONDecodeError as e:
          entity[index] = str(e)
