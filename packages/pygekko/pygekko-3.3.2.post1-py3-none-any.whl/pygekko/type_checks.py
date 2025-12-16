# Type checks and similar are stored here

def is_string(x):
    """
    Type error is the argument is not a string
    """
    if not isinstance(x, str):        
        raise TypeError(f"Argument must be a string, but type is: {type(x).__name__}")
    
def is_list_of_strings(x):
    """
    Type error is the argument is not a list of strings
    """
    if not isinstance(x, list):        
        raise TypeError(f"Argument must be a list type, but typs is: {type(x).__name__}")
    for x2 in list:
        if not isinstance(x2, str):
            raise TypeError(f"All elements must be string type, but one is type: {type(x2).__name__}")
    
def length(x, n):
    """
    Error is args does not have length = n.
    """
    if len(x) != n:
        raise ValueError(f"Expected {n} elements, got {len(x)}.")