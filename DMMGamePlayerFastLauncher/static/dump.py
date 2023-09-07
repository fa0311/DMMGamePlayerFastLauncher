class Dump:
    @classmethod
    def dump(cls):
        item = [(k, v) for k, v in cls.__dict__.items() if not k.startswith("__") and not isinstance(v, classmethod)]
        return dict(item)
