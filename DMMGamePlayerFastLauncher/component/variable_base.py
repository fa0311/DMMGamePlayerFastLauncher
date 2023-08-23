from tkinter import Variable


class VariableBase:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_dict(self) -> dict[str, str]:
        return {k: v.get() if isinstance(v, Variable) else v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, obj: dict[str, str]):
        item = [(k, v(value=obj.get(k))) for k, v in cls.__annotations__.items()]
        return cls(**dict(item))
