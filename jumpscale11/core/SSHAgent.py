class SSHAgentKeyError(Exception):
    pass


class SSHAgent:
    def __init__(self):
        self._inited = False
        self._default_key = None
        self.autostart = True
        self.reset()

    @property
    def ssh_socket_path(self):

        if "SSH_AUTH_SOCK" in os.environ:
            return os.environ["SSH_AUTH_SOCK"]

        socketpath = Tools.text_replace("{DIR_VAR}/sshagent_socket")
        os.environ["SSH_AUTH_SOCK"] = socketpath
        return socketpath

    def _key_name_get(self, name):
        if not name:
            if j.core.myenvconfig["SSH_KEY_DEFAULT"]:
                name = j.core.myenv.config["SSH_KEY_DEFAULT"]
            elif j.core.myenv.interactive:
                name = Tools.ask_string("give name for your sshkey")
            else:
                name = "default"
        return name

    def key_generate(self, name=None, passphrase=None, reset=False):
        """
        Generate ssh key

        :param reset: if True, then delete old ssh key from dir, defaults to False
        :type reset: bool, optional
        """
        j.core.tools.log("generate ssh key")
        name = self._key_name_get(name)

        if not passphrase:
            if j.core.myenv.config["interactive"]:
                passphrase = Tools.ask_password(
                    "passphrase for ssh key to generate, \
                        press enter to skip and not use a passphrase"
                )

        path = Tools.text_replace("{DIR_HOME}/.ssh/%s" % name)
        Tools.Ensure("{DIR_HOME}/.ssh")

        if reset:
            Tools.delete("%s" % path)
            Tools.delete("%s.pub" % path)

        if not Tools.exists(path) or reset:
            if passphrase:
                cmd = 'ssh-keygen -t rsa -f {} -N "{}"'.format(path, passphrase)
            else:
                cmd = "ssh-keygen -t rsa -f {}".format(path)
            Tools.execute(cmd, timeout=10)

            j.core.tools.log("load generated sshkey: %s" % path)

    @property
    def key_default_name(self):
        """

        kosmos 'print(j.core.myenv.sshagent.key_default)'

        checks if it can find the default key for ssh-agent, if not will ask
        :return:
        """

        def ask_key(key_names):
            if len(key_names) == 1:
                # if j.core.myenv.interactive:
                #     if not Tools.ask_yes_no("Ok to use key: '%s' as your default key?" % key_names[0]):
                #         return None
                name = key_names[0]
            elif len(key_names) == 0:
                raise Tools.exceptions.Operations(
                    "Cannot find a possible ssh-key, please load your possible keys in your ssh-agent or have in your homedir/.ssh"
                )
            else:
                if j.core.myenv.interactive:
                    name = Tools.ask_choices("Which is your default sshkey to use", key_names)
                else:
                    name = "id_rsa"
            return name

        self._keys  # will fetch the keys if not possible will show error

        sshkey = j.core.myenv.config["SSH_KEY_DEFAULT"]

        if not sshkey:
            if len(self.key_names) > 0:
                sshkey = ask_key(self.key_names)
        if not sshkey:
            hdir = Tools.text_replace("{DIR_HOME}/.ssh")
            if not Tools.exists(hdir):
                msg = "cannot find home dir:%s" % hdir
                msg += "\n### Please get a ssh key or generate one using ssh-keygen\n"
                raise Tools.exceptions.Operations(msg)
            choices = []
            for item in os.listdir(hdir):
                item2 = item.lower()
                if not (
                    item.startswith(".")
                    or item2.endswith((".pub", ".backup", ".toml", ".old"))
                    or item in ["known_hosts", "config", "authorized_keys"]
                ):
                    choices.append(item)
            sshkey = ask_key(choices)

        if not sshkey in self.key_names:
            if DockerFactory.indocker():
                raise Tools.exceptions.Base("sshkey should be passed forward by means of SSHAgent")
            self.key_load(name=sshkey)
            assert sshkey in self.key_names

        if j.core.myenv.config["SSH_KEY_DEFAULT"] != sshkey:
            j.core.myenv.config["SSH_KEY_DEFAULT"] = sshkey
            j.core.myenv.config_save()

        return sshkey

    def key_load(self, path=None, name=None, passphrase=None, duration=3600 * 24):
        """
        load the key on path

        :param path: path for ssh-key, can be left empty then we get the default name which will become path
        :param name: is the name of key which is in ~/.ssh/$name, can be left empty then will be default
        :param passphrase: passphrase for ssh-key, defaults to ""
        :type passphrase: str
        :param duration: duration, defaults to 3600*24
        :type duration: int, optional
        :raises RuntimeError: Path to load sshkey on couldn't be found
        :return: name,path
        """
        if name:
            path = Tools.text_replace("{DIR_HOME}/.ssh/%s" % name)
        elif path:
            name = os.path.basename(path)
        else:
            name = self._key_name_get(name)
            path = Tools.text_replace("{DIR_HOME}/.ssh/%s" % name)

        if name in self.key_names:
            return

        if not Tools.exists(path):
            raise Tools.exceptions.Base("Cannot find path:%s for sshkey (private key)" % path)

        j.core.tools.log("load ssh key: %s" % path)
        os.chmod(path, 0o600)

        if passphrase:
            j.core.tools.log("load with passphrase")
            C = """
                cd /tmp
                echo "exec cat" > ap-cat.sh
                chmod a+x ap-cat.sh
                export DISPLAY=1
                echo {passphrase} | SSH_ASKPASS=./ap-cat.sh ssh-add -t {duration} {path}
                """.format(
                path=path, passphrase=passphrase, duration=duration
            )
            rc, out, err = Tools.execute(C, showout=False, die=False)
            if rc > 0:
                Tools.delete("/tmp/ap-cat.sh")
                raise Tools.exceptions.Operations("Could not load sshkey with passphrase (%s)" % path)
        else:
            # load without passphrase
            cmd = "ssh-add -t %s %s " % (duration, path)
            rc, out, err = Tools.execute(cmd, showout=False, die=False)
            if rc > 0:
                raise Tools.exceptions.Operations("Could not load sshkey without passphrase (%s)" % path)

        self.reset()

        return name, path

    def key_unload(self, name):
        if name in self._keys:
            path = self.key_path_get(name)
            cmd = "ssh-add -d %s" % (path)
            rc, out, err = Tools.execute(cmd, showout=False, die=True)

    def keys_unload(self):
        cmd = "ssh-add -D"
        rc, out, err = Tools.execute(cmd, showout=False, die=True)

    @property
    def _keys(self):
        """
        """
        if self.__keys is None:
            self._read_keys()
        return self.__keys

    def _read_keys(self):
        return_code, out, err = Tools.execute("ssh-add -L", showout=False, die=False, timeout=2)
        if return_code:
            if return_code == 1 and out.find("The agent has no identities") != -1:
                self.__keys = []
                return []
            else:
                # Remove old socket if can't connect
                if Tools.exists(self.ssh_socket_path):
                    Tools.delete(self.ssh_socket_path)
                    # did not work first time, lets try again
                    return_code, out, err = Tools.execute("ssh-add -L", showout=False, die=False, timeout=10)

        if return_code and self.autostart:
            # ok still issue, lets try to start the ssh-agent if that could be done
            self.start()
            return_code, out, err = Tools.execute("ssh-add -L", showout=False, die=False, timeout=10)
            if return_code == 1 and out.find("The agent has no identities") != -1:
                self.__keys = []
                return []

        if return_code:
            return_code, out, err = Tools.execute("ssh-add", showout=False, die=False, timeout=10)
            if out.find("Error connecting to agent: No such file or directory"):
                raise SSHAgentKeyError("Error connecting to agent: No such file or directory")
            else:
                raise SSHAgentKeyError("Unknown error in ssh-agent, cannot find")

        keys = [line.split() for line in out.splitlines() if len(line.split()) == 3]
        self.__keys = list(map(lambda key: [key[2], " ".join(key[0:2])], keys))
        return self.__keys

    def reset(self):
        self.__keys = None

    @property
    def available(self):
        """
        Check if agent available (does not mean that the sshkey has been loaded, just checks the sshagent is there)
        :return: True if agent is available, False otherwise
        :rtype: bool
        """
        try:
            self._keys
        except SSHAgentKeyError:
            return False
        return True

    def keys_list(self, key_included=False):
        """
        kosmos 'print(j.clients.sshkey.keys_list())'
        list ssh keys from the agent

        :param key_included: defaults to False
        :type key_included: bool, optional
        :raises RuntimeError: Error during listing of keys
        :return: list of paths
        :rtype: list
        """
        if key_included:
            return self._keys
        else:
            return [i[0] for i in self._keys]

    @property
    def key_names(self):

        return [os.path.basename(i[0]) for i in self._keys]

    @property
    def key_paths(self):

        return [i[0] for i in self._keys]

    def key_path_get(self, keyname=None, die=True):
        """
        Returns Path of private key that is loaded in the agent

        :param keyname: name of key loaded to agent to get its path, if empty will check if there is 1 loaded, defaults to ""
        :type keyname: str, optional
        :param die:Raise error if True,else do nothing, defaults to True
        :type die: bool, optional
        :raises RuntimeError: Key not found with given keyname
        :return: path of private key
        :rtype: str
        """
        if not keyname:
            keyname = self.key_default_name
        else:
            keyname = os.path.basename(keyname)
        for item in self.keys_list():
            item2 = os.path.basename(item)
            if item2.lower() == keyname.lower():
                return item
        if die:
            raise Tools.exceptions.Base(
                "Did not find key with name:%s, check its loaded in ssh-agent with ssh-add -l" % keyname
            )

    def keypub_path_get(self, keyname=None):
        path = self.key_path_get(keyname)
        return path + ".pub"

    @property
    def keypub(self):
        return Tools.file_read(self.keypub_path_get()).decode()

    def profile_js_configure(self):
        """
        kosmos 'j.clients.sshkey.profile_js_configure()'
        """

        bashprofile_path = os.path.expanduser("~/.profile")
        if not Tools.exists(bashprofile_path):
            Tools.execute("touch %s" % bashprofile_path)

        content = Tools.readFile(bashprofile_path)
        out = ""
        for line in content.split("\n"):
            if line.find("#JSSSHAGENT") != -1:
                continue
            if line.find("SSH_AUTH_SOCK") != -1:
                continue

            out += "%s\n" % line

        out += '[ -z "SSH_AUTH_SOCK" ] && export SSH_AUTH_SOCK=%s' % self.ssh_socket_path
        out = out.replace("\n\n\n", "\n\n")
        out = out.replace("\n\n\n", "\n\n")
        Tools.writeFile(bashprofile_path, out)

    def start(self):
        """

        start ssh-agent, kills other agents if more than one are found

        :raises RuntimeError: Couldn't start ssh-agent
        :raises RuntimeError: ssh-agent was not started while there was no error
        :raises RuntimeError: Could not find pid items in ssh-add -l
        """

        socketpath = self.ssh_socket_path

        Tools.process_kill_by_by_filter("ssh-agent")

        Tools.delete(socketpath)

        if not Tools.exists(socketpath):
            j.core.tools.log("start ssh agent")
            Tools.dir_ensure("{DIR_VAR}")
            rc, out, err = Tools.execute("ssh-agent -a %s" % socketpath, die=False, showout=False, timeout=20)
            if rc > 0:
                raise Tools.exceptions.Base("Could not start ssh-agent, \nstdout:%s\nstderr:%s\n" % (out, err))
            else:
                if not Tools.exists(socketpath):
                    err_msg = "Serious bug, ssh-agent not started while there was no error, " "should never get here"
                    raise Tools.exceptions.Base(err_msg)

                # get pid from out of ssh-agent being started
                piditems = [item for item in out.split("\n") if item.find("pid") != -1]

                # print(piditems)
                if len(piditems) < 1:
                    j.core.tools.log("results was: %s", out)
                    raise Tools.exceptions.Base("Cannot find items in ssh-add -l")

                # pid = int(piditems[-1].split(" ")[-1].strip("; "))
                # socket_path = j.sal.fs.joinPaths("/tmp", "ssh-agent-pid")
                # j.sal.fs.writeFile(socket_path, str(pid))

            return

        self.reset()

    def kill(self):
        """
        Kill all agents if more than one is found

        """
        Tools.process_kill_by_by_filter("ssh-agent")
        Tools.delete(self.ssh_socket_path)
        # Tools.delete("/tmp", "ssh-agent-pid"))
        self.reset()
