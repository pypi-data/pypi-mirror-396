import copy
from datetime import datetime, date

from ROTools.Helpers.Attr import setattr_ex, hasattr_ex, getattr_ex, delattr_ex
from ROTools.Helpers.DumpBase import DumpBase



class DictObj(DumpBase):
    def __init__(self, *args, **kwargs):
        if (args and kwargs) or len(args) > 1:
            raise Exception("Flow")

        if kwargs or (args and isinstance(args[0], dict)):
            d = kwargs or args[0]
            for k, b in d.items():
                if isinstance(b, (list, tuple)):
                    self.set(k, [DictObj(x) if isinstance(x, dict) else x for x in b])
                else:
                    self.set(k, DictObj(b) if isinstance(b, dict) else b)
            return

        if not args:
            return

        d = args[0]
        if isinstance(d, DictObj):
            for k, v in d.__dict__.items():
                self.__dict__[k] = copy.deepcopy(v)
            return

        raise Exception("Flow")


    def to_dict(self):
        result = {}
        for k, v in self.items():
            result[k] = _convert_to_dict(v)
        return result

    def get(self, path, default=None, throw=False, cast_cb=None):
        self.has(path, throw=throw)
        value = getattr_ex(self, path, default)
        value = cast_cb(value) if cast_cb and value is not None else value
        return value


    def set(self, path, value, overwrite=True):
        if overwrite or not self.has(path):
            setattr_ex(self, path, value, parent_class=DictObj)

    def copy(self, obj, path, default=None, throw=False):
        if isinstance(path, list):
            for item in path:
                self.copy(obj, item, default=default, throw=throw)
            return
        value = obj.get(path, default=default, throw=throw)
        self.set(path, value)

    def rem(self, path, throw=False):
        if not self.has(path, throw=throw):
            return
        delattr_ex(self, path)

    def has(self, path, throw=False):
        result = hasattr_ex(self, path)
        if not result and throw:
            raise Exception("Path not found: " + path)
        return hasattr_ex(self, path)

    def convert(self, path, cb):
        if not self.has(path):
            return
        self.set(path, cb(self.get(path)))

    def set_values(self, values, only_if_exists=True):
        for path, nev_value in values:
            if only_if_exists and not hasattr_ex(self, path):
                continue
            self.set(path, nev_value)

    def fields_list(self):
        return _gen_fields_list(self)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def clone(self):
        import copy
        return copy.deepcopy(self)


def _gen_fields_list(obj, current_path=None):
    if not isinstance(obj, DictObj):
        return [(current_path, obj)]
    result = []
    for key, value in obj.items():
        next_path = ".".join([a for a in (current_path, key) if a is not None])

        if isinstance(value, DictObj):
            result.extend(_gen_fields_list(value, current_path=next_path))
        else:
            result.append((next_path, value))
    return result

def _convert_to_dict(obj):
    if isinstance(obj, DictObj):
        return obj.to_dict()

    if isinstance(obj, datetime):
        return obj.isoformat()

    if isinstance(obj, date):
        return obj.isoformat()

    if isinstance(obj, list) or isinstance(obj, tuple):
        return [_convert_to_dict(a) for a in obj]

    return obj