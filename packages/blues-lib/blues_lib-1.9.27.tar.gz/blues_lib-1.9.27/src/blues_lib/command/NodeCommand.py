from abc import ABC,abstractmethod
from typing import final

from blues_lib.type.executor.Command import Command
from blues_lib.namespace.CrawlerName import CrawlerName
from blues_lib.type.output.STDOut import STDOut
from blues_lib.model.Model import Model
from blues_lib.command.io.IOExcept import IOExcept
from blues_lib.command.io.InputHandler import InputHandler
from blues_lib.command.io.OutputHandler import OutputHandler
from blues_lib.hook.command.CommandHook import CommandHook
from blues_lib.deco.CommandSTDOutLog import CommandSTDOutLog

class NodeCommand(Command,ABC):

  NAME = None
  
  def __init__(self,task_def:dict,bizdata:dict,ti:any) -> None:
    f'''
    Args:
      task_def {dict}: the task's definition
        - id {str} : the task id
        - command {str} : the command name
        - meta {dict} : the task meta data
        - input {list|dict|None} : the task input definition
        - output {list|dict|None} : the task output definition
        - setup {list|dict|None} : the task setup hook
        - teardown {list|dict|None} : the task teardown hook
      bizdata {dict} : the task bizdata
      ti {any} : the task instance
    '''
    super().__init__({})

    # the input mapping can not useing the placeholder
    self._task_def:dict = task_def
    self._bizdata:dict = bizdata
    self._ti:any = ti

    self._model = None
    self._meta = {}
    self._config = {}
    self._summary = {}

    self._dag_def = {}

  @property
  def task_id(self)->str:
    return self._task_def.get('task_id')
  
  def _init(self)->None:

    task_def,task_biz = InputHandler(self._task_def,self._bizdata,self._ti).handle()
    self._task_def = task_def
    self._bizdata = task_biz

    # set model or dag
    self._create_model()
    self._create_dag()

    # set fields after recalculate the model
    self._setup()

  @final
  @CommandSTDOutLog()
  def execute(self)->STDOut:

    # must validate in runtime, make sure the upstream's data has created
    self._init()

    # Airflow不能识别自定义异常，使用xcom标识状态
    hook_defs:list[dict] = self._task_def.get('before_invoked')
    options:dict = {'ti':self._ti}
    CommandHook(hook_defs,options).execute()

    # 因为有多个hook，所以不能基于某个实例判断是否block或skip
    CommandHook.block(self._ti)
    stdout:STDOut|None = CommandHook.skip(self._ti)
    if stdout:
      return stdout

    stdout = self._invoke()

    hook_defs:list[dict] = self._task_def.get('after_invoked')
    options:dict = {'ti':self._ti,'stdout':stdout}
    CommandHook(hook_defs,options).execute()

    # 因为有多个hook，所以不能基于某个实例判断是否block或skip
    CommandHook.block(self._ti)
    # output after hook deal
    OutputHandler.handle(self._ti,stdout)

    # raise except if the stdout is not matched
    IOExcept.validate_except(self._task_def,stdout)
    
    return stdout
  
  def _create_model(self):
    if meta:= self._task_def.get('meta'):
      self._meta = meta
      self._model:Model = Model(meta,self._bizdata)
      self._config:dict = self._model.config
      self._summary:dict = self._config.get(CrawlerName.Field.SUMMARY.value) or {}
      # validate the metadata
      IOExcept.validate_metadata(self._config)
      
  def _create_dag(self):
    if dag:= self._task_def.get('dag'):
      self._dag_def:dict = dag
    
  def _setup(self): 
    # template method
    pass

  @abstractmethod
  def _invoke(self)->STDOut:
    pass
