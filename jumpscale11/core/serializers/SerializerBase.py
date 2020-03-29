from Jumpscale import j


class SerializerBase:
    def dump(self, filepath, obj):
        data = self.dumps(obj)
        j.sal.fs.file_write(filepath, data)

    def load(self, path):
        b = j.sal.fs.file_read(path, binary=True)
        try:
            r = self.loads(b)
        except Exception as e:
            error = "error:%s\n" % e
            error += "\could not parse:\n%s\n" % b
            error += "\npath:%s\n" % path
            raise j.exceptions.Input(message=error)
        return r

