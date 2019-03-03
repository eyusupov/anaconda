from containers import ContainersModule
from pyanaconda.modules.common import init

init()
security_module = ContainersModule()
security_module.run()
