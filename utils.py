from math import ceil


def teto_inteiro(x):
    return int(ceil(x))


def divisao_inteira_superior(x, y):
    return int(ceil((1.0 * x) / y))


class dotdict(dict):
    def __getattr__(self, attr):
        return self.get(attr, None)
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class EqualByAttributes(object):
    def __eq__(self, outro):
        return self.__dict__ == outro.__dict__


class EqualByUnicode(object):
    def __eq__(self, outro):
        return unicode(self) == unicode(outro)
