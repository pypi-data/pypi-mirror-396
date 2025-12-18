from blues_lib.namespace.NSEnum import NSEnum
from blues_lib.namespace.EnumNS import EnumNS

class CommandName(EnumNS):
  
  class Flow(NSEnum):
    ENGINE = "command.flow.engine"
    LOOP = "command.flow.loop"

  class LLM(NSEnum):
    ENGINE = "command.llm.engine"
    LOOP = "command.llm.loop"
    
  class Crawler(NSEnum):
    ENGINE = "command.crawler.engine"
    LOOP = "command.crawler.loop"
  
  class Standard(NSEnum):
    DUMMY = "command.standard.dummy"
    CLEANER = "command.standard.cleaner"
  
  # sql 
  class SQL(NSEnum):
    QUERIER = "command.sql.querier"
    UPDATER = "command.sql.updater"
    INSERTER = "command.sql.inserter"
    DELETER = "command.sql.deleter"

  class Notifier(NSEnum):
    EMAIL = "command.notifier.email"

  class Material(NSEnum):
    SINKER = "command.material.sinker"
    DEDUPLICATOR = "command.material.deduplicator"
    VALIDATOR = "command.material.validator"
    NORMALIZER = "command.material.normalizer"
    LOCALIZER = "command.material.localizer"
