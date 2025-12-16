from .core import MyQAPI, GarageDoor

# make module callable: mylib(data,data2) -> MyQAPI instance
def __call__(**kwargs):
    return MyQAPI(**kwargs)

# public names:
create = __call__   # alias so users can call mylib.create(...)

# Export the class for direct use
__all__ = ['MyQAPI', 'GarageDoor', 'create']
