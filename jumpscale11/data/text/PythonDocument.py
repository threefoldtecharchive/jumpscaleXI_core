
## COMPLETELY UNFINISHED

class DocBase()

class Comment:
    def __init__(self,doc,comment,parent=None):
        self.doc=doc
        self.indent, self.comment, _ = j.data.text.transform_text(comment, removecomments=False, remove_emptyline=True,findcomments=False)
        self.parent=parent
        self._process()

    def _process(self):
        j.shell()

class CommentBlock(Comment):

    # def __init__(self,doc,block):
    #     Comment.__init__(self,doc,block)

    def _process(self):
        j.shell()


class PythonClass:
    def __init__(self,doc,firstline,parent=None):
        self.name, self.args = j.data.text.parse_python_method(firstline)
        self.parts = []
        self.parent=parent
        j.shell()


class PythonMethod:

    def __init__(self,doc,firstline,parent=None):
        self.abstract = False
        self.name, self.args = j.data.text.parse_python_method(firstline)
        self.parts = []
        self.parent = parent
        j.shell()

class PythonDocument:
    def __init__(self, text):
        self.text = j.data.text.strip(text)
        self.parts = []



    def _process(self):
        lastpart = None
        for line in self.text.split("\n"):
            line_strip = line.strip()
            if line_strip=="":
                continue
            elif line_strip.startswith("#"):
                lastpart=Comment(self,line)
            elif line_strip.startswith("'''") or line_strip.startswith("\"\"\"") or line_strip.startswith("```"):
                lastpart = CommentBlock(self, line)
            elif line_strip.startswith("class"):
                lastpart = PythonClass(self, line)
            elif isinstance(PythonClass,lastpart):
                j.shell()
            elif isinstance(PythonMethod,lastpart):
                j.shell()

