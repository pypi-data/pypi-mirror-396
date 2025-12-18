from urllib.parse import urlparse
from blues_lib.type.chain.AllMatchHandler import AllMatchHandler
from blues_lib.material.file.MatFile import MatFile
from blues_lib.util.BluesAlgorithm import BluesAlgorithm
from blues_lib.util.BluesURL import BluesURL

class Downloader(AllMatchHandler):
  # download the images to the local

  def resolve(self)->None:
    entity = self._request.get('entity')

    if thumb_url := entity.get('mat_thumb'):
      entity['mat_thumb'] = self._download_thumb(entity,thumb_url)

    if paras:=entity.get('mat_paras'):
      entity['mat_paras'] = self._download_body_images(entity,paras)
    
  def _download_thumb(self,entity:dict,thumb_url)->str:
    return self._download(entity,thumb_url,'thumb')

  def _download_body_images(self,entity:dict,paras:list)->list[dict]:
    image_idx = 1
    convert_paras = []
    for para in paras:
      if para['type'] == 'image':
        if local_image := self._download(entity,para['value'],f'body-{image_idx}'):
          image_idx += 1
          para['value'] = local_image
          convert_paras.append({**para})
      else:
        convert_paras.append({**para})
    return convert_paras
    
  def _download(self,entity:dict,image_url:str,file_name_suffix:str='')->str:
    if not image_url:
      self._logger.warning(f'[{self.__class__.__name__}] Skip a empty url')
      return ''

    if not BluesURL.is_http_url(image_url):
      self._logger.warning(f'[{self.__class__.__name__}] Skip a not http url - {image_url}')
      return image_url

    # 有限使用页面url中域名作为命名空间
    mat_url = entity.get('mat_url')
    mat_site = entity.get('mat_site') or BluesURL.get_main_domain(mat_url)
    mat_id = entity.get('mat_id') or BluesAlgorithm.md5(entity['mat_url'])
    file_name = f"{mat_id}-{file_name_suffix}"

    stdout:STDOut = MatFile.get_download_image(mat_site,file_name,image_url)
    if stdout.code!=200:
      self._logger.error(f'[{self.__class__.__name__}] {stdout.message} - {stdout.data}')
      return ''
    return stdout.data
