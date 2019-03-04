from .containers import ContainersModule
from pyanaconda.modules.common import init

init()
module = ContainersModule()
module.run()
