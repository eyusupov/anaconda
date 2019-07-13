from pyanaconda.dbus.interface import dbus_interface
from pyanaconda.dbus.property import emits_properties_changed
from pyanaconda.dbus.typing import *  # pylint: disable=wildcard-import
from pyanaconda.modules.common.base import KickstartModuleInterface
from pyanaconda.modules.common.constants.services import CONTAINERS


@dbus_interface(CONTAINERS.interface_name)
class ContainersInterface(KickstartModuleInterface):
    """DBus interface for Containers module."""

    def connect_signals(self):
        """Connect signals to the implementation."""
        super().connect_signals()
        self.implementation.search_registries_changed.connect(self.changed('SearchRegistries'))
        self.implementation.insecure_registries_changed.connect(self.changed('InsecureRegistries'))
        self.implementation.storage_changed.connect(self.changed('Storage'))
        self.implementation.boot_image_changed.connect(self.changed('BootImage'))
        self.implementation.boot_container_options_changed.connect(self.changed('BootContainerOptions'))

    @property
    def SearchRegistries(self) -> List[Str]:
        return self.implementation.search_registries

    @emits_properties_changed
    def SetSearchRegistries(self, registries: List[Str]):
        self.implementation.set_search_registries(registries)

    @property
    def InsecureRegistries(self) -> List[Str]:
        return self.implementation.insecure_registries

    @emits_properties_changed
    def SetInsecureRegistries(self, registries: List[Str]):
        self.implementation.set_insecure_registries(registries)

    @property
    def Storage(self) -> Dict[Str, Str]:
        return self.implementation.storage

    @emits_properties_changed
    def SetStorage(self, storage: Dict[Str, Str]):
        self.implementation.set_storage(storage)

    @property
    def BootImage(self) -> Str:
        return self.implementation.boot_image

    @emits_properties_changed
    def SetBootImage(self, boot_image: Str):
        self.implementation.set_boot_image(boot_image)

    @property
    def BootContainerOptions(self) -> List[Str]:
        return self.implementation.boot_container_options

    @emits_properties_changed
    def SetBootContainerOptions(self, boot_container_options: List[Str]):
        self.implementation.set_boot_container_options(boot_container_options)

    @property
    def BootContainerMountPoint(self) -> Str:
        return self.implementation.boot_container_mount_point

    @emits_properties_changed
    def SetBootContainerMountPoint(self, mount_point: Str):
        self.implementation.set_boot_container_mount_point(mount_point)

    def ConfigureRegistries(self):
        self.implementation.configure_registries()

    def ConfigureStorage(self):
        self.implementation.configure_storage()

    def PullBootImage(self):
        self.implementation.pull_boot_image()

    def SetupBootContainer(self):
        self.implementation.setup_boot_container()

    def CommitBootContainer(self):
        self.implementation.commit_boot_container()
