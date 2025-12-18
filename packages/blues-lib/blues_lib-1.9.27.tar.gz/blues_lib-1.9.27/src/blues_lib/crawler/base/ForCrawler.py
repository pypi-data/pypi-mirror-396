from blues_lib.type.output.STDOut import STDOut
from blues_lib.model.Model import Model
from blues_lib.namespace.CrawlerName import CrawlerName
from blues_lib.crawler.base.BaseCrawler import BaseCrawler

class ForCrawler(BaseCrawler):

  NAME = CrawlerName.Engine.FOR
    
  def _before_crawled(self):
    super()._before_crawled()
    self._entities:list[dict] = self._get_entities()

  def _get_entities(self)->list[dict]|None:
    '''
    Set the entities for for crawler
    @return {None}
    '''
    entities:list[dict] = self._summary_conf.get(CrawlerName.Field.ENTITIES.value) 
    if entities:
      return entities

    for_count:int = self._summary_conf.get(CrawlerName.Field.FOR_COUNT.value) or 1
    # pad a empty entity for each for count
    return [{} for _ in range(for_count)]
    
  def _crawl(self)->STDOut:
    '''
    override the crawl method
    execute the main crawler looply, by the entities or count
    @return {STDOut}
    '''
    if not self._crawler_meta:
      message = f'[{self.NAME}] Failed to crawl - Missing crawler config'
      return STDOut(500,message)

    if not self._entities:
      message = f'[{self.NAME}] Failed to crawl - Missing entities'
      return STDOut(500,message)
    
    
    try:
      results:list[any] = []
      for entity in self._entities:
        # use the entity to cover the bizdata
        merged_entity = {**self._bizdata,**entity}
        model = Model(self._crawler_meta,merged_entity)
        output:STDOut = self._invoke(model)
        # only save the data field
        if isinstance(output.data,list):
          results.extend(output.data)
        else:
          results.append(output.data)
        self._set_interval()
        
      return STDOut(200,'ok',results)
    except Exception as e:
      message = f'[{self.NAME}] Failed to crawl - {e}'
      return STDOut(500,message)
    