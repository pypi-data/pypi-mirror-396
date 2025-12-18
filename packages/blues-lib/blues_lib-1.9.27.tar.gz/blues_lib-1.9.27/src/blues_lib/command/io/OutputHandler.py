from blues_lib.type.output.STDOut import STDOut

class OutputHandler:

  @classmethod
  def handle(cls,ti:any,stdout:STDOut|None):
    if not stdout:
      return

    result = stdout.to_dict()
    for key,value in result.items():
      ti.xcom_push(key,value)
