from datetime import datetime
from json import dumps


class Datum(list):
    _name: str
    _parent: 'Datum'
    _value: float | int | str | datetime | None = None

    def __init__(self, name: str, parent: 'Datum' = None, value: float | int | str | datetime | None = None):
        super().__init__()
        self._name = name
        self._parent = parent
        self._value = value

    def __repr__(self):
        return self._name

    def __str__(self):
        return dumps(self._dict)

    @property
    def _dict(self):
        return {k: v for k, v in self.__dict__ if not k.startswith('_')}

    @property
    def n(self) -> int:
        fields = [i for i in self.__dict__ if not i.startswith('_')]
        return len(fields) + len(self)

    @property
    def is_terminal(self) -> bool:
        return self.n == 0

    def add_child(self, _type: str, value: float | int | str | datetime | None = None):
        d = Datum(_type, parent=self, value=value)
        self.__dict__[_type] = d

        return d

    def union_child(self, child):
        if type(child) is Datum:
            if not child.is_terminal:
                self.__dict__[child.d_name] = child
                child._parent = self
            else:
                self.__dict__[child.d_name] = child.d_value

    @property
    def d_value(self):
        return self._value

    @d_value.setter
    def d_value(self, value):
        self._value = value

    @property
    def d_name(self) -> str:
        return self._name

    @d_name.setter
    def d_name(self, value: str):
        self._name = value


def helper(item: any, name: str) -> Datum:
    d = Datum(name=name)
    if isinstance(item, dict):
        for k, v in item.items():
            child = helper(v, k)
            d.union_child(child)
        return d

    if isinstance(item, list):
        for i, v in enumerate(item):
            child = helper(v, f'{name} list - {i}')
            d.append(child)
        return d

    d.d_value = item
    return d


def construct(_dict: dict) -> Datum:
    return helper(_dict, 'data')
