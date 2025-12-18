import re
from blues_lib.type.output.STDOut import STDOut
from blues_lib.util.BluesMailer import BluesMailer  
from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.util.FileReader import FileReader
from blues_lib.namespace.CommandName import CommandName

class Email(NodeCommand):

  NAME = CommandName.Notifier.EMAIL

  def _invoke(self)->STDOut:
    payload = self.get_payload()
    mailer = BluesMailer.get_instance()
    return mailer.send(payload)
      
  def get_payload(self)->dict:
    entities:list[dict] = self._summary.get('entities',[])
    subject = self._get_subject(entities)
    paras = self._get_paras(entities)
    
    return {
      'subject':subject,
      'paras':paras,
      'addressee':['langcai10@dingtalk.com'], # send to multi addressee
      'addressee_name':'BluesLiu',
    }
    
  def _get_subject(self,entities:list[dict])->str:
    success_count = 0
    failure_count = 0
    for entity in entities:
      if entity.get('pub_stat') == 'success':
        success_count += 1
      else:
        failure_count += 1
    return f'Published : {success_count} success, {failure_count} failure'
    
  def _get_paras(self,entities:list[dict])->list[dict]:
    paras = []
    for entity in entities:
      paras.append({
        'type':'text',
        'value':f'{entity.get("mat_title")} - {entity.get("pub_stat")}',
      })
      paras.append({
        'type':'image',
        'value':entity.get('pub_shot'),
      })
    return paras

  def _get_log(self):
    file = self._logger.file
    separator = self._logger.separator
    content = FileReader.read(file)
    if content:
      # retain the latest one
      items = content.split(separator)
      non_empty_items = [item.strip() for item in items if item.strip()]
      content = non_empty_items[-1] if non_empty_items else content
      
      # break line
      content = content.replace('\n','<br/>')
      # dash line
      pattern = r'[-=]{10,}'
      content = re.sub(pattern, '----------', content)
    return content