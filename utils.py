class EqualByAttributes(object):
    def __eq__(self, outro):
        return self.__dict__ == outro.__dict__
