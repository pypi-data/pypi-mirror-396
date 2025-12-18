class FlowSkipException(Exception):
  """自定义异常：表示流程需要跳过"""
  def __init__(self, message="skip the command"):
    self.message = message
    super().__init__(self.message)