class Registry:
    def __init__(self):
        self.addr = ["134.209.83.144"]
        self._config = None
        self._executor = None

    @property
    def executor(self):
        if not self._executor:
            self._executor = ExecutorSSH(self.addr[0], 22)
        return self._executor

    @property
    def myname(self):
        """
        is the main config
        """
        myname = j.core.myenv.sshagent.key_default_name
        c = self.config["clients"]
        if myname not in c:
            y = j.core.tools.logask_yes_no(
                "is our unique login name:%s\nif not please say no and define new name." % myname
            )
            if not y:
                myname2 = j.core.tools.ask_string("give your unique loginname")
                msg = "careful: your sshkeyname will be changed accordingly on your system to:%s, ok?" % myname2
                if j.core.tools.ask_yes_no(msg):
                    src = j.core.myenv.sshagent.key_path_get()
                    dest = "%s/%s" % (os.path.dirname(src), myname2)
                    shutil.copyfile(src, dest)
                    shutil.copyfile(src + ".pub", dest + ".pub")
                    j.core.myenv.config["SSH_KEY_DEFAULT"] = myname2
                    j.core.myenv.config_save()
                    j.core.tools.delete(src)
                    j.core.tools.delete(src + ".pub")
                    j.core.myenv.sshagent.keys_unload()
                    j.core.myenv.sshagent.key_load(dest)
                    myname = myname2
                else:
                    raise j.exceptions.Input("cannot continue need unique login name which corresponds to your sshkey")
            c[myname] = {}
        c = c[myname]
        keypub = j.core.myenv.sshagent.keypub

        def showdetails(c):
            print(json.dumps(c))

        def askdetails(c):

            organizations = ["codescalers", "freeflow", "frequencyvillage", "threefold", "incubaid", "bettertoken"]
            organizations2 = ", ".join(organizations)
            if "email" not in c:
                c["email"] = j.core.tools.ask_string("please provide your main email addr")
            if "organizations" not in c:
                print("valid organizations: '%s'" % organizations2)
                c["organizations"] = j.core.tools.ask_string("please provide your organizations (comma separated)")
            if "remark" not in c:
                c["remark"] = j.core.tools.ask_string("any remark?")
            if "telegram" not in c:
                c["telegram"] = j.core.tools.ask_string("please provide your main telegram handle")
            if "mobile" not in c:
                c["mobile"] = j.core.tools.ask_string("please provide your mobile nr's (if more than one use ,)")
            showdetails(c)
            y = j.core.tools.ask_yes_no("is above all correct !!!")
            if not y:
                c["email"] = j.core.tools.ask_string("please provide your main email addr", default=c["email"])
                print("valid organizations: '%s'" % organizations2)
                c["organizations"] = j.core.tools.ask_string(
                    "please provide your organizations (comma separated)", default=c["organizations"]
                )
                c["remark"] = j.core.tools.ask_string("any remark?", default=c["remark"])
                c["telegram"] = j.core.tools.ask_string(
                    "please provide your main telegram handle", default=c["telegram"]
                )
                c["mobile"] = j.core.tools.ask_string(
                    "please provide your mobile nr's (if more than one use ,)", default=c["mobile"]
                )
            self.executor.save()

            o = c["organizations"]
            o2 = []
            for oname in o.lower().split(","):
                oname = oname.strip().lower()
                if oname == "":
                    continue
                if oname not in organizations:
                    raise j.exceptions.Input(
                        "please choose valid organizations (notok:%s): %s" % (oname, organizations2)
                    )
                o2.append(oname)
            c["organizations"] = ",".join(o2)

        if "keypub" not in c:
            c["keypub"] = keypub
            askdetails()
            self.executor.save()
        else:
            if not c["keypub"].strip() == keypub.strip():
                showdetails(c)
                y = j.core.tools.ask_yes_no("Are you sure your are above?")
                raise j.exceptions.Input(
                    "keypub does not correspond, your name:%s, is this a unique name, comes from your main sshkey, change if needed"
                    % myname
                )
        return myname

    def load(self):
        self._config = None

    @property
    def config_mine(self):
        return self.config["clients"][self.myname]

    @property
    def myid(self):
        if "myid" not in self.config_mine:
            if "lastmyid" not in self.config:
                self.config["lastmyid"] = 1
            else:
                self.config["lastmyid"] += 1
            self.config_mine["myid"] = self.config["lastmyid"]
            self.executor.save()
        return self.config_mine["myid"]

    # @iterator
    # def users(self):
    #     for name, data in self.config["clients"].items():
    #         yield data

    @property
    def config(self):
        """
        is the main config
        """
        if not self._config:
            c = self.executor.config
            if not "registry" in c:
                c["registry"] = {}
            config = self.executor.config["registry"]
            if "clients" not in config:
                config["clients"] = {}
            self._config = config
        return self._config

