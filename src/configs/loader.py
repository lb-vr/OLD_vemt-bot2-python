import dataclasses

from typing import Any, Type, Dict, Union
from datetime import datetime


@dataclasses.dataclass
class _ConfigBase:
    _optionals: dict = dataclasses.field(init=False, default_factory=dict)


def __parse(name, value, excepted_types: list) -> Any:
    assert type(excepted_types) is list, "invalid args: excepted_types={}".format(excepted_types)

    dtcls: list = [p for p in excepted_types if dataclasses.is_dataclass(p)]
    typings: list = [p for p in excepted_types if hasattr(p, "_name")]

    if value is None and type(None) in excepted_types:
        # 許されたNone
        return value

    elif dtcls:
        # dataclassを要求されたため再帰
        return parseConfigFromJson(value, dtcls[0])

    elif datetime in excepted_types:
        # 書式化された日時
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            if str not in excepted_types:
                raise e  # 文字列ではない場合は日時のエラーを投げる

    elif typings:
        # typingヒンティングされているもの
        for t in typings:
            if t._name == "List" and type(value) is list:
                retlist: list = []
                arg = [t.__args__[0]]
                for vitem in value:
                    retlist.append(__parse(name, vitem, arg))
                return retlist

            elif t._name == "Dict" and type(value) is dict:
                retdict: dict = {}
                arg = t.__args__[0:1]
                for kitem, vitem in value:
                    if type(kitem) is arg[0]:
                        retdict[kitem] = __parse(name, vitem, arg[1])
                return retdict

            elif t._name not in ("List", "Dict"):
                raise NotImplementedError("{} is not supported.".format(str(t._name)))

    if type(value) not in excepted_types:
        raise TypeError(
            "Mismatched type. name={}, type={}, except={}".format(
                name, type(value), excepted_types), name, value)
    return value


def parseConfigFromJson(json_dict: dict, target: Type) -> Any:
    """
    jsonで記述された設定ファイルから、データクラスへ読み込むローダー関数
    """
    assert type(json_dict) is dict, "invalid argument: json_dict={}".format(json_dict)
    assert dataclasses.is_dataclass(target), "invalid argument: target must be dataclass."

    # fieldsからdictを作る
    fields: Dict[str, dataclasses.Field] = {}
    _fields = dataclasses.fields(target)
    for f in _fields:
        assert type(f) is dataclasses.Field, "invalid field."
        fields[f.name] = f

    # 初期化用のdict
    values: dict = {}
    optionals: dict = {}

    # json側をループ
    for k, v in json_dict.items():
        if k in fields:  # fieldsに存在する
            field: dataclasses.Field = fields[k]
            # Union展開とdataclassの抽出
            types: list = [field.type]
            if hasattr(field.type, "__args__") and hasattr(field.type, "__origin__"):
                if field.type.__origin__ == Union:
                    types = list(field.type.__args__)
                else:
                    assert field.type._name is not None, "unexcepted _name: {}".format(field.type._name)
            values[k] = __parse(k, v, types)
        else:
            # fieldsに存在しない
            optionals[k] = v

    ret = target(**values)
    ret._optionals = optionals
    return ret
