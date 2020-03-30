import enum


class Phase(enum.IntEnum):
    kEntry = 1,
    kAttend = 2,
    kSubmit = 3,
    kFinished = 4

    @classmethod
    def getFromInt(cls, value: int):
        assert type(value) is int
        assert 1 <= value <= 4

        for m in Phase.__members__.values():
            if m.value == value:
                return m
        raise ValueError("value={} is not a member of Phase.".format(value))
