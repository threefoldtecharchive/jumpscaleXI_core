class BaseJSException(Exception):
    """
    ## log (exception) levels

        - CRITICAL 	50
        - ERROR 	40
        - WARNING 	30
        - INFO 	    20
        - STDOUT 	15
        - DEBUG 	10

    exception is the exception which comes from e.g. a try except, its to log the original exception

    e.g.

    try:
        dosomething_which_gives_error(data=data)
    except Exception as e:
        raise j.exceptions.Value("incredible error",cat="firebrigade.ghent",data=data,exception=e)

    :param: message a meaningful message
    :level: see above
    :cat: dot notation can be used, just to put your error in a good category
    :context: e.g. methodname, location id, ... the context (area) where the error happened (exception)
    :data: any data worth keeping


    """

    def __init__(self, message="", level=None, cat=None, msgpub=None, context=None, data=None, exception=None):

        super().__init__(message)

        # exc_type, exc_value, exc_traceback = sys.exc_info()
        # _exc_traceback = exc_traceback
        # _exc_value = exc_value
        # _exc_type = exc_type

        if level:
            if isinstance(level, str):
                level = int(level)

            elif isinstance(level, int):
                pass
            else:
                raise JSBUG("level needs to be int or str", data=locals())
            assert level > 9
            assert level < 51

        self.message = message
        self.message_pub = msgpub
        self.level = level
        self.context = context
        self.cat = cat  # is a dot notation category, to make simple no more tags
        self.data = data
        self._logdict = None
        self.exception = exception
        self._init(message=message, level=level, cat=cat, msgpub=msgpub, context=context, exception=exception)

    def _init(self, **kwargs):
        pass

    @property
    def logdict(self):
        return self._logdict

    @property
    def type(self):
        return str(__class__).lower()

    @property
    def str_1_line(self):
        """
        1 line representation of exception

        """
        msg = ""
        if self.level:
            msg += "level:%s " % self.level
        msg += "type:%s " % type
        # if _tags_add != "":
        #     msg += " %s " % _tags_add
        return msg.strip()

    def __str__(self):
        return self.str_1_line

    __repr__ = __str__

    # def __repr__(self):
    #     if not self.logdict:
    #         raise JSBUG("logdict not known (is None)")
    #     print(j.core.tools.log2str(logdict))
    #     return ""


class Permission1(BaseJSException):
    pass


class Halt1(BaseJSException):
    pass


class RuntimeError1(BaseJSException):
    pass


class Input1(BaseJSException):
    pass


class Value1(BaseJSException):
    pass


class NotImplemented1(BaseJSException):
    pass


class BUG1(BaseJSException):
    pass


class JSBUG1(BaseJSException):
    pass


class Operations1(BaseJSException):
    pass


class IO1(BaseJSException):
    pass


class NotFound1(BaseJSException):
    pass


class Timeout1(BaseJSException):
    pass


class SSHError1(BaseJSException):
    pass


class SSHTimeout1(BaseJSException):
    pass


class RemoteException1(BaseJSException):
    pass


class JSExceptions:

    Permission = Permission1
    SSHTimeout = SSHTimeout1
    SSHError = SSHError1
    Timeout = Timeout1
    NotFound = NotFound1
    IO = IO1
    Operations = Operations1
    JSBUG = JSBUG1
    BUG = BUG1
    NotImplemented = NotImplemented1
    Input = Input1
    Value = Value1
    RuntimeError = RuntimeError1
    Runtime = RuntimeError1
    Halt = Halt1
    Base = BaseJSException
    RemoteException = RemoteException1

