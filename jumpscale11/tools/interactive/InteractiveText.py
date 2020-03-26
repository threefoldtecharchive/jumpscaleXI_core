class InteractiveText:
    @staticmethod
    def ask(chatbot, content, name=None, args={}, ask=True):
        """
        look for @ASK statements in text, where found replace with input from user

        syntax for ask is:
            @ASK name:aname type:str descr:adescr default:adefault regex:aregex retry:10 minValue:10 maxValue:20 dropdownvals:1,2,3

            descr, default & regex can be between '' if spaces inside

            types are: str,float,int,bool,multiline,list

            retry means will keep on retrying x times until ask is done properly

            dropdownvals is comma separated list of values to ask for

        @ASK can be at any position in the text

        @return type,content

        """
        content = self.eval(content)
        if content.strip() == "":
            return None, content

        # endlf = content[-1] == "\n"
        ttype = None

        out = ""
        for line in content.split("\n"):

            # print ("ask:%s"%line)

            if line.find("@ASK") == -1 or not ask:
                out += "%s\n" % line
                continue

            result = "ERROR:UNKNOWN VAL FROM ASK"

            prefix, end = line.split("@ASK", 1)
            tags = self._j.data.tags.getObject(end.strip())

            if tags.tagExists("name"):
                name = tags.tagGet("name")
            else:
                if name is None:
                    if line.find("=") != -1:
                        name = line.split("=")[0].strip()
                    else:
                        name = ""

            if name in args:
                result = args[name]
                out += "%s%s\n" % (prefix, result)
                continue

            if name in args:
                result = args[name]
                out += "%s%s\n" % (prefix, result)
                continue

            if tags.tagExists("type"):
                ttype = tags.tagGet("type").strip().lower()
                if ttype == "string":
                    ttype = "str"
            else:
                ttype = "str"
            if tags.tagExists("descr"):
                descr = tags.tagGet("descr")
            else:
                if name != "":
                    descr = "Please provide value for %s of type %s" % (name, ttype)
                else:
                    descr = "Please provide value"

            # name=name.replace("__"," ")

            descr = descr.replace("__", " ")
            descr = descr.replace("\\n", "\n")

            if tags.tagExists("default"):
                default = tags.tagGet("default")
            else:
                default = ""

            if tags.tagExists("retry"):
                retry = int(tags.tagGet("retry"))
            else:
                retry = -1

            if tags.tagExists("regex"):
                regex = tags.tagGet("regex")
            else:
                regex = None

            if len(descr) > 30 and ttype not in ("dict", "multiline"):
                self._log_info(descr)
                descr = ""

            # print "type:'%s'"%ttype
            if ttype == "str":
                result = j.tools.console.askString(question=descr, defaultparam=default, regex=regex, retry=retry)

            elif ttype == "password":
                result = j.tools.console.askPassword(question=descr, confirm=False)

            elif ttype == "list":
                result = self._j.tools.console.askString(question=descr, defaultparam=default, regex=regex, retry=retry)

            elif ttype == "multiline":
                result = self._j.tools.console.askMultiline(question=descr)

            elif ttype == "float":
                result = self._j.tools.console.askString(question=descr, defaultparam=default, regex=None)
                # check getFloat
                try:
                    result = float(result)
                except BaseException:
                    raise self._j.exceptions.Input("Please provide float.", "system.self.ask.neededfloat")
                result = str(result)

            elif ttype == "int":
                if tags.tagExists("minValue"):
                    minValue = int(tags.tagGet("minValue"))
                else:
                    minValue = None

                if tags.tagExists("maxValue"):
                    maxValue = int(tags.tagGet("maxValue"))
                else:
                    maxValue = None

                if not default:
                    default = None
                result = self._j.tools.console.askInteger(
                    question=descr, defaultValue=default, minValue=minValue, maxValue=maxValue, retry=retry
                )

            elif ttype == "bool":
                if descr != "":
                    self._log_info(descr)
                result = self._j.tools.console.askYesNo()
                if result:
                    result = True
                else:
                    result = False

            elif ttype == "dropdown":
                if tags.tagExists("dropdownvals"):
                    dropdownvals = tags.tagGet("dropdownvals")
                else:
                    raise self._j.exceptions.Input(
                        "When type is dropdown in ask, then dropdownvals needs to be specified as well."
                    )
                choicearray = [item.strip() for item in dropdownvals.split(",")]
                result = self._j.tools.console.askChoice(choicearray, descr=descr, sort=True)
            elif ttype == "dict":
                rawresult = self._j.tools.console.askMultiline(question=descr)
                result = "\n"
                for line in rawresult.splitlines():
                    result += "    %s,\n" % line.strip().strip(",")

            else:
                raise self._j.exceptions.Input(
                    "Input type:%s is invalid (only: bool,int,str,string,dropdown,list,dict,float)" % ttype
                )

            out += "%s%s\n" % (prefix, result)

        # if endlf==False:
        out = out[:-1]
        return ttype, out
