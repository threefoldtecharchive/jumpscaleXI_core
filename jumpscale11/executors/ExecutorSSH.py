import msgpack


class ExecutorSSH:
    def __init__(self, addr=None, port=22, debug=False, name="executor"):
        self.name = name
        self.addr = addr
        self.port = port
        self.debug = debug
        self._id = None
        self._env = {}
        self.readonly = False
        self.CURDIR = ""
        self._data_path = "/var/executor_data"
        self._init3()

    def reset(self):
        self.state_reset()
        self._init3()
        self.save()

    def _init3(self):
        self._config = None
        # self._env_on_system = None

    @property
    def config(self):
        if not self._config:
            self.load()
        return self._config

    def load(self):
        if self.exists(self._data_path):
            data = self.file_read(self._data_path, binary=True)
            self._config = msgpack.loads(data)
            if "DIR_BASE" not in self._config:
                self.systemenv_load()
                self.save()
        else:
            self._config = {}

    def cmd_installed(self, cmd):
        rc, out, err = self.execute("which %s" % cmd, die=False, showout=False)
        if rc > 0:
            return False
        return True

    def save(self):
        """
        only relevant for ssh
        :return:
        """
        data = msgpack.dumps(self.config)
        self.file_write(self._data_path, data)

    def delete(self, path):
        path = self._replace(path)
        cmd = "rm -rf %s" % path
        self.execute(cmd)

    def exists(self, path):
        path = self._replace(path)
        rc, _, _ = self.execute("test -e %s" % path, die=False, showout=False)
        if rc > 0:
            return False
        else:
            return True

    def _replace(self, content, args=None):
        """
        args will be substitued to .format(...) string function https://docs.python.org/3/library/string.html#formatspec
        MyEnv.config will also be given to the format function
        content example:
        "{name!s:>10} {val} {n:<10.2f}"  #floating point rounded to 2 decimals
        performance is +100k per sec
        """
        return j.core.tools.logtext_replace(content=content, args=args, executor=self)

    def dir_ensure(self, path):
        cmd = "mkdir -p %s" % path
        self.execute(cmd, interactive=False)

    def path_isdir(self, path):
        """
        checks if the path is a directory
        :return:
        """
        rc, out, err = self.execute('if [ -d "%s" ] ;then echo DIR ;fi' % path, interactive=False)
        return out.strip() == "DIR"

    def path_isfile(self, path):
        """
        checks if the path is a directory
        :return:
        """
        rc, out, err = self.execute('if [ -f "%s" ] ;then echo FILE ;fi' % path, interactive=False)
        return out.strip() == "FILE"

    @property
    def platformtype(self):
        raise Tools.exceptions("not implemented")

    def file_read(self, path, binary=False):
        j.core.tools.log("file read:%s" % path)
        if not binary:
            rc, out, err = self.execute("cat %s" % path, showout=False, interactive=False)
            return out
        else:
            p = Tools._file_path_tmp_get("data")
            self.download(path, dest=p)
            data = Tools.file_read(p)
            Tools.delete(p)
            return data

    def file_write(self, path, content, mode=None, owner=None, group=None, showout=True):
        """
        @param append if append then will add to file
        """
        path = self._replace(path)
        if showout:
            j.core.tools.log("file write:%s" % path)

        assert isinstance(path, str)
        # if isinstance(content, str) and not "'" in content:
        #
        #     cmd = 'echo -n -e "%s" > %s' % (content, path)
        #     self.execute(cmd)
        # else:
        temp = Tools._file_path_tmp_get(ext="data")
        Tools.file_write(temp, content)
        self.upload(temp, path)
        Tools.delete(temp)
        cmd = ""
        if mode:
            cmd += "chmod %s %s && " % (mode, path)
        if owner:
            cmd += "chown %s %s && " % (owner, path)
        if group:
            cmd += "chgrp %s %s &&" % (group, path)
        cmd = cmd.strip().strip("&")
        if cmd:
            self.execute(cmd, showout=False, interactive=False)

        return None

    @property
    def uid(self):
        if self._id is None:
            raise Tools.exceptions.Base("self._id cannot be None")
        return self._id

    def find(self, path):
        rc, out, err = self.execute("find %s" % path, die=False, interactive=False)
        if rc > 0:
            if err.lower().find("no such file") != -1:
                return []
            raise Tools.exceptions.Base("could not find:%s \n%s" % (path, err))
        res = []
        for line in out.split("\n"):
            if line.strip() == path:
                continue
            if line.strip() == "":
                continue
            res.append(line)
        res.sort()
        return res

    @property
    def container_check(self):
        """
        means we don't work with ssh-agent ...
        """

        if not "IN_DOCKER" in self.config:
            rc, out, _ = self.execute("cat /proc/1/cgroup", die=False, showout=False, interactive=False)
            if rc == 0 and out.find("/docker/") != -1:
                self.config["IN_DOCKER"] = True
            else:
                self.config["IN_DOCKER"] = False
            self.save()
        return self.config["IN_DOCKER"]

    # @property
    # def env_on_system(self):
    #     if not self._env_on_system:
    #         self.systemenv_load()
    #         self._env_on_system = pickle.loads(self.env_on_system_msgpack)
    #     return self._env_on_system
    #
    # @property
    # def env(self):
    #     return self.env_on_system["ENV"]

    @property
    def state(self):
        if "state" not in self.config:
            self.config["state"] = {}
        return self.config["state"]

    def state_exists(self, key):
        key = Tools.text_strip_to_ascii_dense(key)
        return key in self.state

    def state_set(self, key, val=None, save=True):
        key = Tools.text_strip_to_ascii_dense(key)
        if save or key not in self.state or self.state[key] != val:
            self.state[key] = val
            self.save()

    def state_get(self, key, default_val=None):
        key = Tools.text_strip_to_ascii_dense(key)
        if key not in self.state:
            if default_val:
                self.state[key] = default_val
                return default_val
            else:
                return None
        else:
            return self.state[key]

    def state_delete(self, key):
        key = Tools.text_strip_to_ascii_dense(key)
        if key in self.state:
            self.state.pop(key)
            self.save()

    def systemenv_load(self):
        """
        get relevant information from remote system e.g. hostname, env variables, ...
        :return:
        """
        C = """
        set +ex
        if [ -e /sandbox ]; then
            export PBASE=/sandbox
        else
            export PBASE=~/sandbox
        fi
        ls $PBASE  > /dev/null 2>&1 && echo 'ISSANDBOX = 1' || echo 'ISSANDBOX = 0'
        ls "$PBASE/bin/python3"  > /dev/null 2>&1 && echo 'ISSANDBOX_BIN = 1' || echo 'ISSANDBOX_BIN = 0'
        echo UNAME = \""$(uname -mnprs)"\"
        echo "HOME = $HOME"
        echo HOSTNAME = "$(hostname)"
        if [[ "$(uname -s)" == "Darwin" ]]; then
            echo OS_TYPE = "darwin"
        else
            echo OS_TYPE = "ubuntu"
        fi
        echo "CFG_JUMPSCALE = --TEXT--"
        cat $PBASE/cfg/jumpscale_config.msgpack 2>/dev/null || echo ""
        echo --TEXT--
        echo "BASHPROFILE = --TEXT--"
        cat $HOME/.profile_js 2>/dev/null || echo ""
        echo --TEXT--
        echo "ENV = --TEXT--"
        export
        echo --TEXT--
        """
        rc, out, err = self.execute(C, showout=False, interactive=False, replace=False)
        res = {}
        state = ""
        for line in out.split("\n"):
            if line.find("--TEXT--") != -1 and line.find("=") != -1:
                varname = line.split("=")[0].strip().lower()
                state = "TEXT"
                txt = ""
                continue

            if state == "TEXT":
                if line.strip() == "--TEXT--":
                    res[varname.upper()] = txt
                    state = ""
                    continue
                else:
                    txt += line + "\n"
                    continue

            if "=" in line:
                varname, val = line.split("=", 1)
                varname = varname.strip().lower()
                val = str(val).strip().strip('"')
                if val.lower() in ["1", "true"]:
                    val = True
                elif val.lower() in ["0", "false"]:
                    val = False
                else:
                    try:
                        val = int(val)
                    except BaseException:
                        pass
                res[varname.upper()] = val

        if res["CFG_JUMPSCALE"].strip() != "":
            rconfig = Tools.config_load(content=res["CFG_JUMPSCALE"])
            res["CFG_JUMPSCALE"] = rconfig
        else:
            res["CFG_JUMPSCALE"] = {}

        envdict = {}
        for line in res["ENV"].split("\n"):
            line = line.replace("declare -x", "")
            line = line.strip()
            if line.strip() == "":
                continue
            if "=" in line:
                pname, pval = line.split("=", 1)
                pval = pval.strip("'").strip('"')
                envdict[pname.strip().upper()] = pval.strip()

        res["ENV"] = envdict

        def get_cfg(name, default):
            name = name.upper()
            if "CFG_JUMPSCALE" in res and name in res["CFG_JUMPSCALE"]:
                self.config[name] = res["CFG_JUMPSCALE"]
                return
            if name not in self.config:
                self.config[name] = default

        get_cfg("DIR_HOME", res["ENV"]["HOME"])
        get_cfg("DIR_BASE", "/sandbox")
        get_cfg("DIR_CFG", "%s/cfg" % self.config["DIR_BASE"])
        get_cfg("DIR_TEMP", "/tmp")
        get_cfg("DIR_VAR", "%s/var" % self.config["DIR_BASE"])
        get_cfg("DIR_CODE", "%s/code" % self.config["DIR_BASE"])
        get_cfg("DIR_BIN", "/usr/local/bin")

    def execute(
        self,
        cmd,
        die=True,
        showout=False,
        timeout=1000,
        sudo=False,
        replace=True,
        interactive=False,
        retry=None,
        args=None,
        python=False,
        jumpscale=False,
        debug=False,
    ):
        original_command = cmd + ""
        if not args:
            args = {}

        tempfile, cmd = Tools._cmd_process(
            cmd=cmd,
            python=python,
            jumpscale=jumpscale,
            die=die,
            env=args,
            sudo=sudo,
            debug=debug,
            replace=replace,
            executor=self,
        )

        Tools._cmd_check(cmd)

        if interactive:
            cmd2 = "ssh -oStrictHostKeyChecking=no -t root@%s -A -p %s '%s'" % (self.addr, self.port, cmd)
        else:
            cmd2 = "ssh -oStrictHostKeyChecking=no root@%s -A -p %s '%s'" % (self.addr, self.port, cmd)
        r = Tools._execute(
            cmd2,
            interactive=interactive,
            showout=showout,
            timeout=timeout,
            retry=retry,
            die=die,
            original_command=original_command,
        )
        if tempfile:
            Tools.delete(tempfile)
        return r

    def upload(
        self,
        source,
        dest=None,
        recursive=True,
        createdir=False,
        rsyncdelete=True,
        ignoredir=None,
        ignorefiles=None,
        keepsymlinks=True,
        retry=4,
    ):
        """
        :param source:
        :param dest:
        :param recursive:
        :param createdir:
        :param rsyncdelete:
        :param ignoredir: the following are always in, no need to specify ['.egg-info', '.dist-info', '__pycache__']
        :param ignorefiles: the following are always in, no need to specify: ["*.egg-info","*.pyc","*.bak"]
        :param keepsymlinks:
        :param showout:
        :return:
        """
        source = self._replace(source)
        if not dest:
            dest = source
        else:
            dest = self._replace(dest)
        if not os.path.exists(source):
            raise Tools.exceptions.Input("path '%s' not found" % source)

        if os.path.isfile(source):
            if createdir:
                destdir = os.path.dirname(source)
                self.dir_ensure(destdir)
            cmd = "scp -P %s %s root@%s:%s" % (self.port, source, self.addr, dest)
            Tools._execute(cmd, showout=True, interactive=False)
            return
        raise Tools.exceptions.RuntimeError("not implemented")
        dest = self._replace(dest)
        if dest[0] != "/":
            raise Tools.exceptions.RuntimeError("need / in beginning of dest path")
        if source[-1] != "/":
            source += "/"
        if dest[-1] != "/":
            dest += "/"
        dest = "%s@%s:%s" % (self.login, self.addr, dest)

    def download(self, source, dest=None, ignoredir=None, ignorefiles=None, recursive=True):
        """
        :param source:
        :param dest:
        :param recursive:
        :param ignoredir: the following are always in, no need to specify ['.egg-info', '.dist-info', '__pycache__']
        :param ignorefiles: the following are always in, no need to specify: ["*.egg-info","*.pyc","*.bak"]
        :return:
        """
        if not dest:
            dest = source
        else:
            dest = self._replace(dest)
        source = self._replace(source)

        sourcedir = os.path.dirname(source)
        Tools.dir_ensure(sourcedir)

        destdir = os.path.dirname(dest)
        Tools.dir_ensure(destdir)

        cmd = "scp -P %s root@%s:%s %s" % (self.port, self.addr, source, dest)
        Tools._execute(cmd, showout=True, interactive=False)

    def kosmos(self):
        self.jsxexec("j.shell()")

    @property
    def uid(self):
        if not "uid" in self.config:
            self.config["uid"] = str(random.getrandbits(32))
            self.save()
        return self.config["uid"]

    def state_reset(self):
        self.config["state"] = {}
        self.save()
