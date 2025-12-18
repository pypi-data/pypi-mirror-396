import re
from typing import Any
from pyhocon import ConfigFactory
from pyhocon.config_tree import ConfigTree
from blues_lib.hocon.replacer.Replacer import Replacer

class VariableFormatReplacer(Replacer):

  '''
  replace the variable in the template with the given values
  - single variable "{}"
  - interpolate variable "name is {}, age is {}"
  '''  

  VAR_SEARCH_PATTERN = r"\{\}"
  VAR_MATCH_PATTERN = r"^\{\}$"
  
  def replace(self)->dict:
    if not self._variables or not self._template:
      return self._template
    
    tree:ConfigTree = ConfigFactory.from_dict(self._template)
    
    for path,value in self._variables.items():
      node:dict = self._get_node(tree,path)
      node_key:str|int|None = node.get('key')
      node_value:Any|None = node.get('value')
      node_parent:ConfigTree|None = node.get('parent')
      
      # if the template's node value is not a string, skip (must not be a placeholder)
      if not isinstance(node_value,str):
        continue
      
      # if the node's value is not a placeholder, skip
      if not re.search(self.VAR_SEARCH_PATTERN,node_value):
        continue
      
      replacement:Any = None
      if re.match(self.VAR_MATCH_PATTERN,node_value):
        # if the placeholder is a single variable, replace it using the original value
        replacement = value
      else:
        # if the placeholder is an interpolate variable, replace it using the format syntax
        args:list[Any] = value if isinstance(value,list) else [value]
        replacement = node_value.format(*args)
      
      node_parent[node_key] = replacement
    
    return tree.as_plain_ordered_dict()
  
  def _get_node(self,tree:ConfigTree,path:str)->dict:
    '''
    get the ConfigTree's node info, support the path include list index:
    - with dot notation: "prompt.user.content"
    - with list index: "crawler.setup[0].urls[1].url"
    
    node's attributes:
    - key: the dict node's key or the list node's index
    - value: the node value (may be a placeholder)
    - parent: the parent node of the ConfigTree
    
    Error handling:
    - If the path doesn't exist, node's parent and value will be set to None
    - If array index is out of range or negative, node's parent and value will be set to None
    '''
    node:dict = {
      "key":None, # {str|int} the dict key or the list index
      "value":None, # {Any} the node value (may be a placeholder)
      "parent":None, # {ConfigTree} the parent node 
    }
    
    # Split the path into segments, handling both dot notation and list indices
    # Regex to match either: [index] or .key
    segments = re.split(r'\.(?![^\[]*\])|\[(\d+)\]', path)
    # Filter out empty strings and None values
    segments = [seg for seg in segments if seg is not None and seg != '']
    
    current = tree
    parent = None
    key = None
    
    # Traverse through each segment
    for segment in segments:
      if isinstance(current, list):
        # Current is a list, segment should be an index
        try:
          index = int(segment)
          # Check if index is valid (non-negative and within range)
          if index < 0 or index >= len(current):
            # Invalid index, return node with None values
            return node
          key = index
        except ValueError:
          # Invalid index format (not a valid integer), return node with None values
          return node
      else:
        # Current is a ConfigTree, segment should be a key
        key = segment
        # Check if key exists in current node
        if key not in current:
          return node
      
      # Save parent before moving to next level
      parent = current
      
      # Move to next level
      if isinstance(current, list):
        # If current is a list, get the item at index (already validated)
        current = current[key]
      else:
        # If current is a ConfigTree, get the value by key (already validated)
        current = current[key]
    
    # Set the node information
    node['key'] = key
    node['value'] = current
    node['parent'] = parent
    
    return node