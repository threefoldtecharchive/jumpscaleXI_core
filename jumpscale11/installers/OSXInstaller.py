from .BaseInstaller import BaseInstaller


class OSXInstaller:
    @staticmethod
    def do_all(executor, pips_level=3):
        j.core.myenv.init()
        j.core.tools.log("installing OSX version")
        OSXInstaller.base(executor)
        BaseInstaller.pips_install(executor, pips_level=pips_level)

    @staticmethod
    def base(executor):
        OSXInstaller.brew_install(executor)
        if (
            not executor.cmd_installed("curl")
            or not executor.cmd_installed("unzip")
            or not executor.cmd_installed("rsync")
        ):
            script = """
            brew install curl unzip rsync tmux libssh2
            """
            # graphviz #TODO: need to be put elsewhere but not in baseinstaller
            executor.execute(script, replace=True)
        BaseInstaller.pips_install(executor, ["click"])  # TODO: *1

    @staticmethod
    def brew_install():
        if not j.core.tools.cmd_installed("brew"):
            cmd = 'ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"'
            j.core.tools.execute(cmd, interactive=True)

    @staticmethod
    def brew_uninstall():
        j.core.myenv.init()
        cmd = 'ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/uninstall)"'
        j.core.tools.execute(cmd, interactive=True)
        toremove = """
        sudo rm -rf /usr/local/.com.apple.installer.keep
        sudo rm -rf /usr/local/include/
        sudo rm -rf /usr/local/etc/
        sudo rm -rf /usr/local/var/
        sudo rm -rf /usr/local/FlashcardService/
        sudo rm -rf /usr/local/texlive/
        """
        j.core.tools.execute(toremove, interactive=True)

