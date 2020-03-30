import enum


class Hoge(enum.Enum):
    kAAA = "aaa"


print(str(Hoge.kAAA.value))
