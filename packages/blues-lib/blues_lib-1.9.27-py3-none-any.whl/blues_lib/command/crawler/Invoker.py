from blues_lib.sele.browser.chrome.ChromeFactory import ChromeFactory   
from blues_lib.crawler.CrawlerFactory import CrawlerFactory
from blues_lib.sele.browser.Browser import Browser
from blues_lib.type.output.STDOut import STDOut
from blues_lib.model.Model import Model

class Invoker():
  
  @classmethod
  def invoke(cls,model:Model)->STDOut:
    browser = cls.get_browser(model.config)
    crawler = CrawlerFactory(model,browser).create()
    return crawler.execute()
  
  @classmethod
  def get_browser(cls,config:dict)->Browser:
    browser_conf:dict = config.get('browser') or {}
    driver_config =  browser_conf.get('config') or {} # optional
    driver_options = browser_conf.get('options') or {} # optional
    browser = ChromeFactory(**driver_options).create(driver_config)
    if not browser:
      raise Exception(f'[{self.NAME}] fail to create the browser')
    return browser