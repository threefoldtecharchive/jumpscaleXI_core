import sys
import os
from .Exceptions import JSExceptions
import traceback

DEFAULT_BRANCH = "unstable"
from .RedisTools import RedisTools


class MyEnv:
    def __init__(self, j):
        """

        :param configdir: default /sandbox/cfg, then ~/sandbox/cfg if not exists
        :return:
        """
        self._j = j
        self._redis_active = False
        self.DEFAULT_BRANCH = DEFAULT_BRANCH
        self.readonly = False  # if readonly will not manipulate local filesystem appart from /tmp
        self.sandbox_python_active = False  # means we have a sandboxed environment where python3 works in
        self.sandbox_lua_active = False  # same for lua
        self.config_changed = False
        self._cmd_installed = {}
        # should be the only location where we allow logs to be going elsewhere
        self.loghandlers = []
        self.errorhandlers = []
        self.state = None
        self.__init = False
        self.debug = False
        self.log_console = False
        self.log_level = 15

        self._sshagent = None
        self.interactive = False

        self.appname = "installer"

        self.FORMAT_TIME = "%a %d %H:%M:%S"

        self.MYCOLORS = {
            "RED": "\033[1;31m",
            "BLUE": "\033[1;34m",
            "CYAN": "\033[1;36m",
            "GREEN": "\033[0;32m",
            "GRAY": "\033[0;37m",
            "YELLOW": "\033[0;33m",
            "RESET": "\033[0;0m",
            "BOLD": "\033[;1m",
            "REVERSE": "\033[;7m",
        }

        self.MYCOLORS_IGNORE = {
            "RED": "",
            "BLUE": "",
            "CYAN": "",
            "GREEN": "",
            "GRAY": "",
            "YELLOW": "",
            "RESET": "",
            "BOLD": "",
            "REVERSE": "",
        }

        LOGFORMATBASE = "{COLOR}{TIME} {filename:<20}{RESET} -{linenr:4d} - {GRAY}{context:<35}{RESET}: {message}"  # DO NOT CHANGE COLOR

        self.LOGFORMAT = {
            "DEBUG": LOGFORMATBASE.replace("{COLOR}", "{CYAN}"),
            "STDOUT": "{message}",
            # 'INFO': '{BLUE}* {message}{RESET}',
            "INFO": LOGFORMATBASE.replace("{COLOR}", "{BLUE}"),
            "WARNING": LOGFORMATBASE.replace("{COLOR}", "{YELLOW}"),
            "ERROR": LOGFORMATBASE.replace("{COLOR}", "{RED}"),
            "CRITICAL": "{RED}{TIME} {filename:<20} -{linenr:4d} - {GRAY}{context:<35}{RESET}: {message}",
        }
        self._db = None

        RedisTools._j = j

    @property
    def db(self):
        if not self._db:
            if self._redis_active:
                self._db = RedisTools._core_get()
        return self._db

    def init(self, reset=False, configdir=None):
        if self.__init:
            return

        args = self._j.core.tools.cmd_args_get()

        if self.platform == "linux":
            self.platform_is_linux = True
            self.platform_is_unix = True
            self.platform_is_osx = False
        elif "darwin" in self.platform:
            self.platform_is_linux = False
            self.platform_is_unix = True
            self.platform_is_osx = True
        else:
            raise self._j.core.tools.exceptions.Base("platform not supported, only linux or osx for now.")

        if not configdir:
            if "JSX_DIR_CFG" in os.environ:
                configdir = os.environ["JSX_DIR_CFG"]
            else:
                if configdir is None and "configdir" in args:
                    configdir = args["configdir"]
                else:
                    configdir = self._cfgdir_get()

        # Set codedir
        self._j.core.tools.dir_ensure("{}/code".format(self._basedir_get()))
        self.config_file_path = os.path.join(configdir, "jumpscale_config.toml")
        # if DockerFactory.indocker():
        #     # this is important it means if we push a container we keep the state file
        #     self.state_file_path = os.path.join(self._homedir_get(), ".jumpscale_done.toml")
        # else:
        self.state_file_path = os.path.join(configdir, "jumpscale_done.toml")

        if self._j.core.tools.exists(self.config_file_path):
            self._config_load()
            if not "DIR_BASE" in self.config:
                return

            self.log_includes = [i for i in self.config.get("LOGGER_INCLUDE", []) if i.strip().strip("''") != ""]
            self.log_excludes = [i for i in self.config.get("LOGGER_EXCLUDE", []) if i.strip().strip("''") != ""]
            self.log_level = self.config.get("LOGGER_LEVEL", 10)
            # self.log_console = self.config.get("LOGGER_CONSOLE", False)
            # self.log_redis = self.config.get("LOGGER_REDIS", True)
            self.debug = self.config.get("DEBUG", False)
            self.debugger = self.config.get("DEBUGGER", "pudb")
            self.interactive = self.config.get("INTERACTIVE", True)

            if os.path.exists(os.path.join(self.config["DIR_BASE"], "bin", "python3.6")):
                self.sandbox_python_active = True
            else:
                self.sandbox_python_active = False

        else:
            self.config = self.config_default_get()

        self._state_load()

        sys.excepthook = self.excepthook
        if RedisTools.active and self._j.core.tools.exists(
            "{}/bin".format(self.config["DIR_BASE"])
        ):  # To check that Js is on host
            from jumpscale11.core.LogHandler import LogHandler

            self.loghandler_redis = LogHandler(db=self.db)
        else:
            print("- redis loghandler cannot be loaded")
            self.loghandler_redis = None

        self.__init = True

    @property
    def sshagent(self):
        if not self._sshagent:
            # if self.config["SSH_AGENT"]
            from jumpscale11.core.SSHAgent import SSHAgent

            self._sshagent = SSHAgent()
        return self._sshagent

    @property
    def platform(self):
        """
        will return one of following strings:
            linux, darwin

        """
        return sys.platform

    #
    # def platform_is_linux(self):
    #     return "posix" in sys.builtin_module_names

    def check_platform(self):
        """check if current platform is supported (linux or darwin)
        for linux, the version check is done by `UbuntuInstaller.ensure_version()`

        :raises RuntimeError: in case platform is not supported
        """
        platform = self.platform
        if "linux" in platform:
            from jumpscale11.core.UbuntuInstaller import UbuntuInstaller

            UbuntuInstaller.ensure_version()
        elif "darwin" not in platform:
            raise self._j.core.tools.exceptions.Base("Your platform is not supported")

    def _homedir_get(self):
        if "HOMEDIR" in os.environ:
            dir_home = os.environ["HOMEDIR"]
        elif "HOME" in os.environ:
            dir_home = os.environ["HOME"]
        else:
            dir_home = "/root"
        return dir_home

    def _basedir_get(self):
        if self.readonly:
            return "/tmp/jumpscale"
        if "darwin" not in self.platform:
            isroot = None
            rc, out, err = self._j.core.tools.execute("whoami", showout=False, die=False)
            if rc == 0:
                if out.strip() == "root":
                    isroot = 1
            if self._j.core.tools.exists("/sandbox") or isroot == 1:
                self._j.core.tools.dir_ensure("/sandbox")
                return "/sandbox"
        p = "%s/sandbox" % self._homedir_get()
        if not self._j.core.tools.exists(p):
            self._j.core.tools.dir_ensure(p)
        return p

    def _cfgdir_get(self):
        if self.readonly:
            return "/tmp/jumpscale/cfg"
        return "%s/cfg" % self._basedir_get()

    def config_default_get(self, config={}):
        if "DIR_BASE" not in config:
            config["DIR_BASE"] = self._basedir_get()

        if "DIR_HOME" not in config:
            config["DIR_HOME"] = self._homedir_get()

        if not "DIR_CFG" in config:
            config["DIR_CFG"] = self._cfgdir_get()

        if not "USEGIT" in config:
            config["USEGIT"] = True
        if not "READONLY" in config:
            config["READONLY"] = False
        if not "DEBUG" in config:
            config["DEBUG"] = False
        if not "DEBUGGER" in config:
            config["DEBUGGER"] = "pudb"
        if not "INTERACTIVE" in config:
            config["INTERACTIVE"] = True
        if not "SECRET" in config:
            config["SECRET"] = ""
        if "SSH_AGENT" not in config:
            config["SSH_AGENT"] = True
        if "SSH_KEY_DEFAULT" not in config:
            config["SSH_KEY_DEFAULT"] = ""
        if "LOGGER_INCLUDE" not in config:
            config["LOGGER_INCLUDE"] = ["*"]
        if "LOGGER_EXCLUDE" not in config:
            config["LOGGER_EXCLUDE"] = ["sal.fs"]
        if "LOGGER_LEVEL" not in config:
            config["LOGGER_LEVEL"] = 15  # means std out & plus gets logged
        if config["LOGGER_LEVEL"] > 50:
            config["LOGGER_LEVEL"] = 50
        # if "LOGGER_CONSOLE" not in config:
        #     config["LOGGER_CONSOLE"] = True
        # if "LOGGER_REDIS" not in config:
        #     config["LOGGER_REDIS"] = False
        if "LOGGER_PANEL_NRLINES" not in config:
            config["LOGGER_PANEL_NRLINES"] = 0

        if self.readonly:
            config["DIR_TEMP"] = "/tmp/jumpscale_installer"
            # config["LOGGER_REDIS"] = False
            # config["LOGGER_CONSOLE"] = True

        if not "DIR_TEMP" in config:
            config["DIR_TEMP"] = "/tmp/jumpscale"
        if not "DIR_VAR" in config:
            config["DIR_VAR"] = "%s/var" % config["DIR_BASE"]
        if not "DIR_CODE" in config:
            config["DIR_CODE"] = "%s/code" % config["DIR_BASE"]
            # if self._j.core.tools.exists("%s/code" % config["DIR_BASE"]):
            #     config["DIR_CODE"] = "%s/code" % config["DIR_BASE"]
            # else:
            #     config["DIR_CODE"] = "%s/code" % config["DIR_HOME"]
        if not "DIR_BIN" in config:
            config["DIR_BIN"] = "%s/bin" % config["DIR_BASE"]
        if not "DIR_APPS" in config:
            config["DIR_APPS"] = "%s/apps" % config["DIR_BASE"]

        if not "EXPLORER_ADDR" in config:
            config["EXPLORER_ADDR"] = "explorer.testnet.grid.tf"
        if not "THREEBOT_DOMAIN" in config:
            config["THREEBOT_DOMAIN"] = "3bot.testnet.grid.tf"

        return config

    def configure(
        self,
        configdir=None,
        codedir=None,
        config={},
        readonly=None,
        sshkey=None,
        sshagent_use=None,
        debug_configure=None,
        secret=None,
        interactive=False,
    ):
        """

        the args of the command line will also be parsed, will check for

        --configdir=                    default $BASEDIR/cfg
        --codedir=                      default $BASEDIR/code

        --sshkey=                       key to use for ssh-agent if any
        --no-sshagent                   default is to use the sshagent, if you want to disable use this flag

        --readonly                      default is false
        --no-interactive                default is interactive, means will ask questions
        --debug_configure               default debug_configure is False, will configure in debug mode

        :param configdir: is the directory where all configuration & keys will be stored
        :param basedir: the root of the sandbox
        :param config: configuration arguments which go in the config file
        :param readonly: specific mode of operation where minimal changes will be done while using JSX
        :param codedir: std $sandboxdir/code
        :return:
        """

        basedir = self._basedir_get()

        if not os.path.exists(self.config_file_path):
            self.config = self.config_default_get(config=config)
        else:
            self._config_load()

        if interactive not in [True, False]:
            raise self._j.core.tools.exceptions.Base("interactive is True or False")
        args = self._j.core.tools.cmd_args_get()

        if configdir is None and "configdir" in args:
            configdir = args["configdir"]
        if codedir is None and "codedir" in args:
            codedir = args["codedir"]
        # if sshkey is None and "sshkey" in args:
        #     sshkey = args["sshkey"]

        if readonly is None and "readonly" in args:
            readonly = True

        if sshagent_use is None or ("no-sshagent" in args and sshagent_use is False):
            sshagent_use = False
        else:
            sshagent_use = True

        if debug_configure is None and "debug_configure" in args:
            debug_configure = True

        if not configdir:
            if "DIR_CFG" in config:
                configdir = config["DIR_CFG"]
            elif "JSX_DIR_CFG" in os.environ:
                configdir = os.environ["JSX_DIR_CFG"]
            else:
                configdir = self._cfgdir_get()
        config["DIR_CFG"] = configdir

        # installpath = os.path.dirname(inspect.getfile(os.path))
        # # MEI means we are pyexe BaseInstaller
        # if installpath.find("/_MEI") != -1 or installpath.endswith("dist/install"):
        #     pass  # dont need yet but keep here

        config["DIR_BASE"] = basedir

        if basedir == "/sandbox" and not os.path.exists(basedir):
            script = """
            set -ex
            cd /
            sudo mkdir -p /sandbox/cfg
            sudo chown -R {USERNAME}:{GROUPNAME} /sandbox
            mkdir -p /usr/local/EGG-INFO
            sudo chown -R {USERNAME}:{GROUPNAME} /usr/local/EGG-INFO
            """
            args = {}
            args["USERNAME"] = getpass.getuser()
            st = os.stat(self.config["DIR_HOME"])
            gid = st.st_gid
            args["GROUPNAME"] = grp.getgrgid(gid)[0]
            self._j.core.tools.execute(script, interactive=True, args=args, die_if_args_left=True)

        self.config_file_path = os.path.join(config["DIR_CFG"], "jumpscale_config.toml")

        if codedir is not None:
            config["DIR_CODE"] = codedir

        if not os.path.exists(self.config_file_path):
            self.config = self.config_default_get(config=config)
        else:
            self._config_load()

        # merge interactive flags
        if "INTERACTIVE" in self.config:
            self.interactive = interactive and self.config["INTERACTIVE"]
            # enforce interactive flag consistency after having read the config file,
            # arguments overrides config file behaviour
        self.config["INTERACTIVE"] = self.interactive

        if not "DIR_TEMP" in self.config:
            config.update(self.config)
            self.config = self.config_default_get(config=config)

        if readonly:
            self.config["READONLY"] = readonly

        self.config["SSH_AGENT"] = sshagent_use
        if sshkey:
            self.config["SSH_KEY_DEFAULT"] = sshkey
        if debug_configure:
            self.config["DEBUG"] = debug_configure

        for key, val in config.items():
            self.config[key] = val

        if not sshagent_use and self.interactive:  # just a warning when interactive
            T = """
            Did not find an ssh agent, is this ok?
            It's recommended to have a SSH key as used on github loaded in your ssh-agent
            If the SSH key is not found, repositories will be cloned using https.
            Is better to stop now and to load an ssh-agent with 1 key.
            """
            print(self._j.core.tools.text_strip(T))
            if self.interactive:
                if not self._j.core.tools.ask_yes_no("OK to continue?"):
                    sys.exit(1)

        # defaults are now set, lets now configure the system
        if sshagent_use:
            # TODO: this is an error SSH_agent does not work because cannot identify which private key to use
            # see also: https://github.com/threefoldtech/jumpscaleX_core/issues/561
            self.sshagent = SSHAgent()
            self.sshagent.key_default_name
        if secret is None:
            if "SECRET" not in self.config or not self.config["SECRET"]:
                self.secret_set()  # will create a new one only when it doesn't exist
        else:
            self.secret_set(secret)

        if DockerFactory.indocker():
            self.config["IN_DOCKER"] = True
        else:
            self.config["IN_DOCKER"] = False

        self.config_save()
        self.init(configdir=configdir)

    @property
    def adminsecret(self):
        if not self.config["SECRET"]:
            self.secret_set()
        return self.config["SECRET"][0:32]

    def secret_set(self, secret=None):
        if self.interactive:
            while not secret:  # keep asking till the secret is not empty
                secret = self._j.core.tools.ask_password("provide secret to use for encrypting private key")
            secret = secret.encode()
        else:
            if not secret:
                secret = str(random.randint(1, 100000000)).encode()
            else:
                secret = secret.encode()

        import hashlib

        m = hashlib.sha256()
        m.update(secret)

        secret2 = m.hexdigest()

        if "SECRET" not in self.config:
            self.config["SECRET"] = ""

        if self.config["SECRET"] != secret2:
            self.config["SECRET"] = secret2

            self.config_save()

    def test(self):
        if not j.core.myenv.loghandlers != []:
            self._j.core.tools.shell()

    def excepthook(self, exception_type, exception_obj, tb, die=True, stdout=True, level=50):
        """
        :param exception_type:
        :param exception_obj:
        :param tb:
        :param die:
        :param stdout:
        :param level:
        :return: logdict see github/threefoldtech/jumpscaleX_core/docs/Internals/logging_errorhandling/logdict.md
        """
        if isinstance(exception_obj, self._j.core.tools.exceptions.RemoteException):
            print(self._j.core.tools.text_replace("{RED}*****Remote Exception*****{RESET}"))
            logdict = exception_obj.data
            self._j.core.tools.log2stdout(logdict)

            exception_obj.data = None
            exception_obj.exception = None

        try:
            logdict = self._j.core.tools.log(tb=tb, level=level, exception=exception_obj, stdout=stdout)
        except Exception as e:
            self._j.core.tools.pprint("{RED}ERROR IN LOG HANDLER")
            print(e)
            ttype, msg, tb = sys.exc_info()
            traceback.print_exception(etype=ttype, tb=tb, value=msg)
            self._j.core.tools.pprint("{RESET}")
            sys.exit(1)

        exception_obj._logdict = logdict

        if self.debug and tb and pudb:
            # exception_type, exception_obj, tb = sys.exc_info()
            pudb.post_mortem(tb)

        if die is False:
            return logdict
        else:
            sys.exit(1)

    def exception_handle(self, exception_obj, die=True, stdout=True, level=50, stack_go_up=0):
        """
        e is the error as raised by e.g. try/except statement
        :param exception_obj: the exception obj coming from the try/except
        :param die: die if error
        :param stdout: if True send the error log to stdout
        :param level: 50 is error critical
        :return: logdict see github/threefoldtech/jumpscaleX_core/docs/Internals/logging_errorhandling/logdict.md

        example


        try:
            something
        except Exception as e:
            logdict = j.core.myenv.exception_handle(e,die=False,stdout=True)


        """
        ttype, msg, tb = sys.exc_info()
        return self.excepthook(ttype, exception_obj, tb, die=die, stdout=stdout, level=level)

    def config_edit(self):
        """
        edits the configuration file which is in {DIR_BASE}/cfg/jumpscale_config.toml
        {DIR_BASE} normally is /sandbox
        """
        self._j.core.tools.file_edit(self.config_file_path)

    def _config_load(self):
        """
        loads the configuration file which default is in {DIR_BASE}/cfg/jumpscale_config.toml
        {DIR_BASE} normally is /sandbox
        """
        config = self._j.core.tools.config_load(self.config_file_path)
        self.config = self.config_default_get(config)

    def config_save(self):
        self._j.core.tools.config_save(self.config_file_path, self.config)

    def _state_load(self):
        """
        only 1 level deep toml format only for int,string,bool
        no multiline
        """
        if self._j.core.tools.exists(self.state_file_path):
            self.state = self._j.core.tools.config_load(self.state_file_path, if_not_exist_create=False)
        elif not self.readonly:
            self.state = self._j.core.tools.config_load(self.state_file_path, if_not_exist_create=True)
        else:
            self.state = {}

    def state_save(self):
        if self.readonly:
            return
        self._j.core.tools.config_save(self.state_file_path, self.state)

    def _key_get(self, key):
        key = key.split("=", 1)[0]
        key = key.split(">", 1)[0]
        key = key.split("<", 1)[0]
        key = key.split(" ", 1)[0]
        key = key.upper()
        return key

    def state_get(self, key):
        key = self._key_get(key)
        if key in self.state:
            return True
        return False

    def state_set(self, key):
        if self.readonly:
            return
        key = self._key_get(key)
        self.state[key] = True
        self.state_save()

    def state_delete(self, key):
        if self.readonly:
            return
        key = self._key_get(key)
        if key in self.state:
            self.state.pop(key)
            self.state_save()

    def states_delete(self, prefix):
        if self.readonly:
            return
        prefix = prefix.upper()
        keys = [i for i in self.state.keys()]
        for key in keys:
            if key.startswith(prefix):
                self.state.pop(key)
                # print("#####STATEPOP:%s" % key)
                self.state_save()

    def state_reset(self):
        """
        remove all state
        """
        self._j.core.tools.delete(self.state_file_path)
        self._state_load()
