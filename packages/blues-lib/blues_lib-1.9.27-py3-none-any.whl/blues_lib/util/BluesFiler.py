import os,base64
from datetime import datetime,timedelta
from blues_lib.util.OSystem import OSystem

class BluesFiler:
  
  @classmethod
  def get_lib_path(cls):
    # 此目录 用来存放此库生成的文件
    root_dir = "blues_lib"
    os_type = OSystem.get_os_type()
    if os_type == 'windows':
      return os.path.join("c:\\",root_dir)
    elif os_type == 'linux':
      return os.path.join('/usr/share',root_dir)
    elif os_type == 'mac':
      return os.path.join('/Users/Shared',root_dir)
    else:
      return ''

  @classmethod
  def get_cft_path(cls):
    # 此目录 存放chrome cft资源
    root_path = BluesFiler.get_lib_path()
    root_dir = 'cft'
    return os.path.join(root_path,root_dir)

  @classmethod
  def get_app_path(cls,project_root_dir:str='')->str:
    # 执行py文件的绝对路径
    cur_path = os.path.realpath(__file__)
    root_dir = project_root_dir
    return os.path.join(cur_path.split(root_dir)[0],root_dir)
  
  @classmethod
  def get_abs_path(cls,project_root_dir:str,path:str)->str:
    root_path = cls.get_app_path(project_root_dir)
    return os.path.join(root_path,path)

  @classmethod
  def readfiles(cls,directory):
    '''
    Read the file list in a dir, don't support the next dirs
    @param {string} directory 
    '''
    file_list = []
    for root, dirs, files in os.walk(directory):
      for file in files:
        file_list.append(os.path.join(root, file))
    return file_list

  @classmethod
  def removedirs(cls,directory,retention_days=0):
    '''
    @description Remove all child dir and files
    @param {string} directory 
    '''
    threshold = datetime.now() - timedelta(days=retention_days)
    removed_count = 0
    if not cls.exists(directory):
      return removed_count

    for root, dirs, files in os.walk(directory):
      for file in files:
        file_path = os.path.join(root, file)
        file_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        if file_modified_time < threshold:
          os.remove(file_path)
          removed_count +=1
      for dire in dirs:
        dir_path = os.path.join(root, dire)
        file_modified_time = datetime.fromtimestamp(os.path.getmtime(dir_path))
        if file_modified_time < threshold:
          # recursion to remove the dir
          removed_count += cls.removedirs(dir_path,retention_days)
    # remove the base dir
    if cls.is_dir_empty(directory):
      os.rmdir(directory)
      removed_count +=1
    return removed_count

  @classmethod
  def is_dir_empty(cls,dir_path):
    return not bool(os.listdir(dir_path))

  @classmethod
  def exists(cls,path):
    '''
    @description : Does a dir or file exist
    @param {str} path
    @returns {bool} 
    '''
    return os.path.exists(path)

  @classmethod
  def filter_exists(cls,files):
    exists_files = []
    for file in files:
      if not cls.exists(file):
        continue
      exists_files.append(file)
    return exists_files

  @classmethod
  def makedirs(cls,path):
    '''
    @description : Create dirs (support multilevel directory) if they don't exist
    @param {str} path : multilevel dir
    @returns {None}
    '''
    if not cls.exists(path):
      os.makedirs(path)

  @classmethod
  def get_rename_file(cls,file_path,new_name='',prefix='',suffix='',separator='-'):
    '''
    @description : get the new file name path
    '''
    path_slices = file_path.split('/')
    original_name = path_slices[-1]
    copy_name = new_name if new_name else original_name
    if prefix:
      copy_name = prefix+separator+copy_name
    if suffix:
      copy_name = copy_name+separator+suffix
    path_slices[-1]=copy_name
    copy_path='/'.join(path_slices)
    return copy_path

  @classmethod
  def removefiles(cls,directory,retention_days=0):
    '''
    @description : clear files before n days
    @param {str} directory
    @param {int} retention_days : default 7
    @returns {int} deleted files count
    '''
    # 转换天数到时间间隔
    threshold = datetime.now() - timedelta(days=retention_days)
    removed_count = 0
    # 遍历目录
    for item in os.scandir(directory):
      try:
        # 获取文件的最后修改时间
        file_modified_time = datetime.fromtimestamp(os.path.getmtime(item.path))
        # 如果文件的最后修改时间早于阈值，则删除文件
        if os.path.isfile(item.path) and file_modified_time < threshold:
          os.remove(item.path)
          removed_count +=1
      except OSError as e:
        pass

    return removed_count

  @classmethod
  def dump_base64(cls,text):
    # 只接受bytes类型 b'xx'，且返回bytes，将其转为字符串
    return base64.b64encode(text.encode()).decode()

  @classmethod
  def load_base64(cls,b64):
    # 只接受bytes类型 b'xx'，且返回bytes，将其转为字符串
    return base64.b64decode(b64.encode()).decode()
