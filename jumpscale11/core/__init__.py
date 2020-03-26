from .Exceptions import JSExceptions


class JumpscaleCore:
    __myenv = None
    __tools = None
    __docker = None
    __codetools = None

    @property
    def myenv(self):
        if self.__class__.__myenv is None:
            from jumpscale11.core.MyEnv import MyEnv

            self.__class__.__myenv = MyEnv(j=self._j)
            self.__class__.__myenv.__tools = self.tools
            self.__class__.__myenv.init()
        return self.__class__.__myenv

    exceptions = JSExceptions

    @property
    def tools(self):
        if self.__class__.__tools is None:
            from jumpscale11.core.Tools import Tools

            self.__class__.__tools = Tools
            self.__class__.__tools._j = self._j
            self.__class__.__tools.__myenv = self.myenv
        return self.__class__.__tools

    @property
    def docker(self):
        if self.__class__.__docker is None:
            from jumpscale11.core.DockerFactory import DockerFactory

            self.__class__.__docker = DockerFactory
            self.__class__.__docker._j = self._j
        return self.__class__.__docker

    @property
    def codetools(self):
        if self.__class__.__codetools is None:
            from jumpscale11.core.CodeTools import CodeTools

            self.__class__.__codetools = CodeTools(self._j)
        return self.__class__.__codetools
