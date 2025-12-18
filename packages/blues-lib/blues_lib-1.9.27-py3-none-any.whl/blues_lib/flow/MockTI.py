class MockTI:

  # static field to save all tasks' xcom data
  store:dict = {}
  
  def __init__(self,task_id:str) -> None:
    # public field
    self.task_id:str = task_id

    if not task_id in MockTI.store:
      MockTI.store[task_id] = {}
  
  def xcom_pull(self, task_ids: str | list[str] | tuple[str] = '', key: str = '') -> any:
    # 若未指定task_ids，默认当前任务
    if not task_ids:
      task_ids = self.task_id
      
    if not key:
      key = 'return_value'

    # 处理单个task_id的情况（转为列表统一处理）
    if isinstance(task_ids, str):
        task_ids = [task_ids]
    
    # 多任务时返回列表，单任务时返回单个值
    results = []
    for task_id in task_ids:
        if task_id in MockTI.store:
            results.append(MockTI.store[task_id].get(key))
        else:
            results.append(None)
    
    # 若原始输入是单个字符串，返回单个结果（而非列表）
    return results[0] if len(results) == 1 else results
  
  def xcom_push(self, key: str, value: any) -> None:
    MockTI.store[self.task_id][key] = value
