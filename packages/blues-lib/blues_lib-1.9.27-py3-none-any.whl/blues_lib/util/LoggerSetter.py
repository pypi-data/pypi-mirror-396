import os,logging,datetime

from blues_lib.util.BluesFiler import BluesFiler 
from blues_lib.material.file.MatFile import MatFile

class LoggerSetter(): 

  _LOG_LEVELS = {
    'debug':logging.DEBUG,
    'info':logging.INFO, # will print all system info 
    'warning':logging.WARNING,
    'error':logging.ERROR,
  }
  _WIDTH = 100 
  _NAME = 'airflow.task' # same to the logger name in the DAG

  def __init__(self,config={}):
    '''
    @description : set log config
    @param {str} config.directory : Directory for storing logs
    @param {str} config.name : log's topic
    @param {int} config.retention_days : Maximum number of days for storing logs
    @param {str} config.level : The lowest level of log output
      - enum: debug info warning error
    '''
    self._config = self._get_config(config)


  def _get_config(self,config:dict):
    dft = {
      'name':self._NAME,
      'file_name':os.environ.get('OS_LOG_NAME',self._NAME),
      'directory':MatFile.get_today_log_root(),
      'level':'info',
      'retention_days':7,
    }
    return {**dft,**config} if config else dft
    
  def _set_dir(self):
    # make sure the dir exist
    BluesFiler.makedirs(self._config['directory'])
    # clear log history
    BluesFiler.removefiles(self._config['directory'],self._config['retention_days'])

  def set(self):
    self._set_dir()

    log_level  = self._LOG_LEVELS.get(self._config['level'],logging.INFO)
    logging.basicConfig(level=log_level)
    logger = logging.getLogger(self._config['name']) # will be show in the formatter as the `name`

    formatter = self._get_airflow_formatter()

    # output to the logs
    log_file = self._get_log_file()
    file_logger = logging.FileHandler(log_file,'a','utf-8')
    file_logger.setFormatter(formatter)
    logger.addHandler(file_logger)
    
    # output to the console
    #console_logger = logging.StreamHandler()
    #console_logger.setFormatter(formatter)
    #logger.addHandler(console_logger)

  def _get_airflow_formatter(self):
    formatter = '[%(asctime)s] %(filename)s %(lineno)s %(levelname)s - %(message)s'
    return logging.Formatter(formatter,datefmt='%Y-%m-%d %H:%M:%S')
      
  def _get_formatter(self):
    split_line = ''.join(['-' for x in range(self._WIDTH)])
    formatter = split_line+'\n'+'%(levelname)s (%(name)s) %(asctime)s:\n%(message)s'
    return logging.Formatter(formatter)
      
  def _get_log_file(self):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    log_name = f"{self._config['file_name']}_{today}.log"
    return os.path.join(self._config['directory'],log_name)

  @property
  def config(self):
    return self._config

  @property
  def file(self):
   return self._get_log_file() 

  def print_file(self):
    title = self.file
    char = '-'
    padding = (self._WIDTH - len(title) - 2) // 2
    left = char * padding
    right = char * (self._WIDTH - padding - len(title) - 2)
    print(f'\n{left} {title} {right}')

