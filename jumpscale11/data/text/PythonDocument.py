
## COMPLETELY UNFINISHED

class Comment:
    def __init__(self,doc,comment):
        self.doc=doc
        self.indent, self.comment, _ = j.data.text.transform_text(comment, removecomments=False, remove_emptyline=True,findcomments=False)

        self._process()

    def _process(self):
        j.shell()

class CommentBlock(Comment):

    # def __init__(self,doc,block):
    #     Comment.__init__(self,doc,block)

    def _process(self):
        j.shell()


class PythonClass:
    def __init__(self,doc,firstline):
        self.name, self.args = j.data.text.parseDefLine(firstline)
        j.shell()


class PythonMethod:

    def __init__(self,doc,firstline):
        self.abstract = False
        self.name, self.args = j.data.text.parseDefLine(firstline)
        j.shell()

class PythonDocument:
    def __init__(self, text):
        self.text = j.data.text.strip(text)
        self.parts = []



    def _process(self):
        for line in self.text.split("\n"):
            line_strip = line.strip()
            if line_strip=="":
                continue
            elif line.startswith("#"):
