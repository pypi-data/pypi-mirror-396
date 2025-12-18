from blues_lib.material.file.MatFile import MatFile
from blues_lib.cleaner.CleanerHandler import CleanerHandler
from blues_lib.util.BluesFiler import BluesFiler

class MaterialHandler(CleanerHandler):

  kind = 'handler'

  def resolve(self,request)->int:
    '''
    Args:
      {dict} request : 
        - {int} validity_days : by default is 100
    Returns {int} count
    '''
    validity_days = request.get('rule',{}).get('validity_days',30)
    root = MatFile.get_material_root()
    count = BluesFiler.removedirs(root,validity_days) or 0
    request.get('messages').append(f'Deleted {count} material files')
    return count
