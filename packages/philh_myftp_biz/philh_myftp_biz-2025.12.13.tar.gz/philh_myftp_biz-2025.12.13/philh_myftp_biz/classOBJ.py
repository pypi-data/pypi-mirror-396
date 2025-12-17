from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .db import colors

class attr:
    """
    Attribute of Instance/Object
    """

    def __init__(self,
        parent,
        name: str
    ):
        self.name = name
        self.parent = parent

    def callable(self) -> bool:
        """
        Check if the attribute can be called like a function
        """
        return callable(self.value())
    
    def private(self) -> bool:
        """
        Check if the attribute is name mangled
        """
        
        if self.name.startswith('__'):
            return True
        
        elif hasattr(self.parent, '__name__') and (self.name.startswith(f'_{self.parent.__name__}__')):
            return True
        
        elif (self.name.startswith(f'_{self.parent.__class__.__name__}__')):
            return True

        else:
            
            for base in self.parent.__class__.__bases__:
                if self.name.startswith(f'_{base.__name__}__'):
                    return True

        return False

    def value(self):
        """
        Get the value of the attribute
        
        Will return None if private
        """

        if not self.private():
            return getattr(self.parent, self.name)
    
    def __str__(self):
        """
        Get the value of the attribute as a string

        Formats with json.dumps
        """
        from .json import dumps

        try:
            return dumps(
                obj = self.value(),
                indent = 2
            )
        except:
            return str(self.value())

def attrs(obj):
    """
    Get all attributes of an instance or object
    """
    for name in dir(obj):
        yield attr(obj, name)

def path(obj) -> str:
    """
    Get Full path of instance

    Ex: path(print) -> '__builtins__.print'
    """

    return obj.__class__.__module__ + '.' + obj.__class__.__qualname__

def location(obj) -> str:
    """
    Get the hexadecimal location of an instance in memory
    """
    return hex(id(obj))

def stringify(obj) -> str:
    """
    Creates a string containing a table of all attributes of an instance
    (for debugging)
    """
    from io import StringIO
    
    IO = StringIO()

    IO.write('--- ')
    IO.write(path(obj))
    IO.write(f' @{location(obj)}')
    IO.write(' ---\n')

    for c in attrs(obj):
        if not (c.private() or c.callable() or (c.value() is None)):
            IO.write(c.name)
            IO.write(' = ')
            IO.write(str(c))
            IO.write('\n')

    return IO.getvalue()

def log(
    obj,
    color: 'colors.names' = 'DEFAULT'
) -> None:
    """
    Print all attributes of the instance to the terminal
    """
    from .pc import print as __print
    
    print()

    __print(
        stringify(obj),
        color = color
    )
    
    print()

def to_json(obj) -> dict:
    """
    Convert an instance to a dictionary
    """

    json_obj = {}

    for c in attrs(obj):
        if not (c.private() or c.callable()):
            json_obj[c.name] = c.value()

    return json_obj
