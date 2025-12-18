from blues_lib.dao.login.LoginMutator import LoginMutator
from blues_lib.cleaner.CleanerHandler import CleanerHandler
from blues_lib.type.output.SQLSTDOut import SQLSTDOut

class LoginLogHandler(CleanerHandler):

  kind = 'handler'
  mutator = LoginMutator()

  def resolve(self,request)->int:
    '''
    Args:
      {dict} request: 
        - {int} validity_days : by default is 100
    Returns {int} count
    '''
    validity_days = request.get('rule',{}).get('validity_days',100)
    conditions = [
      {
        'field':'login_created_time',
        'comparator':'<=',
        'value':'DATE_SUB(CURRENT_DATE, INTERVAL %s DAY)' % validity_days,
        'value_type':'function',
      }
    ]
    output:SQLSTDOut = self.mutator.delete(conditions)
    count = output.count or 0
    request.get('messages').append(f'Deleted {count} login log rows')
    return count