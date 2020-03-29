import time
import re
import socket

# import os
import textwrap
import unicodedata
import math
from unidecode import unidecode

matchquote = re.compile(r"\'[^\']*\'")
matchlist = re.compile(r"\[[^\']*\]")
re_nondigit = re.compile(r"\D")
re_float = re.compile(r"[0-9]*\.[0-9]+")
re_digit = re.compile(r"[0-9]*")
from builtins import str

try:
    import pygments.lexers

    # from pygments.formatters import get_formatter_by_name
    pygmentsObj = True
    import sys
except BaseException:
    pygmentsObj = False

mascot = """
                                                        .,,'
                                                   'c.cool,..',,,,,,,.
                                                  'dxocol:l:;,'......';:,.
                                              .lodoclcccc,...............;:.
                                                ':lc:;;;;;.................:;
            JUMPSCALE                         :oc;'..................,'.....,;
            ---------                        olc'.......'...........,. .,:'..:.
                                            ,oc'......;,',..........od.   'c..'
                                            ;o:......l,   ':........dWkkN. ,;..
                                            .d;.....:K. ;   l'......:KMMM: ''.';'
                                             :,.....cNWNMx  .o.......;OWNc,.....,c
                                              c.....'kMMMX   l.........,,......;'c.
                                             l........xNNx...,. 'coxk;',;;'....;xd.
                                            .l..,...........';;;:dkkc::;;,.....'l'
                                             o'x............lldo,.'o,cl:;'...;,;;
                                           ..;dd'...........':'.,lkkk,.....,.l;l
                                       .',,....'l'.co..;'..........'.....;d,;:
                                    ';;..........;;o:c;,dl;oc,'......';;locc;
                                 ,:;...................;;:',:'',,,,,'.      .,.
                              .::.................................            'c
                            .:,...................................           . .l
                          .:,......................................          'l':
                        .;,.......................................            .l.
                     ';c:.........................................          ;:.';
              ',;::::'...........................................            :d;l;.
           'lolclll,,'..............................','..........            .dccco;
          loooool:,'..............................'l'..........     '.       cocclll..
        .lol:;'...................................::.,,'........    .o     .ldcccccccco:
       ,lcc'.........,;...,;.    ................',c:,''........,.  .o   .;;xccccccccld:
        .';ccc:;;,,'.  ...  ..''..             ;;'...............';.c'.''.  ;loolloooo;
                                ..',,,,,,,''...:o,.................c           ....
                                               .;l.................c.
                                                 ;;;;,'..........,;,
                                                    .':ldddoooddl
"""


