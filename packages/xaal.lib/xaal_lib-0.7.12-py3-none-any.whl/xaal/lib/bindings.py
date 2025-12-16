import uuid

from .exceptions import UUIDError


class UUID:
    def __init__(self, *args, **kwargs):
        self.__uuid = uuid.UUID(*args, **kwargs)

    @staticmethod
    def random_base(digit=2) -> 'UUID':
        """zeros the last digits of a random uuid, usefull w/ you want to forge some addresses
        two digit is great.
        """
        if (digit > 0) and (digit < 13):
            tmp = str(uuid.uuid1())
            st = "%s%s" % (tmp[:-digit], '0' * digit)
            return UUID(st)
        else:
            raise UUIDError

    @staticmethod
    def random() -> 'UUID':
        tmp = uuid.uuid1().int
        return UUID(int=tmp)

    def __add__(self, value: int) -> 'UUID':
        tmp = self.__uuid.int + value
        return UUID(int=tmp)

    def __sub__(self, value: int) -> 'UUID':
        tmp = self.__uuid.int - value
        return UUID(int=tmp)

    def __eq__(self, value) -> bool:
        return self.__uuid == value

    def __lt__(self, value) -> bool:
        return self.__uuid.int < value

    def __gt__(self, value) -> bool:
        return self.__uuid.int > value

    def __str__(self) -> str:
        return str(self.__uuid)

    def __repr__(self) -> str:  # pragma: no cover
        return f"UUID('{self.__uuid}')"

    def __hash__(self) -> int:
        return self.__uuid.__hash__()

    def get(self) -> uuid.UUID:
        return self.__uuid

    def set(self, value: uuid.UUID):
        self.__uuid = value

    @property
    def str(self) -> str:
        return str(self)

    @property
    def bytes(self) -> bytes:
        return self.__uuid.bytes


class URL:
    def __init__(self, value):
        self.__url = value

    def __eq__(self, value):
        return self.__url == value

    def __str__(self):
        return str(self.__url)

    def __repr__(self) -> str:  # pragma: no cover
        return f"URL('{self.__url}')"

    def set(self, value: str):
        self.__url = value

    def get(self) -> str:
        return self.__url

    @property
    def str(self):
        return str(self)

    @property
    def bytes(self):
        return self.__url


classes = [UUID, URL]
