import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
from blues_lib.util.BluesAlgorithm import BluesAlgorithm
from blues_lib.util.BluesDateTime import BluesDateTime
from blues_lib.type.output.STDOut import STDOut

class BluesMailer():

  config = {
    # pick a smtp server
    'server' : 'smtp.qq.com',
    'port' : 465,
    # debug level: 0 - no message; 1 - many messages
    'debug_level' : 0, 
    # the sender's address
    'addresser' : '1121557826@qq.com',
    'addresser_name' : 'BluesLiu QQ',
    # the qq's auth code (not the account's login password)
    'addresser_pwd' : 'ryqokljshrrlifae',
  }

  __instance = None

  @classmethod
  def get_instance(cls):
    if not cls.__instance:
      cls.__instance = BluesMailer()
    return cls.__instance

  def __init__(self):
    self.connection = self.__get_connection()

  def __get_connection(self):
    connection = smtplib.SMTP_SSL(self.config['server'],self.config['port'])
    connection.set_debuglevel(self.config['debug_level'])
    connection.login(self.config['addresser'],self.config['addresser_pwd'])
    return connection

  def send(self,payload)->STDOut:
    '''
    @description : send the mail
    @param {MailPayload} payload : mail's required info
     - addressee ：list | str  ; required
     - addressee_name ：str , can't contains space
     - subject : str ; required
     - content : str 
    @returns {STDOut} : send result

    '''
    # the receiver's address
    if not payload.get('addressee'):
      return STDOut(501,'The addressee address is empty!',False)
    
    if not payload.get('subject'):
      return STDOut(502,'The mail subject is empty!',False)

    if not payload.get('paras'):
      return STDOut(503,'The mail paras is empty!',False)
    
    try:
      message = self._get_message(payload)
      self.connection.sendmail(self.config['addresser'],payload['addressee'],message)
      self.connection.quit()
    except Exception as e:
      return STDOut(504,f'Failed to send - {e}',False)

    return STDOut(200,'Managed to send',True)

  def _get_html_body(self,payload:dict,message)->str:
    subject = self._get_title(payload.get('subject',''))
    time = self._get_time()
    para = self._get_para(payload.get('paras',[]),message)
    return f'<div style="padding:1rem 2%;">{subject}{time}{para}</div>'
  
  def _get_title(self,title:str):
    return f'<h1>{title}</h1>'
  
  def _get_time(self):
    now = BluesDateTime.get_now()
    return f'<p style="margin-top:1rem;color:gray;font-size:14px;" data-tag="time">At {now}</p>'
  
  def _get_message(self,payload):
    message = MIMEMultipart()
    message['subject'] = payload['subject']
    # the last string must be from mail address
    from_with_nickname = '%s <%s>' % (self.config['addresser_name'],self.config['addresser']) 
    message['from'] = Header(from_with_nickname)

    if type(payload['addressee'])==str:
      message['to'] = Header(payload.get('addressee_name',payload['addressee']))
    else:
      message['to'] = Header(','.join(payload['addressee']))
    
    # support html document
    content = self._get_html_body(payload,message)
    message.attach(MIMEText(content, 'html'))
    return message.as_string()

  def _get_para(self,paras:list[str],message)->str:
    html = ''
    for para in paras:
      para = para if isinstance(para,dict) else {'type':'text','value':para}
      html += self._get_html(para,message)
    return html
  
  def _get_html(self,para:dict,message)->str:
    if para['type']=='text':
      return self._get_text(para['value'])
    elif para['type']=='image':
      return self._get_image(para['value'],message)
    elif para['type']=='link':
      return self._get_link(para['value'])
    elif para['type']=='remark':
      return self._get_remark(para['value'])
    else:
      return ''
  
  def _get_text(self,value:str):
    return f'<p style="margin-top:1rem;line-height:26px;font-size:16px;" data-tag="para">{value}</p>'

  def _get_image(self,image:str,message)->str:
    if not image:
      return ''
    
    with open(image, 'rb') as file:
      img = MIMEImage(file.read())
    # 自定义一个唯一id
    cid = 'image-%s' % BluesAlgorithm.md5(image)
    img.add_header('Content-ID', '<%s>' % cid)
    message.attach(img)
    return '<p style="margin-top:1rem;"><img style="width:100%;" src="cid:{}"/></p>'.format(cid)

  def _get_link(self,link:dict|str):
    if not link:
      return ''
    
    link = link if isinstance(link,dict) else {'href':link,'text':link}
    return '''
      <p data-tag="link" style="margin-top:1rem;"><a href="{}" style="font-size:16px;color:#07c;">{}</a></p>
      '''.format(link['href'],link['text'])
  
  def _get_remark(self,remark:str):
    if not remark:
      return ''
    return f'<p style="margin-top:1rem;line-height:20px;font-size:14px;color:gray;" data-tag="remark">{remark}</p>'
