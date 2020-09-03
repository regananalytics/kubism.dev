from kubism.util.ref_dicts import registry


class Backlog:

    def __init__(self):
        self.backlog = registry()


    def append(self, trigger, func, args, kwargs={}):
        self.backlog.update({trigger:{func:(args, kwargs)}})


    def execute(self, trigger):
        if (trigger_log := self.backlog.pop(trigger, None)) is not None:
            rets = []
            print(f'Executing from backlog:')
            while True:
                try:
                    next = trigger_log.pop(0)
                    func = list(next.keys())[0]
                    args, kwargs = next[func]
                    print(f'\t{func.__qualname__}')
                    ret = func(*args, **kwargs)
                    rets.append(ret)
                except IndexError:
                    break
            return rets


    # Backlog method decorator
    #   Adds method to backlog until condition is met
    @classmethod
    def method(cls, condition=None, trigger=None):
        def decorate_method(func, *args, **kwargs):
            def wrapper_method(self, *args, **kwargs):
                if getattr(self, condition):
                    func(self, *args, **kwargs)
                    return True
                else:
                    self.backlog.append(trigger, func, (self, *args), kwargs)
                    return False
            return wrapper_method
        return decorate_method


    @classmethod
    def condition(cls, func, *args, **kwargs):
        def wrapper_condition(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.backlog.execute(func.__qualname__)
            return True
        return wrapper_condition