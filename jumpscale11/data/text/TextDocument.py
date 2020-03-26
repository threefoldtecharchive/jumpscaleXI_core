# need better specs before we can implement this, is more not too loose the code


class Document:
    def add_cmd_out(self, out, entity, cmd):
        out += "!%s.%s\n" % (entity, cmd)
        return out

    def add_time_hr(self, line, epoch, start=50):
        if int(epoch) == 0:
            return line
        while len(line) < start:
            line += " "
        line += "# " + time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(int(epoch)))
        return line

    def add_val(self, out, name, val, addtimehr=False):
        if isinstance(val, int):
            val = str(val)
        while len(val) > 0 and val[-1] == "\n":
            val = val[:-1]
        if len(val.split("\n")) > 1:
            out += "%s=...\n" % (name)
            for item in val.split("\n"):
                out += "%s\n" % (item)
            out += "...\n"
        else:
            line = "%s=%s" % (name, val)
            if addtimehr:
                line = self.addTimeHR(line, val)
            out += "%s\n" % line
        return out
