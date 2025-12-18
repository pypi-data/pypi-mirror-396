import os
import json,csv
from blues_lib.util.BluesFiler import BluesFiler

class FileWriter:

  @classmethod
  def write(cls,file_path,text,mode='w')->str:
    '''
    @description : write text to file
    @param {str} file_path : file's path
    @param {str} text : content
    @param {str} mode : write mode
      - 'w' : clear the history content
      - 'a' : append text
    @returns {str} : the writed file path
    '''
    dir_path = os.path.dirname(file_path)
    if dir_path!='.':
      BluesFiler.makedirs(dir_path)

    try:
      with open(file_path,mode,encoding='utf-8') as file:
        file.write(text)
      return file_path
    except Exception as e:
      print(f'==>write error: {e}')
      return ''

  @classmethod
  def write_after(cls,file_path,text)->str:
    return cls.write(file_path,text,'a')

  @classmethod
  def write_json(cls,file_path,data,indent=2)->str:
    dir_path = os.path.dirname(file_path)
    if dir_path!='.':
      BluesFiler.makedirs(dir_path)

    try:
      with open(file_path, 'w', encoding='utf-8') as file:
        # must set ensure_ascii as False for Chinese character
        json.dump(data,file,indent=indent,ensure_ascii=False)
        return file_path
    except Exception as e:
      print(f'==>write_json error: {e}')
      return ''

  @classmethod
  def write_csv(cls,file_path,rows,header=None,mode='w')->str:
    '''
    @description : write to csv file
    @param {str} file_path : the csv file's path
    @param {list<list>|tuple<tuple>} rows : the data rows
    @param {list|tuple} header
    @param {str} mode : 'a' - append ; 'w' - cover
    '''
    dir_path = os.path.dirname(file_path)
    if dir_path!='.':
      BluesFiler.makedirs(dir_path)

    try:
      with open(file_path, mode, encoding='utf-8',newline="") as file:
        writer = csv.writer(file) 
        if mode=='w' and header:
          writer.writerow(header)
        if rows:
          for row in rows:
            writer.writerow(row)
        return file_path
    except Exception as e:
      print(f'==>write_csv error: {e}')
      return ''
