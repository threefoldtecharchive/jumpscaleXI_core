from jumpscale11.core import j


class UbuntuInstaller:
    @staticmethod
    def do_all(executor, prebuilt=False, pips_level=3):
        j.core.tools.log("installing Ubuntu version")

        UbuntuInstaller.ensure_version()
        UbuntuInstaller.base()
        # UbuntuInstaller.ubuntu_base_install()
        if not prebuilt:
            UbuntuInstaller.python_dev_install()
        UbuntuInstaller.apts_install()
        if not prebuilt:
            BaseInstaller.pips_install(pips_level=pips_level)

    @staticmethod
    def ensure_version():
        j.core.myenv.init()
        if not os.path.exists("/etc/lsb-release"):
            raise j.core.tools.logexceptions.Base("Your operating system is not supported")

        return True

    @staticmethod
    def base():
        j.core.myenv.init()

        if j.core.myenv.state_get("base"):
            return

        rc, out, err = j.core.tools.logexecute("lsb_release -a")
        if out.find("Ubuntu 18.04") != -1:
            bionic = True
        else:
            bionic = False

        if bionic:
            script = """
            if ! grep -Fq "deb http://mirror.unix-solutions.be/ubuntu/ bionic" /etc/apt/sources.list; then
                echo >> /etc/apt/sources.list
                echo "# Jumpscale Setup" >> /etc/apt/sources.list
                echo deb http://mirror.unix-solutions.be/ubuntu/ bionic main universe multiverse restricted >> /etc/apt/sources.list
            fi
            """
            j.core.tools.logexecute(script, interactive=True, die=False)

        script = """
        apt-get update
        apt-get install -y mc wget python3 git tmux telnet
        set +ex
        apt-get install python3-distutils -y
        set -ex
        apt-get install python3-psutil -y
        apt-get install -y curl rsync unzip
        locale-gen --purge en_US.UTF-8
        apt-get install python3-pip -y
        apt-get install -y redis-server
        apt-get install locales -y

        """
        j.core.tools.logexecute(script, interactive=True)

        if bionic and not DockerFactory.indocker():
            UbuntuInstaller.docker_install()

        j.core.myenv.state_set("base")

    @staticmethod
    def docker_install():
        if j.core.myenv.state_get("ubuntu_docker_install"):
            return
        script = """
        apt-get update
        apt-get upgrade -y --force-yes
        apt-get install sudo python3-pip  -y
        pip3 install pudb
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
        add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
        apt-get update
        sudo apt-get install docker-ce -y
        """
        j.core.tools.logexecute(script, interactive=True)
        j.core.myenv.state_set("ubuntu_docker_install")

    @staticmethod
    def python_dev_install():
        if j.core.myenv.state_get("python_dev_install"):
            return

        j.core.tools.log("installing jumpscale tools")

        script = """
        cd /tmp
        apt-get install -y build-essential
        #apt-get install -y python3.8-dev


        """
        rc, out, err = j.core.tools.logexecute(script, interactive=True, timeout=300)
        if rc > 0:
            # lets try other time
            rc, out, err = j.core.tools.logexecute(script, interactive=True, timeout=300)
        j.core.myenv.state_set("python_dev_install")

    @staticmethod
    def apts_list():
        return [
            "iproute2",
            "python-ufw",
            "ufw",
            "libpq-dev",
            "iputils-ping",
            "net-tools",
            "libgeoip-dev",
            "libcapnp-dev",
            "graphviz",
            "libssl-dev",
            "cmake",
            "fuse",
        ]

    @staticmethod
    def apts_install():
        for apt in UbuntuInstaller.apts_list():
            if not j.core.myenv.state_get("apt_%s" % apt):
                command = "apt-get install -y %s" % apt
                j.core.tools.logexecute(command, die=True)
                j.core.myenv.state_set("apt_%s" % apt)
