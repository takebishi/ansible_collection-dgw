from __future__ import absolute_import, division, print_function
__metaclass__ = type


def find_object(keys, obj):
    # 指定の階層のJSONオブジェクトを取得
    for key in keys:
        # リストの場合は指定のキーの要素を取得
        if isinstance(obj, list):
            foundname = False
            for item in obj:
                if "name" in item:
                    if item["name"] == key:
                        obj = item
                        foundname = True
                        break
                elif "setting" in item:
                    # "name": <設定名>のキー＆値がなかった
                    # setting内のname設定から探す
                    for s in item["setting"]:
                        if not ("name" in s) or not ("value" in s):
                            continue
                        if s["name"] == "name" and s["value"] == key:
                            obj = item
                            foundname = True
                            break
                    if foundname:
                        break

            if not foundname:
                raise DgwUtilError(f"Cannot find parameter key :'{key}'")
        else:
            if not (key in obj):
                raise DgwUtilError(f"Cannot find parameter key :'{key}'")
            obj = obj[key]

    return obj


class DgwUtilError(Exception):
    pass