class Text:
    @staticmethod
    def unicodedata(text):
        return unicodedata.normalize("NFKD", text.decode("utf-8")).encode("ascii", "ignore")

    @staticmethod
    def strip_to_ascii(text):
        return "".join([char for char in str(text) if ((ord(char) > 31 and ord(char) < 127) or ord(char) == 10)])

    @staticmethod
    def convert_to_snake_case(text):
        converted_string = re.sub("([^/_.])([A-Z][a-z]+)", r"\1_\2", text)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", converted_string).lower()

    @staticmethod
    def strip_to_ascii_dense(text):
        """
        convert to ascii converting as much as possibe to ascii
        replace -,:... to _
        lower the text
        remove all the other parts
        
        """
        text = unidecode(text)  # convert to ascii letters
        # text=Text.strip_to_ascii(text) #happens later already
        text = text.lower()
        text = text.replace("\n", "")
        text = text.replace("\t", "")
        text = text.replace(" ", "")

        def replace(char):
            if char in "-/\\= ;!+()":
                return "_"
            return char

        def check(char):
            charnr = ord(char)
            if char in "._":
                return True
            if charnr > 47 and charnr < 58:
                return True
            if charnr > 96 and charnr < 123:
                return True
            return False

        res = [replace(char) for char in str(text)]
        res = [char for char in res if check(char)]
        text = "".join(res)
        while "__" in text:
            text = text.replace("__", "_")
        text = text.rstrip("_")
        return text

    @staticmethod
    def pad(text, length):
        while len(text) < length:
            text += " "
        return text

    # def stripItems( line, items=["PATH", "\"", " ", "'", ":", "${PATH}", "=", ","]):
    #     def checknow(line, items):
    #         found = False
    #         for item in items:
    #             if line.startswith(item):
    #                 line = line[len(item):]
    #                 found = True
    #             if line.endswith(item):
    #                 line = line[:-len(item)]
    #                 found = True
    #         return found, line
    #
    #     res, line = checknow(line, items)
    #     while res:
    #         res, line = checknow(line, items)
    #     return line

    @staticmethod
    def string_to_version_int(versionStr, minDigits=3):
        """
        convert 3.2.1 to 3002001
        convert 3 to 3000000
        """
        if "." in versionStr:
            splitted = versionStr.split(".")
        else:
            splitted = versionStr.split(",")
        while len(splitted) < minDigits:
            splitted.append("0")
        y = 0
        splitted.reverse()
        x = 0
        for item in splitted:
            y += int(math.pow(1000, x)) * int(splitted[x])
            x += 1
        return y

    @staticmethod
    def byte_to_string(value, codec="utf-8"):
        """
        bytes to string
        """
        if isinstance(value, bytes):
            value = value.decode(codec)
        return value

    @staticmethod
    def string_to_safe_path(txt, maxlen=0):
        """
        process string so it can be used in a path on windows or linux
        """
        txt = Text.toAscii(txt)
        txt = txt.lower().strip().strip(" .-_'")
        txt = (
            txt.replace("/", "")
            .replace(",", " ")
            .replace("*", "")
            .replace("(", "")
            .replace(")", "")
            .replace('"', "")
            .replace("?", "")
            .replace("'", "")
            .replace(":", " ")
        )
        while txt.find("  ") != -1:
            txt = txt.replace("  ", " ")
        if maxlen > 0 and len(txt) > maxlen:
            txt = txt[0:maxlen]
        return txt.strip()

    @staticmethod
    def string_to_ascii(value, maxlen=0):
        value = Text.toStr(value)
        out = ""
        for item in value:
            if ord(item) > 127:
                continue
            out += item
        # out=out.encode('ascii','ignore')
        out = out.replace("\x0b", "")
        out = out.replace("\x0c", "")
        out = out.replace("\r", "")
        out = out.replace("\t", "    ")

        if maxlen > 0 and len(out) > maxlen:
            out = out[0:maxlen]
        # out.decode()
        return out

    @staticmethod
    def text_md5(txt):
        import hashlib

        if isinstance(s, str):
            s = s.encode("utf-8")
        impl = hashlib.new("md5", data=s)
        return impl.hexdigest()

    @staticmethod
    def replace(
        content,
        args=None,
        executor=None,
        ignorecomments=False,
        text_strip=True,
        die_if_args_left=False,
        ignorecolors=False,
        primitives_only=False,
    ):
        """

        j.core.tools.text_replace

        content example:

        "{name!s:>10} {val} {n:<10.2f}"  #floating point rounded to 2 decimals
        format as in str.format_map() function from

        following colors will be replaced e.g. use {RED} to get red color.

        MYCOLORS =
                "RED",
                "BLUE",
                "CYAN",
                "GREEN",
                "YELLOW,
                "RESET",
                "BOLD",
                "REVERSE"

        """

        if isinstance(content, bytes):
            content = content.decode()

        if not isinstance(content, str):
            raise j.exceptions.Input("content needs to be str")

        if args is None:
            args = {}

        if not "{" in content:
            return content

        if executor:
            content2 = j.core.tools.args_replace(
                content,
                # , executor.info.cfg_jumpscale
                args_list=(args, executor.config),
                ignorecolors=ignorecolors,
                die_if_args_left=die_if_args_left,
                primitives_only=primitives_only,
            )
        else:
            content2 = j.core.tools.args_replace(
                content,
                args_list=(args, j.core.myenv.config),
                ignorecolors=ignorecolors,
                die_if_args_left=die_if_args_left,
                primitives_only=primitives_only,
            )

        if text_strip:
            content2 = j.data.text.strip(content2, ignorecomments=ignorecomments, replace=False)

        return content2

    @staticmethod
    def text_strip_to_ascii_dense(text):
        """
        convert to ascii converting as much as possibe to ascii
        replace -,:... to _
        lower the text
        remove all the other parts

        """
        # text = unidecode(text)  # convert to ascii letters
        # text=j.core.tools.strip_to_ascii(text) #happens later already
        text = text.lower()
        text = text.replace("\n", "")
        text = text.replace("\t", "")
        text = text.replace(" ", "")

        def replace(char):
            if char in "-/\\= ;!+()":
                return "_"
            return char

        def check(char):
            charnr = ord(char)
            if char in "._":
                return True
            if charnr > 47 and charnr < 58:
                return True
            if charnr > 96 and charnr < 123:
                return True
            return False

        res = [replace(char) for char in str(text)]
        res = [char for char in res if check(char)]
        text = "".join(res)
        while "__" in text:
            text = text.replace("__", "_")
        text = text.rstrip("_")
        return text

    @staticmethod
    def args_replace(content, args_list=None, primitives_only=False, ignorecolors=False, die_if_args_left=False):
        """

        :param content:
        :param args: add all dicts you want to replace in a list
        :return:
        """

        # IF YOU TOUCH THIS LET KRISTOF KNOW (despiegk)

        assert isinstance(content, str)
        assert args_list

        if content == "":
            return content

        def arg_process(key, val):
            if key in ["self"]:
                return None
            if val is None:
                return ""
            if isinstance(val, str):
                if val.strip().lower() == "none":
                    return None
                return val
            if isinstance(val, bool):
                if val:
                    return "1"
                else:
                    return "0"
            if isinstance(val, int) or isinstance(val, float):
                return val
            if isinstance(val, list) or isinstance(val, set):
                out = "["
                for v in val:
                    if isinstance(v, str):
                        v = "'%s'" % v
                    else:
                        v = str(v)
                    out += "%s," % v
                val = out.rstrip(",") + "]"
                return val
            if primitives_only:
                return None
            else:
                return j.core.tools._data_serializer_safe(val)

        def args_combine():
            args_new = {}
            for replace_args in args_list:
                for key, val in replace_args.items():
                    if key not in args_new:
                        val = arg_process(key, val)
                        if val:
                            args_new[key] = val

            for field_name in j.core.myenv.MYCOLORS:
                if ignorecolors:
                    args_new[field_name] = ""
                else:
                    args_new[field_name] = j.core.myenv.MYCOLORS[field_name]

            return args_new

        def process_line_failback(line):
            args_new = args_combine()
            # SLOW!!!
            # print("FALLBACK REPLACE:%s" % line)
            for arg, val in args_new.items():
                assert arg
                line = line.replace("{%s}" % arg, str(val))
            return line

        def process_line(line):
            if line.find("{") == -1:
                return line
            emptyone = False
            if line.find("{}") != -1:
                emptyone = True
                line = line.replace("{}", ">>EMPTYDICT<<")

            try:
                items = [i for i in j.core.tools.formatter.parse(line)]
            except Exception as e:
                return process_line_failback(line)

            do = {}

            for literal_text, field_name, format_spec, conversion in items:
                if not field_name:
                    continue
                if field_name in j.core.myenv.MYCOLORS:
                    if ignorecolors:
                        do[field_name] = ""
                    else:
                        do[field_name] = j.core.myenv.MYCOLORS[field_name]
                for args in args_list:
                    if field_name in args:
                        do[field_name] = arg_process(field_name, args[field_name])
                if field_name not in do:
                    if die_if_args_left:
                        raise j.exceptions.Input("could not find:%s in line:%s" % (field_name, line))
                    # put back the original
                    if conversion and format_spec:
                        do[field_name] = "{%s!%s:%s}" % (field_name, conversion, format_spec)
                    elif format_spec:
                        do[field_name] = "{%s:%s}" % (field_name, format_spec)
                    elif conversion:
                        do[field_name] = "{%s!%s}" % (field_name, conversion)
                    else:
                        do[field_name] = "{%s}" % (field_name)

            try:
                line = line.format_map(do)
            except KeyError as e:
                # means the format map did not work,lets fall back on something more failsafe
                return process_line_failback(line)
            except ValueError as e:
                # means the format map did not work,lets fall back on something more failsafe
                return process_line_failback(line)
            except Exception as e:
                return line
            if emptyone:
                line = line.replace(">>EMPTYDICT<<", "{}")

            return line

        out = ""
        for line in content.split("\n"):
            if "{" in line:
                line = process_line(line)
            out += "%s\n" % line

        out = out[:-1]  # needs to remove the last one, is because of the split there is no last \n
        return out

    # @staticmethod
    # def indent_find(content):
    #     # find generic prepend for full content
    #     minchars = 9999
    #     assert isinstance(content, str)
    #     for line in content.split("\n"):
    #         if line.strip() == "":
    #             continue
    #         prechars = len(line) - len(line.lstrip())
    #         # print("'%s':%s:%s" % (line, prechars, minchars))
    #         if prechars < minchars:
    #             minchars = prechars
    #     return minchars

    @staticmethod
    def transform_text(
        content, removecomments=False, removefirst_emptyline=False, remove_emptyline=False, findcomments=False
    ):
        """

        will remove indent, will find comments, will remove emptyline

        return indent,content, comments

        comments and content will be stripped with found indent

        """
        minchars = 9999
        assert isinstance(content, str)
        if len(content.strip()) == 0:
            return content
        r = []
        nr = 0
        comments = ""
        for line in content.split("\n"):
            line_ = line.strip()
            if len(line_) == 0:
                if remove_emptyline:
                    continue
                elif nr == 0 and removefirst_emptyline:
                    continue
                else:
                    r.append(line)
            elif line_[0] == "#":
                if findcomments:
                    comments += "%s\n" % line.strip()
                if removecomments:
                    continue
            prechars = len(line) - len(line.lstrip())
            # print("'%s':%s:%s" % (line, prechars, minchars))
            if prechars < minchars:
                minchars = prechars
            r.append(line)

        r = [i[minchars:] for i in r]
        out = "\n".join(r)

        if content[-1] != "\n":
            out.rstrip("\n")

        return minchars, out, comments

    def transform_remove_first_empty_line(self, content):
        # if first line is empty, remove
        lines = content.split("\n")
        if len(lines) > 0:
            if lines[0].strip() == "":
                lines.pop(0)
        content = "\n".join(lines)
        return content

    @staticmethod
    def indent_remove(content, nrchars=0):
        if nrchars > 0:

            # remove the prechars
            content = "\n".join([line[nrchars:] for line in content.split("\n")])
        return content

    @staticmethod
    def indent(content, nspaces=4, wrap=120, strip=True, indentchar=" ", prefix=None, args=None):
        """Indent a string a given number of spaces.

        Parameters
        ----------

        instr : basestring
            The string to be indented.
        nspaces : int (default: 4)
            The number of spaces to be indented.

        Returns
        -------

        str|unicode : string indented by ntabs and nspaces.

        """
        if content is None:
            raise j.exceptions.Base("content cannot be None")
        if content == "":
            return content
        if not prefix:
            prefix = ""
        content = str(content)
        if args is not None:
            content = j.data.text.replace(content, args=args)
        if strip:
            content = j.data.text.strip(content, replace=False)
        if wrap > 0:
            content = j.data.text.wrap(content, wrap)

            # flatten = True
        ind = indentchar * nspaces
        out = ""
        for line in content.split("\n"):
            if line.strip() == "":
                out += "\n"
            else:
                out += "%s%s%s\n" % (ind, prefix, line)
        if content[-1] == "\n":
            out = out[:-1]
        return out

    @staticmethod
    def unicode(value, codec="utf-8"):
        if isinstance(value, str):
            return value.decode(codec)
        elif isinstance(value, str):
            return value
        else:
            return str(value)

    @staticmethod
    def strip(
        content, removecomments=False, args={}, replace=False, executor=None, colors=False, die_if_args_left=False
    ):
        """
        remove all spaces at beginning & end of line when relevant (this to allow easy definition of scripts)
        args will be substitued to .format(...) string function https://docs.python.org/3/library/string.html#formatspec
        j.core.myenv.config will also be given to the format function


        for examples see text_replace method


        """
        indent, out, comments = Text.transform_text(
            content, removecomments=removecomments, remove_emptyline=True, findcomments=False
        )
        if replace:
            content = j.data.text.replace(
                content=content, args=args, executor=executor, text_strip=False, die_if_args_left=die_if_args_left
            )
        else:
            if colors and "{" in content:
                for key, val in j.core.myenv.MYCOLORS.items():
                    content = content.replace("{%s}" % key, val)

        return content

    @staticmethod
    def sort(txt):
        """
        removes all empty lines & does a sort
        """
        return "\n".join([item for item in sorted(txt.split("\n")) if item != ""]) + "\n"

    @staticmethod
    def prefix(prefix, txt):
        out = ""
        txt = txt.rstrip("\n")
        for line in txt.split("\n"):
            out += "%s%s\n" % (prefix, line)
        return out

    @staticmethod
    def wrap(txt, length=120):
        out = ""
        for line in txt.split("\n"):
            out += textwrap.fill(line, length, subsequent_indent="    ") + "\n"
        return out

    @staticmethod
    def prefix_remove(prefix, txt, onlyPrefix=False):
        """
        @param onlyPrefix if True means only when prefix found will be returned, rest discarded
        """
        out = ""
        txt = txt.rstrip("\n")
        l = len(prefix)
        for line in txt.split("\n"):
            if line.find(prefix) == 0:
                out += "%s\n" % (line[l:])
            elif onlyPrefix is False:
                out += "%s\n" % (line)
        return out

    @staticmethod
    def prefix_remove_withtrailing(prefix, txt, onlyPrefix=False):
        """
        there can be chars for prefix (e.g. '< :*: aline'  and this function looking for :*: would still work and ignore '< ')
        @param onlyPrefix if True means only when prefix found will be returned, rest discarded
        """
        out = ""
        txt = txt.rstrip("\n")
        # l = len(prefix)
        for line in txt.split("\n"):
            if line.find(prefix) > -1:
                out += "%s\n" % (line.split(prefix, 1)[1])
            elif onlyPrefix is False:
                out += "%s\n" % (line)
        return out

    @staticmethod
    def numeric_test(txt):
        """
        check if the text can be translated to a numeric int/float
        """
        return re_nondigit.search(txt) is None

    # def lstrip(content):
    #     """
    #     remove all spaces at beginning & end of line when relevant
    #     """
    #     #find generic prepend for full file
    #     minchars=9999
    #     prechars = 0
    #     for line in content.split("\n"):
    #         prechars=len(line)-len(line.lstrip())
    #         if prechars<minchars:
    #             minchars=prechars

    #     if prechars>0:
    #         #remove the prechars
    #         content="\n".join([line[minchars:] for line in content.split("\n")])
    #     return content

    @staticmethod
    def macro_candidates_get(txt):
        """
        look for \{\{\}\} return as list
        """
        result = []
        items = txt.split("{{")
        for item in items:
            if item.find("}}") != -1:
                item = item.split("}}")[0]
                if item not in result:
                    result.append("{{%s}}" % item)
        return result

    @staticmethod
    def _str2var(string):
        """
        try to check int or float or bool
        """
        if not isinstance(string, str):
            string = str(string)
        if string.lower() == "empty":
            return "n", None
        if string.lower() == "none":
            return "n", None
        if string == "":
            return "s", ""
        string2 = string.strip()
        if string2.lower() == "true":
            return "b", True
        if string2.lower() == "false":
            return "b", False
        # check int
        if re_nondigit.search(string2) is None and string2 != "":
            # print "int:'%s'"%string2
            return "i", int(string2)
        # check float
        match = re_float.search(string2)
        if match is not None and match.start() == 0 and match.end() == len(string2):
            return "f", float(string2)

        return "s", Text.machinetext2str(string)

    @staticmethod
    def parse_python_arguments(args):
        """
        @param args e.g.
            msg,f = 'f',g = 1, x=[1,2,3]

        result is dict with key the name, val is the default val
        if empty like for msg then None
        """
        args = args.rstrip("):")
        amMethodArgs = {}
        for arg in args.split(","):
            if "=" in arg:
                argname, default = arg.split("=", 1)
                argname = argname.strip()
                default = default.strip()
                if default[0] == '"':
                    default = default.strip('"')
                elif default[0] == "'":
                    default = default.strip("'")
                elif default == "[]":
                    default = []
                elif default == "{}":
                    default = {}
                elif default[0] in ("[", "{"):
                    default = eval(default)
                elif "." in default:
                    default = float(default)
                else:
                    default = int(default)
            else:
                argname = arg.strip()
                default = None
            amMethodArgs[argname] = default
        return amMethodArgs

    @staticmethod
    def parse_python_method(line, parseArgs=True):
        """
        will return name & args
        args is dict, with support for int, str, list, dict, float

        example line:
            def echo('f',g = 1, x=[1,2,3])
            async def echo('f',g = 1, x=[1,2,3])

        """
        # async = False
        definition = ""
        if line.find("async") == 0:
            # async = True
            line = line[len("async ") :]

        definition, args = line.split("(", 1)
        amName = definition[4:].strip()
        args = args.strip()
        if parseArgs:
            args = Text.parse_python_arguments(args)
        return amName, args

    @staticmethod
    def str2var(string):
        """
        convert list, dict of strings
        or convert 1 string to python objects
        """

        if Text._j.data.types.list.check(string):
            ttypes = []
            for item in string:
                ttype, val = Text._str2var(item)
                if ttype not in ttypes:
                    ttypes.append(ttype)
            if "s" in ttypes:
                result = [str(Text.machinetext2val(item)) for item in string]
            elif "f" in ttypes and "b" not in ttypes:
                result = [Text.getFloat(item) for item in string]
            elif "i" in ttypes and "b" not in ttypes:
                result = [Text.getInt(item) for item in string]
            elif "b" == ttypes:
                result = [Text.getBool(item) for item in string]
            else:
                result = [str(Text.machinetext2val(item)) for item in string]
        elif Text._j.data.types.dict.check(string):
            ttypes = []
            result = {}
            for key, item in list(string.items()):
                ttype, val = Text._str2var(item)
                if ttype not in ttypes:
                    ttypes.append(ttype)
            if "s" in ttypes:
                for key, item in list(string.items()):
                    result[key] = str(Text.machinetext2val(item))
            elif "f" in ttypes and "b" not in ttypes:
                for key, item in list(string.items()):
                    result[key] = Text.getFloat(item)
            elif "i" in ttypes and "b" not in ttypes:
                for key, item in list(string.items()):
                    result[key] = Text.getInt(item)
            elif "b" == ttypes:
                for key, item in list(string.items()):
                    result[key] = Text.getBool(item)
            else:
                for key, item in list(string.items()):
                    result[key] = str(Text.machinetext2val(item))
        elif isinstance(string, str) or isinstance(string, float) or isinstance(string, int):
            ttype, result = Text._str2var(Text._j.core.text.toStr(string))
        else:
            raise Text._j.exceptions.Input(
                "Could not convert '%s' to basetype, input was %s. Expected string, dict or list."
                % (string, type(string)),
                "Text.str2var",
            )
        return result

    @staticmethod
    def eval(code):
        """
        look for {{}} in code and evaluate as python result is converted back to str
        """
        candidates = Text.macro_candidates_get(code)
        for item in candidates:
            if "{{" and "}}" in item:
                item = item.strip("{{").strip("}}")
            try:
                result = eval(item)
            except Exception as e:
                raise Text._j.exceptions.RuntimeError(
                    "Could not execute code in Text._j.core.text.,%s\n%s. Error was:%s" % (item, code, e)
                )
            result = Text.transform_pythonobject_multiline(result, multiline=False).strip()
            code = code.replace(item, result)
        return code

    @staticmethod
    def transform_pythonobject_1line(obj):
        return Text.transform_pythonobject_multiline(obj, False, canBeDict=False)

    @staticmethod
    def transform_pythonobject_multiline(obj, multiline=True, canBeDict=True, partial=False):
        """
        try to convert a python object to string representation works for None, bool, integer, float, dict, list
        """
        if obj is None:
            return ""
        elif isinstance(obj, bytes):
            obj = obj.decode("utf8")
            return obj
        elif Text._j.data.types.bool.check(obj):
            if obj:
                obj = "True"
            else:
                obj = "False"
            return obj
        elif Text._j.data.types.string.check(obj):
            isdict = canBeDict and obj.find(":") != -1
            if obj.strip() == "":
                return ""
            if obj.find("\n") != -1 and multiline:
                obj = "\n%s" % Text.prefix("    ", obj.strip())
            elif not isdict or obj.find(" ") != -1 or obj.find("/") != -1 or obj.find(",") != -1:
                if not partial:
                    obj = "'%s'" % obj.strip("'")
                else:
                    obj = "%s" % obj.strip("'")
            return obj
        elif Text._j.data.types.int.check(obj) or Text._j.data.types.float.check(obj):
            return str(obj)
        elif Text._j.data.types.list.check(obj):
            obj.sort()
            tmp = []
            for item in obj:
                if item is None:
                    continue
                if isinstance(item, str):
                    if item.strip() == "" or item.strip() == "''":
                        continue
                tmp.append(item)
            obj = tmp
            # if not canBeDict:
            #     raise Text._j.exceptions.RuntimeError("subitem cannot be list or dict for:%s"%obj)
            if multiline:
                resout = "\n"
                for item in obj:
                    resout += "    %s,\n" % Text.transform_pythonobject_1line(item)
                resout = resout.rstrip().strip(",") + ",\n"
            else:
                resout = "["
                for item in obj:
                    resout += "%s," % Text.transform_pythonobject_1line(item)
                resout = resout.rstrip().strip(",") + "]"

            return resout

        elif Text._j.data.types.dict.check(obj):
            if not canBeDict:
                raise Text._j.exceptions.RuntimeError("subitem cannot be list or dict for:%s" % obj)
            if multiline:
                resout = "\n"
                keys = sorted(obj.keys())
                for key in keys:
                    val = obj[key]
                    val = Text.transform_pythonobject_1line(val)
                    # resout+="%s:%s, "%(key,val)
                    resout += "    %s:%s,\n" % (key, Text.transform_pythonobject_1line(val))
                resout = resout.rstrip().rstrip(",") + ",\n"
            else:
                resout = ""
                keys = sorted(obj.keys())
                for key in keys:
                    val = obj[key]
                    val = Text.transform_pythonobject_1line(val)
                    resout += "%s:%s," % (key, val)
                resout = resout.rstrip().rstrip(",") + ","
            return resout

        else:
            raise Text._j.exceptions.RuntimeError("Could not convert %s to string" % obj)

    @staticmethod
    def transform_quotes(value, replacewith):
        for item in re.findall(matchquote, value):
            value = value.replace(item, replacewith)
        return value

    # def machinetext2val( value):
    #     """
    #     do reverse of:
    #          SPACE -> \\S
    #          " -> \\Q
    #          , -> \\K
    #          : -> \\D
    #          \\n -> return
    #     """
    #     # value=value.strip("'")
    #     value2 = value.replace("\\K", ",")
    #     value2 = value2.replace("\\Q", '"')
    #     value2 = value2.replace("\\S", " ")
    #     value2 = value2.replace("\\D", ":")
    #     value2 = value2.replace("\\N", "\n")
    #     value2 = value2.replace("\\n", "\n")
    #     # change = False
    #     # if value != value2:
    #     #     change = True
    #     if value2.strip() == "":
    #         return value2
    #     if value2.strip().strip("'").startswith("[") and value2.strip().strip("'").endswith("]"):
    #         value2 = value2.strip().strip("'").strip("[]")
    #         res = []
    #         for item in value2.split(","):
    #             if item.strip() == "":
    #                 continue
    #             if Text.isInt(item):
    #                 item = Text.getInt(item)
    #             elif Text.isFloat(item):
    #                 item = Text.getFloat(item)
    #             res.append(item)
    #         return res
    #
    #         # Check if it's not an ip address
    #         # because int/float test fails on "1.1.1.1" for example
    #         try:
    #             socket.inet_aton(value2)
    #         except socket.error:
    #             if Text.isInt(value2):
    #                 return Text.getInt(value2)
    #             elif Text.isFloat(value2):
    #                 return Text.getFloat(value2)
    #     # value2=value2.replace("\n","\\n")
    #     return value2
    #
    # def machinetext2str( value):
    #     """
    #     do reverse of:
    #          SPACE -> \\S
    #          " -> \\Q
    #          , -> \\K
    #          : -> \\D
    #          \n -> \\N
    #     """
    #     value = value.replace("\\K", ",")
    #     value = value.replace("\\Q", '"')
    #     value = value.replace("\\S", " ")
    #     value = value.replace("\\D", ":")
    #     value = value.replace("\\N", "\n")
    #     value = value.replace("\\n", "\n")
    #     return value
    #
    # def getInt( text):
    #     if Text._j.data.types.string.check(text):
    #         text = Text.strip(text).strip("'\"").strip()
    #         if text.lower() == "none":
    #             return 0
    #         elif text is None:
    #             return 0
    #         elif text == "":
    #             return 0
    #         else:
    #             text = int(text)
    #     else:
    #         text = int(text)
    #     return text
    #
    # def getFloat( text):
    #     if Text._j.data.types.string.check(text):
    #         text = text.strip()
    #         if text.lower() == "none":
    #             return 0.0
    #         elif text is None:
    #             return 0.0
    #         elif text == "":
    #             return 0.0
    #         else:
    #             text = float(text)
    #     else:
    #         text = float(text)
    #     return text
    #
    # def isFloat( text):
    #     text = Text.strip(",").strip()
    #     if not text.find(".") == 1:
    #         return False
    #     try:
    #         float(text)
    #         return True
    #     except ValueError:
    #         return False
    #
    # def isInt( text):
    #     text = Text.strip(",").strip()
    #     return text.isdigit()
    #
    # def getBool( text):
    #     if Text._j.data.types.bool.check(text):
    #         return text
    #     elif Text._j.data.types.int.check(text):
    #         if text == 1:
    #             return True
    #         else:
    #             return False
    #     elif Text._j.data.types.string.check(text):
    #         text = text.strip()
    #         if text.lower() == "none":
    #             return False
    #         elif text is None:
    #             return False
    #         elif text == "":
    #             return False
    #         elif text.lower() == "true":
    #             return True
    #         elif text == "1":
    #             return True
    #         else:
    #             return False
    #     else:
    #         raise Text._j.exceptions.RuntimeError("input needs to be None, string, bool or int")
    #
    # # def _dealWithQuote( text):
    # #     """
    # #     look for 'something,else' the comma needs to be converted to \k
    # #     """
    # #     for item in re.findall(matchquote, text):
    # #         text = text.replace(item, item)
    # #     return text
    # #
    # # def _dealWithList( text):
    # #     """
    # #     look for [something,2] the comma needs to be converted to \k
    # #     """
    # #     for item in re.findall(matchlist, text):
    # #         item2 = item.replace(",", "\\K")
    # #         text = text.replace(item, item2)
    # #     return text
    #
    # def getList( text, ttype=None):
    #     """
    #     @type can be int,bool or float (otherwise its always str)
    #     """
    #
    #     # if already list just return
    #     if Text._j.data.types.list.check(text):
    #         return text
    #
    #     if text is None:
    #         return []
    #
    #     if not Text._j.data.types.string.check(text):
    #         raise j.exceptions.Base("need to be string:%s" % text)
    #
    #     text = text.strip(" [")
    #     text = text.strip(" ]")
    #
    #     text = text.strip('"').strip()
    #
    #     if Text.strip(text) == "":
    #         return []
    #
    #     # text = Text._dealWithQuote(text)  # to get ',' in '' not counting
    #     if "," in text:
    #         text = text.split(",")
    #         text = [item.strip().strip("'").strip() for item in text if item.strip().strip("'").strip() is not ""]
    #     elif "\n" in text:
    #         text = text.split("\n")
    #         text = [item.strip().strip("'").strip() for item in text if item.strip().strip("'").strip() is not ""]
    #     else:
    #         text = [text]
    #
    #     if ttype is not None:
    #         ttype = Text._j.data.types.get(ttype)
    #     else:
    #         ttype = Text._j.data.types.string
    #
    #     res = []
    #     for item in text:
    #         item = ttype.clean(item)
    #         if item not in res:
    #             res.append(item)
    #     return res
    #
    # def getDict( text, ttype=None):
    #     """
    #     keys are always treated as string
    #     @type can be int,bool or float (otherwise its always str)
    #     """
    #     if Text.strip() == "" or Text.strip() == "{}":
    #         return {}
    #     # text = Text._dealWithList(text)
    #     # text = Text._dealWithQuote(text)
    #     res2 = {}
    #     for item in Text.split(","):
    #         if item.strip() != "":
    #             if item.find(":") == -1:
    #                 raise Text._j.exceptions.RuntimeError("Could not find : in %s, cannot get dict out of it." % text)
    #
    #             key, val = item.split(":", 1)
    #             if val.find("[") != -1:
    #                 val = Text.machinetext2val(val)
    #             else:
    #                 # val = val.replace("\k", ",")
    #                 key = key.strip()
    #                 val = val.strip()
    #             res2[key] = val
    #     return res2

    def print(text, style="vim", lexer="bash"):
        """

        :param text:
        :param style: vim
        :param lexer: py3 or bash
        :return:
        """
        text = Text.strip(text)
        formatter = pygments.formatters.Terminal256Formatter(style=pygments.styles.get_style_by_name(style))

        lexer = pygments.lexers.get_lexer_by_name(lexer)  # , stripall=True)
        colored = pygments.highlight(text, lexer, formatter)
        sys.stdout.write(colored)

