import os
import string
import jinja2


class ClassDef:
    def __init__(self):
        self.name_real = None
        self.name = None
        self.static = True  # if yes then use as class only, no instance, otherwise True then make object out of it


class FileDef:
    def __init__(self, path):
        self.path = path
        self.class_defs = []


class CodeTools:
    def __init__(self, j):
        self._j = j

    def _log(self, msg):
        print(" - %s" % msg)

    def init_generate(self, path=None):
        if not path:
            path = os.getcwd()
        prevline = ""

        def init_write(path):
            C_init = """

            class {modulename}:
                {{repeat:classdefs}}
                __myenv = None
                __tools = None
                __docker = None
                __codetools = None

            {{#filedef.class_defs}}
            @property
            def {classdef.name}(self):
                if self.__class__.__@classdef.name is None:
                    from jumpscale11.core.MyEnv import MyEnv        
                    self.__class__.__@classdef.name = @{classdef.name_real}()
                return self.__class__.__@{classdef.name}             
            }
            {{/repo}}

            """

        def file_parse(path):
            fd = FileDef(path=path)
            content = self._j.core.tools.file_read(path).decode()
            classdef = None
            for line in content.split("\n"):
                if line.strip() == "":
                    continue
                elif line.startswith("class "):
                    if classdef:
                        if classdef.name:
                            fd.class_defs.append(classdef)
                    line1 = line.split("class", 1)[1].strip()
                    class_name_real = line1.split("(", 1)[0].strip()
                    classdef = ClassDef()
                    classdef.name_real = class_name_real
                elif classdef and line.strip().startswith("__name"):
                    classdef.name = line.split("=", 1)[1].strip().lower()
                elif classdef and line.strip().startswith("def "):
                    # we found a def, if staticmethod not in previous line then the class needs to be instantiated
                    if not prevline.strip().startswith("@staticmethod"):
                        classdef.static = False

                # if classdef:
                #     if "yaml" in classdef.name_real.lower():
                #         self._log(line)
                #         self._log(f"{classdef.name_real}:{classdef.name}")

                prevline = line

            if classdef:
                if classdef.name:
                    fd.class_defs.append(classdef)

            return fd

        res = []

        # r=root, d=directories, f = files
        for r, d, f in os.walk(path):
            for file in f:
                if file.endswith(".py"):
                    file_path = os.path.join(r, file)
                    fd = file_parse(file_path)
                    if fd.class_defs != []:
                        res.append(fd)

        for fd in res:
            if len(fd.class_defs) != 1:
                raise self._j.tools.exceptions.Input("should only be one class with __name in %s" % fd.path)

            self._j.shell()
            w
