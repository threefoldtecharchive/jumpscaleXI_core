import json

try:
    import msgpack
except:
    msgpack = None

try:
    import ujson as ujson
except BaseException:
    import json as ujson


try:
    import yaml

    def serializer(data):
        if isinstance(data, bytes):
            return "BINARY"
        if hasattr(data, "_ddict"):
            data = data._ddict
        try:
            data = yaml.dump(data, default_flow_style=False, default_style="", indent=4, line_break="\n")
        except Exception as e:
            # print("WARNING: COULD NOT YAML SERIALIZE")
            # return str(data)
            data = "CANNOT SERIALIZE YAML"
        return data


except:
    try:

        def serializer(data):
            if hasattr(data, "_data"):
                return str(data._data)
            if hasattr(data, "_ddict"):
                data = data._ddict
            try:
                return ujson.dumps(data, ensure_ascii=False, sort_keys=True, indent=True)
            except Exception as e:
                # data = str(data)
                data = "CANNOT SERIALIZE"
                return data

    except:

        def serializer(data):
            raise RuntimeError("cannot serialize, serializer not found")
