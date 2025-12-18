from blues_lib.behavior.Trigger import Trigger
from blues_lib.util.BluesMailer import BluesMailer  

class Email(Trigger):

  def _trigger(self)->bool:
    payload = self._get_payload()
    mailer = BluesMailer.get_instance()
    stdout = mailer.send(payload)
    return stdout.code == 200

  def _get_payload(self)->dict:
    payload_conf:dict = self._config.get('value')
    subject = payload_conf.get('subject')
    paras = payload_conf.get('paras')
    addressee = payload_conf.get('addressee') or ['langcai10@dingtalk.com']
    addressee_name = payload_conf.get('addressee_name') or 'BluesLiu'

    return {
      'subject':subject,
      'paras':paras,
      'addressee':addressee, # send to multi addressee
      'addressee_name':addressee_name,
    }
