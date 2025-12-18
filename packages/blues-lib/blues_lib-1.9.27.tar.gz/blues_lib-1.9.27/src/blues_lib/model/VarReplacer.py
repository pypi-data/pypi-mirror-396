from blues_lib.model.BaseVarReplacer import BaseVarReplacer
from blues_lib.model.EnvVarReplacer import EnvVarReplacer
from blues_lib.model.CalVarReplacer import CalVarReplacer

class VarReplacer(BaseVarReplacer):
    '''
    Composite variable replacer that combines multiple variable replacers.
    Performs variable replacement using multiple replacers in a single traversal,
    checking each replacer in order until a value is found.
    
    This avoids the need for multiple separate replacements and duplicate traversals.
    '''
    
    # Class-level storage for replacer classes
    _replacer_classes = [EnvVarReplacer, CalVarReplacer]
    
    @classmethod
    def set_replacers(cls, replacer_classes):
        '''
        Set the list of replacer classes to use.
        
        Args:
            replacer_classes: List of replacer classes to use for variable lookup
        '''
        cls._replacer_classes = replacer_classes
    
    @classmethod
    def _get_raw_value(cls, var_name: str):
        '''
        Get value by checking all configured replacers in order.
        
        Args:
            var_name: Variable name to look up
            
        Returns:
            First found variable value from any replacer, or None if not found
        '''
        for replacer_class in cls._replacer_classes:
            value = replacer_class._get_raw_value(var_name)
            if value is not None:
                return value
        return None
    
    @classmethod
    def create_with_replacers(cls, replacer_classes):
        '''
        Create a composite replacer with specified replacers.
        
        Args:
            replacer_classes: List of replacer classes to use
            
        Returns:
            VarReplacer class with configured replacers
        '''
        # Create a new subclass to avoid modifying the original class
        class CustomVarReplacer(cls):
            pass
        CustomVarReplacer._replacer_classes = replacer_classes
        return CustomVarReplacer