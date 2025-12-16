import unicodedata
from functools import wraps

def _string_to_ascii(string):
    return unicodedata.normalize('NFKD', string).encode('ascii', errors='ignore').decode('ascii')

def handle_data_tuples(func):
    """
    Decorator to handle string or list of tuples.
    
    Inputs:
    - string: processes directly, returns [result]
    - [(id, type, content, level), ...]: list of data tuples
    
    Returns:
    - string -> [result]
    - list -> [result1, None, result2, ...] where None = non-'text' types
    """
    @wraps(func)
    def wrapper(data, *args, **kwargs):
        # Check if it's a list of tuples
        if isinstance(data, list):
            results = []
            for item in data:
                if not (isinstance(item, tuple) and len(item) == 4):
                    raise ValueError(f"Expected tuple of length 4, got {type(item)}")
                
                id_, type_, content, level = item
                
                if type_ == 'text':
                    result = func(content, *args, **kwargs)
                    results.append(result)
                else:
                    results.append(None)
            
            return results
        
        # Otherwise treat as string
        else:
            return func(data, *args, **kwargs)
    
    return wrapper