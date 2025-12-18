from typing import Any
import json,csv,yaml,json5
from blues_lib.hocon.HoconReader import HoconReader

class FileReader:

  @classmethod
  def read(cls,file_path:str)->str:
    try:
      with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
    except Exception as e:
      print(f"read file error: {e}")
      return ''

  @classmethod
  def read_text(cls,file_path:str)->str:
    return cls.read(file_path)

  @classmethod
  def read_yaml(cls,file_path:str)->Any|None:
    try:
      with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)
    except Exception as e:
      print(f"read yaml error: {e}")
      return None

  @classmethod
  def read_json5(cls,file_path:str)->Any|None:
    try:
      with open(file_path, 'r', encoding='utf-8') as file:
        data = json5.load(file)
        return data
    except Exception as e:
      print(f"read json5 error: {e}")
      return None

  @classmethod
  def read_json(cls,file_path:str)->Any|None:
    try:
      with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data
    except Exception as e:
      print(f"read json error: {e}")
      return None

  @classmethod
  def read_csv(cls,file_path:str,headless=False)->list[list[str]]|None:
    '''
    @description : read csv file
    @param {str} file_path
    @returns {list<list>}
    '''
    try:
      with open(file_path, 'r', encoding='utf-8',errors='ignore') as file:
        lines = csv.reader(file) 
        rows = []
        i=0
        for line in lines:
          i+=1
          if i==1 and headless:
            continue
          if not line:
            continue
          rows.append(line)
        return rows
    except Exception as e:
      print(f"read csv error: {e}")
      return None

  @classmethod
  def read_hocon(cls,file_path:str)->dict:
    '''
    @description: read conf file 
    @param {str} file path such as 'c:/blues-lib-py/tests/mock/command/llm-loop-urls/def.conf'
    @returns {any|None}
    '''
    return HoconReader.read_as_dict(file_path)
