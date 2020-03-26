from jumpscale11.core import JumpscaleCore


class j:
    _init = False
    core = JumpscaleCore()


if not j._init:
    print("INIT CORE INIT")
    j.core._j = j
    j.shell = j.core.tools.shell
    j.exceptions = j.core.exceptions
    j._init = True
    if j.core.tools.tcp_port_connection_test("localhost", 6379):
        j.core.myenv._redis_active = True
