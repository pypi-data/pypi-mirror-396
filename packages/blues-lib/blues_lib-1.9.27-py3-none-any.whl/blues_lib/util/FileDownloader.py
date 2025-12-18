import os,requests
from blues_lib.util.BluesConsole import BluesConsole
from blues_lib.util.BluesURL import BluesURL
from blues_lib.util.BluesFiler import BluesFiler

class FileDownloader:

  @classmethod
  def download(cls,urls,directory,success=None,error=None):
    '''
    @description Download multi files
    @param {list|str} urls files' remote url
    @param {string} directory : Local directory to save the downloaded files
    @param {function} success : Callback function called on success
    @param {function} error : Callback function called on failure
    @returns {dict} complex result
    '''
    result = cls._get_result()
    if not urls:
      return result 
    
    url_list = urls if type(urls)==list else [urls]
    for url in url_list:
      # download the image
      (code,file_or_msg) = cls.download_one(url,directory)
      if code == 200:
        item = {
          'url':url,
          'file':file_or_msg,
          'callback_value':None
        }
        if success:
          item['callback_value'] = success(file_or_msg)
        result['success']['count']+=1
        result['success']['files'].append(item)
        result['files'].append(file_or_msg)
        result['code'] = 200
      else:
        item = {
          'url':url,
          'message':file_or_msg,
          'callback_value':None
        }
        if error:
          item['callback_value'] = error(str(e))
        result['error']['count']+=1
        result['error']['files'].append(item)
    
    return result 

  @classmethod
  def download_one(cls,url,directory,name:str=''):
    '''
    @description : download one file
    @param {str} url : file's remote url
    @param {str} directory : The dir to save the download file
    @param {str} name : The file name without extension
    '''
    try:
      # Ensure directory existence
      BluesFiler.makedirs(directory)
      # Keep the file name unchanged
      file_name = BluesURL.get_file_name(url,name)
      local_file = os.path.join(directory,file_name)

      # The timeout period must be set, otherwise the request will not stop automatically
      BluesConsole.info('Downloading the file: %s' % url)
      res=requests.get(url,timeout=1)
      res.raise_for_status()
      with open(local_file,'wb') as f:
        f.write(res.content)
        f.close()
        BluesConsole.success(f'Downloaded the file: {url} to {local_file}')
        return (200,local_file) 
    except Exception as e:
      BluesConsole.error(f'Downloaded the image failure: {e}')
      return (500,str(e))

  @classmethod
  def _get_result(cls):
    return {
      'code':500,
      'files':[],
      'success':{
        'count':0,
        'files':[],
      },
      'error':{
        'count':0,
        'files':[],
      },
    }
