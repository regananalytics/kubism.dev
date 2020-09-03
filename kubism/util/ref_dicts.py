import collections

class registry(collections.MutableMapping, dict):

    def __getitem__(self,key):
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        if not isinstance(value, list):
            value = [value]
        if key in self:
            reg = self.__getitem__(key)
            if not value in reg:
                reg.append(value[0])
                value = reg
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)

    def __iter__(self):
        return dict.__iter__(self)

    def __len__(self):
        return dict.__len__(self)
        
    def __contains__(self, x):
        return dict.__contains__(self, x)



class recipe(collections.MutableMapping, dict):
    # {kind:[(fieldname, fieldtype),(fieldname, fieldtype)]}

    def __getitem__(self,key):
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        if key in self:
            reg = self.__getitem__(key)
            if not value in reg:
                if reg == []:
                    reg = [value]
                else:
                    reg.append(value)
                value = reg
            else:
                return
        else:
            if value == {}:
                value = []
            elif not isinstance(value, list):
                value = [value]
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)

    def __iter__(self):
        return dict.__iter__(self)

    def __len__(self):
        return dict.__len__(self)
        
    def __contains__(self, x):
        return dict.__contains__(self, x)


        