class dotdict(dict):
	def __getattr__(self, attr):
		return self.get(attr, None)
	__setattr__ = dict.__setitem__
	__delattr__ = dict.__delitem__

class EqualByAttributes(object):
    def __eq__(self, outro):
        return self.__dict__ == outro.__dict__
