import sys

# import functools
# from Jumpscale import j


# from baseclasses.JSBase import JSBase
# from baseclasses.JSAttr import JSAttr
#
#
# class ClassTest(JSBase, JSAttr):
#     __properties = {
#         "date1": j.data.types.date,
#         "date2": j.data.types.date,
#         "date3": j.data.types.date,
#         "date4": j.data.types.date,
#         "int1": j.data.types.int,
#         "float1": j.data.types.float,
#         "string1": j.data.types.string,
#     }
#
#     @functools.lru_cache(maxsize=5)
#     def test(self, a):
#         return a
#
#
# c = ClassTest()
# c.test(a="1")

from jumpscale11 import j

j.core.myenv

# from jumpscale11.data.hash import *

from jumpscale11.installers.Nix import Nix

n = Nix()
n.install()

# j.core.codetools.init_generate(
#     "/Users/despiegk/sandbox/code/github/threefoldtech/jumpscaleXI_core/jumpscale11/data/serializers"
# )
