from typing import List


class Safe:
    class Meta:
        include: List[str] | str = "__all__"
        exclude: List[str] = []


class Ram(Safe):
    id = "id"
    total_mb = "total_mb"
    free_mb = "free_mb"
    used_mb = "used_mb"
    timestamp = "timestamp"
    device = "device"

    class Meta:
        exclude = ["device", "used_mb"]


class Device:
    internal = 1
    external = 2


class Sort:
    DESC = "DESC"
    ASC = "ASC"


def safe(cls: type) -> list[str]:
    data = [
        variable
        for variable in cls.__dict__
        if (
            not variable.startswith("__")
            and not variable.endswith("__")
            and not variable == "Meta"
        )
    ]
    out = []
    if hasattr(cls, "Meta"):
        if hasattr(cls.Meta, "include"):
            if cls.Meta.include == "__all__":
                return data
            for variable in data:
                if variable in cls.Meta.include:
                    out.append(variable)
            return out
        if hasattr(cls.Meta, "exclude"):
            for variable in cls.Meta.exclude:
                data.remove(variable)
    return data
