DEFAULT_BRANCH = "unstable"
GITREPOS = {}

GITREPOS["builders_extra"] = [
    "https://github.com/threefoldtech/jumpscaleX_builders",
    "%s" % DEFAULT_BRANCH,
    "JumpscaleBuildersExtra",
    "{DIR_BASE}/lib/jumpscale/JumpscaleBuildersExtra",
]

GITREPOS["installer"] = [
    "https://github.com/threefoldtech/jumpscaleX_core",
    "%s" % DEFAULT_BRANCH,
    "install",  # directory in the git repo
    "{DIR_BASE}/installer",
]
GITREPOS["core"] = [
    "https://github.com/threefoldtech/jumpscaleX_core",
    "%s" % DEFAULT_BRANCH,
    "JumpscaleCore",
    "{DIR_BASE}/lib/jumpscale/Jumpscale",
]
GITREPOS["home"] = ["https://github.com/threefoldtech/home", "master", "", "{DIR_BASE}/lib/jumpscale/home"]

GITREPOS["builders"] = [
    "https://github.com/threefoldtech/jumpscaleX_builders",
    "%s" % DEFAULT_BRANCH,
    "JumpscaleBuilders",
    "{DIR_BASE}/lib/jumpscale/JumpscaleBuilders",
]

GITREPOS["builders_community"] = [
    "https://github.com/threefoldtech/jumpscaleX_builders",
    "%s" % DEFAULT_BRANCH,
    "JumpscaleBuildersCommunity",
    "{DIR_BASE}/lib/jumpscale/JumpscaleBuildersCommunity",
]

GITREPOS["libs_extra"] = [
    "https://github.com/threefoldtech/jumpscaleX_libs_extra",
    "%s" % DEFAULT_BRANCH,
    "JumpscaleLibsExtra",
    "{DIR_BASE}/lib/jumpscale/JumpscaleLibsExtra",
]
GITREPOS["libs"] = [
    "https://github.com/threefoldtech/jumpscaleX_libs",
    "%s" % DEFAULT_BRANCH,
    "JumpscaleLibs",
    "{DIR_BASE}/lib/jumpscale/JumpscaleLibs",
]
GITREPOS["threebot"] = [
    "https://github.com/threefoldtech/jumpscaleX_threebot",
    "%s" % DEFAULT_BRANCH,
    "ThreeBotPackages",
    "{DIR_BASE}/lib/jumpscale/threebot_packages",
]

# GITREPOS["tutorials"] = [
#     "https://github.com/threefoldtech/jumpscaleX_libs",
#     "%s" % DEFAULT_BRANCH,
#     "tutorials",
#     "{DIR_BASE}/lib/jumpscale/tutorials",
# ]
#
# GITREPOS["kosmos"] = [
#     "https://github.com/threefoldtech/jumpscaleX_threebot",
#     "%s" % DEFAULT_BRANCH,
#     "kosmos",
#     "{DIR_BASE}/lib/jumpscale/kosmos",
# ]
#
# PREBUILT_REPO = ["https://github.com/threefoldtech/sandbox_threebot_linux64", "master", "", "not used"]
