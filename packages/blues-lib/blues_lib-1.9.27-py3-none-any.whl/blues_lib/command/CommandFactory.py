from blues_lib.type.factory.Factory import Factory
from blues_lib.type.executor.Command import Command
from blues_lib.namespace.CommandName import CommandName

# flow
from blues_lib.command.flow.Engine import Engine as FlowEngine
from blues_lib.command.flow.Loop import Loop as FlowLoop

# llm
from blues_lib.command.llm.Engine import Engine as LLMEngine
from blues_lib.command.llm.Loop import Loop as LLMLoop

# crawler
from blues_lib.command.crawler.Engine import Engine as CrawlerEngine
from blues_lib.command.crawler.Loop import Loop as CrawlerLoop

# standard
from blues_lib.command.standard.Dummy import Dummy
from blues_lib.command.standard.Cleaner import Cleaner

# sql
from blues_lib.command.sql.Querier import Querier
from blues_lib.command.sql.Updater import Updater
from blues_lib.command.sql.Inserter import Inserter
from blues_lib.command.sql.Deleter import Deleter

# notifier
from blues_lib.command.notifier.Email import Email

# material
from blues_lib.command.material.Sinker import Sinker
from blues_lib.command.material.Deduplicator import Deduplicator
from blues_lib.command.material.Validator import Validator
from blues_lib.command.material.Normalizer import Normalizer
from blues_lib.command.material.Localizer import Localizer

class CommandFactory(Factory):

  _COMMANDS:dict[str,Command] = {
    # flow command
    FlowEngine.NAME:FlowEngine,
    FlowLoop.NAME:FlowLoop,

    # llm
    LLMEngine.NAME:LLMEngine,
    LLMLoop.NAME:LLMLoop,

    # crawler
    CrawlerEngine.NAME:CrawlerEngine,
    CrawlerLoop.NAME:CrawlerLoop,
    
    # standard
    Dummy.NAME:Dummy,
    Cleaner.NAME:Cleaner,
    
    # sql
    Querier.NAME:Querier,
    Updater.NAME:Updater,
    Inserter.NAME:Inserter,
    Deleter.NAME:Deleter,
    
    # notifier
    Email.NAME:Email,

    # material
    Sinker.NAME:Sinker,
    Deduplicator.NAME:Deduplicator,
    Validator.NAME:Validator,
    Normalizer.NAME:Normalizer,
    Localizer.NAME:Localizer,
    
  }
  
  _TASK_CONF_FIELDS:list[str] = [
    'task_id',
    'command',
  ]
  
  @classmethod
  def create(cls,task_def:dict,bizdata:dict,ti:any)->Command | None:
    
    error:str = cls.check(task_def,bizdata,ti)
    if error:
      raise ValueError(f"Failed to create command - {error}")

    # overide
    command_value:str = task_def.get('command')
    command_name:CommandName|None = CommandName.from_value(command_value)
    if not command_name:
      error = f"The command '{command_value}' is not supported."
      raise ValueError(f"Failed to create command - {error}")

    executor:Command|None = cls._COMMANDS.get(command_name)
    if not executor:
      error = f"The command '{command_value}' is not supported."
      raise ValueError(f"Failed to create command - {error}")

    return executor(task_def,bizdata,ti)
  
  @classmethod
  def check(cls,task_def:dict,bizdata:dict,ti:any)->str:
    error:str = ''
    if not ti:
      error = f"{cls.__class__.__name__} The parameter 'ti' is missing."
    if not bizdata or not isinstance(bizdata,dict):
      error = f"{cls.__class__.__name__} The parameter 'bizdata' must be a dict."
    if not task_def or not isinstance(task_def,dict):
      error = f"{cls.__class__.__name__} The parameter 'task_def' must be a dict."

    for field in cls._TASK_CONF_FIELDS:
      if task_def.get(field) is None:
        error = f"{cls.__class__.__name__} The parameter 'task_def.{field}' is missing."   
        break
    return error

