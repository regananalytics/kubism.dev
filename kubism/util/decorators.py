# Copyright 2020 Regan Analytics

# Automate decorator to write, build, and push images
def automate(init_func): #TODO: remove *args, **kwargs?
    def wrapper(init_self, *args, **kwargs):
        if 'automate' in kwargs:
            _automate = kwargs.pop('automate')
        else:
            _automate = False
        init_func(init_self, *args, **kwargs)
        if _automate:
            init_self.automate()
    return wrapper

