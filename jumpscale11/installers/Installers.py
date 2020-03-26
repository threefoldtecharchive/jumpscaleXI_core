class JumpscaleInstaller:
    def install(self, sandboxed=False, force=False, gitpull=False, prebuilt=False, branch=None, threebot=False):

        j.core.myenv.check_platform()
        # will check if there's already a key loaded (forwarded) will continue installation with it
        rc, _, _ = Tools.execute("ssh-add -L")
        if not rc:
            if "SSH_Agent" in j.core.myenv.config and j.core.myenv.config["SSH_Agent"]:
                j.core.myenv.sshagent.key_default_name  # means we will load ssh-agent and help user to load it properly

        if threebot:
            pips_level = 3
        else:
            pips_level = 0

        BaseInstaller.install(sandboxed=sandboxed, force=force, branch=branch, pips_level=pips_level)

        Tools.file_touch(os.path.join(j.core.myenv.config["DIR_BASE"], "lib/jumpscale/__init__.py"))

        self.repos_get(pull=gitpull, branch=branch)
        self.repos_link()
        self.cmds_link()

        script = """
        set -e
        cd {DIR_BASE}
        source env.sh
        mkdir -p {DIR_BASE}/openresty/nginx/logs
        mkdir -p {DIR_BASE}/var/log
        kosmos 'j.data.nacl.configure(generate=True,interactive=False)'
        kosmos 'j.core.installer_jumpscale.remove_old_parts()'
        # kosmos --instruct=/tmp/instructions.toml
        kosmos 'j.core.tools.pprint("JumpscaleX init step for encryption OK.")'
        """
        Tools.execute(script, die_if_args_left=True)

        if threebot:
            Tools.execute_jumpscale("j.servers.threebot.start(background=True)")
            timestop = time.time() + 240.0
            ok = False
            while ok == False and time.time() < timestop:
                if j.core.myenv.db.get("threebot.started") == b"1":
                    ok = True
                    break
                else:
                    print(" - threebot starting")
                    time.sleep(1)

            print(" - Threebot stopped")
            if not ok:
                raise Tools.exceptions.Base("could not stop threebot after install")
            Tools.execute("j.servers.threebot.default.stop()", die=False, jumpscale=True, showout=False)
            time.sleep(2)
            Tools.execute("j.servers.threebot.default.stop()", die=True, jumpscale=True)

    def remove_old_parts(self):
        tofind = ["DigitalMe", "Jumpscale", "ZeroRobot"]
        for part in sys.path:
            if Tools.exists(part) and os.path.isdir(part):
                # print(" - REMOVE OLD PARTS:%s" % part)
                for item in os.listdir(part):
                    for item_tofind in tofind:
                        toremove = os.path.join(part, item)
                        if (
                            item.find(item_tofind) != -1
                            and toremove.find("sandbox") == -1
                            and toremove.find("github") == -1
                        ):
                            j.core.tools.log("found old jumpscale item to remove:%s" % toremove)
                            Tools.delete(toremove)
                        if item.find(".pth") != -1:
                            out = ""
                            for line in Tools.file_text_read(toremove).split("\n"):
                                if line.find("threefoldtech") == -1:
                                    out += "%s\n" % line
                            try:
                                Tools.file_write(toremove, out)
                            except:
                                pass
                            # Tools.shell()
        tofind = ["js_", "js9"]
        for part in os.environ["PATH"].split(":"):
            if Tools.exists(part):
                for item in os.listdir(part):
                    for item_tofind in tofind:
                        toremove = os.path.join(part, item)
                        if (
                            item.startswith(item_tofind)
                            and toremove.find("sandbox") == -1
                            and toremove.find("github") == -1
                        ):
                            j.core.tools.log("found old jumpscale item to remove:%s" % toremove)
                            Tools.delete(toremove)

    # def prebuilt_copy(self):
    #     """
    #     copy the prebuilt files to the {DIR_BASE} location
    #     :return:
    #     """
    #     self.cmds_link(generate_js=False)
    #     # why don't we use our primitives here?
    #     Tools.execute("cp -a {DIR_CODE}/github/threefoldtech/sandbox_threebot_linux64/* /")
    #     # -a won't copy hidden files
    #     Tools.execute("cp {DIR_CODE}/github/threefoldtech/sandbox_threebot_linux64/.startup.toml /")
    #     Tools.execute("source {DIR_BASE}/env.sh; kosmos 'j.data.nacl.configure(generate=True,interactive=False)'")
    #
    def repos_get(self, pull=False, prebuilt=False, branch=None, reset=False):
        assert not prebuilt  # not supported yet
        if prebuilt:
            GITREPOS["prebuilt"] = PREBUILT_REPO

        for NAME, d in GITREPOS.items():
            GITURL, BRANCH, RPATH, DEST = d
            if branch:
                C = f"""git ls-remote --heads {GITURL} {branch}"""
                _, out, _ = Tools.execute(C, showout=False, die_if_args_left=True, interactive=False)
                if out:
                    BRANCH = branch

            try:
                dest = Tools.code_github_get(url=GITURL, rpath=RPATH, branch=BRANCH, pull=pull, reset=reset)
            except Exception as e:
                r = Tools.code_git_rewrite_url(url=GITURL, ssh=False)
                Tools.code_github_get(url=GITURL, rpath=RPATH, branch=BRANCH, pull=pull)

        if prebuilt:
            self.prebuilt_copy()

    def repos_link(self):
        """
        link the jumpscale repo's to right location in sandbox
        :return:
        """

        for NAME, d in GITREPOS.items():
            GITURL, BRANCH, PATH, DEST = d

            (host, type, account, repo, url2, branch2, GITPATH, RPATH, port) = Tools.code_giturl_parse(url=GITURL)
            srcpath = "%s/%s" % (GITPATH, PATH)
            if not Tools.exists(srcpath):
                raise Tools.exceptions.Base("did not find:%s" % srcpath)

            DESTPARENT = os.path.dirname(DEST.rstrip())

            script = f"""
            set -e
            rm -f {DEST}
            mkdir -p {DESTPARENT}
            ln -s {GITPATH}/{PATH} {DEST}
            """
            Tools.execute(script, die_if_args_left=True)

    def cmds_link(self, generate_js=True):
        _, _, _, _, loc = Tools._code_location_get(repo="jumpscaleX_core/", account="threefoldtech")
        for src in os.listdir("%s/cmds" % loc):
            src2 = os.path.join(loc, "cmds", src)
            dest = "%s/bin/%s" % (MyEnv.config["DIR_BASE"], src)
            if not os.path.exists(dest):
                Tools.link(src2, dest, chmod=770)
        Tools.link("%s/install/jsx.py" % loc, "{DIR_BASE}/bin/jsx", chmod=770)
        if generate_js:
            Tools.execute("cd {DIR_BASE};source env.sh;js_init generate", interactive=False, die_if_args_left=True)
