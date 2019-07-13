from pyanaconda.dbus import DBus
from pyanaconda.core.signal import Signal
from pyanaconda.core import util
from pyanaconda.modules.common.base import KickstartModule
from pyanaconda.modules.common.constants.services import CONTAINERS
from .kickstart import ContainersKickstartSpecification
from .containers_interface import ContainersInterface
import json
import toml

from pyanaconda.anaconda_loggers import get_module_logger
log = get_module_logger(__name__)


class ContainersModule(KickstartModule):
    """ Boot to container module. """

    def __init__(self):
        super().__init__()

        self.search_registries_changed = Signal()
        self._search_registries = []

        self.insecure_registries_changed = Signal()
        self._insecure_registries = []

        self.storage_changed = Signal()
        self._storage = {}

        self.boot_image_changed = Signal()
        self._boot_image = ""

        self.boot_container_options_changed = Signal()
        self._boot_container_options = []

        self._mount_point = ""

    def publish(self):
        """Publish the module."""

        DBus.publish_object(CONTAINERS.object_path, ContainersInterface(self))
        DBus.register_service(CONTAINERS.service_name)

    @property
    def kickstart_specification(self):
        """Return the kickstart specification."""
        return ContainersKickstartSpecification

    def process_kickstart(self, data):
        """Process the kickstart data."""
        log.debug("Processing kickstart data...")
        if data.containerregistries.search:
            self.set_search_registries(data.containerregistries.search)

        if data.containerregistries.insecure:
            self.set_insecure_registries(data.containerregistries.insecure)

        if data.containerstorage.seen:
            self.set_storage(data.containerstorage.options)

        if data.containerbootimage.seen:
            self.set_boot_image(data.containerbootimage.image)

        if data.containerbootoptions.seen:
            self.set_boot_container_options(data.containerbootoptions.options)

    def generate_kickstart(self):
        """Return the kickstart string."""
        log.debug("Generating kickstart data...")
        data = self.get_kickstart_handler()
        return str(data)

    @property
    def search_registries(self):
        return self._search_registries

    def set_search_registries(self, registries):
        self._search_registries = registries
        self.search_registries_changed.emit()

    @property
    def insecure_registries(self):
        return self._insecure_registries

    def set_insecure_registries(self, registries):
        self._insecure_registries = registries
        self.insecure_registries_changed.emit()

    @property
    def storage(self):
        return self._storage

    def set_storage(self, storage):
        self._storage = dict(storage)
        self.storage_changed.emit()

    @property
    def boot_image(self):
        return self._boot_image

    def set_boot_image(self, boot_image):
        self._boot_image = boot_image
        self.boot_image_changed.emit()

    @property
    def boot_container_options(self):
        return self._boot_container_options

    def set_boot_container_options(self, boot_container_options):
        self._boot_container_options = list(boot_container_options)
        self.boot_container_options_changed.emit()

    def configure_registries(self, path='/etc/containers/registries.conf'):
        # TODO: keep formatting
        config = toml.load(path)

        if self.search_registries:
            config['registries']['search']['registries'] = self.search_registries

        if self.insecure_registries:
            config['registries']['insecure']['registries'] = self.insecure_registries

        with open(path, 'w') as f:
            toml.dump(config, f)

    def configure_storage(self, path='/etc/containers/storage.conf'):
        # TODO: keep formatting
        config = toml.load(path)

        for key, value in self.storage.items():
            sections, _sep, key = key.rpartition('.')
            parent = config['storage']
            if sections:
                for section in sections.split('.'):
                    parent = parent[section]
            parent[key] = value

        with open(path, 'w') as f:
            toml.dump(config, f)

    def pull_boot_image(self):
        # TODO: implement as payload
        self.pull(self.boot_image)

    def setup_boot_container(self):
        # TODO: move to constants
        self.create(self.boot_image, 'boot-container', self.boot_container_options)
        self._mount_point = self.mount('boot-container')

    @property
    def boot_container_mount_point(self):
        return self._mount_point

    def set_boot_container_mount_point(self, mount_point):
        self._mount_point = mount_point

    def commit_boot_container(self):
        # TODO: move to constants
        self.unmount('boot-container')
        # TODO: make configurable
        self.commit('boot-container', 'boot:latest')

    def pull(self, image):
        return util.execWithCapture('buildah', ['pull', image])

    def create(self, image, container, options):
        return util.execWithCapture('buildah', ['from', '--name', container] + options + [image])

    def mount(self, container):
        return util.execWithCapture('buildah', ['mount', container])

    def unmount(self, container):
        util.execWithRedirect('buildah', ['umount', container])

    def container_run(self, container, options, command, args):
        return util.execWithCapture('buildah', ['run'] + options + [container, command] + args)

    def commit(self, container, image):
        return util.execWithCapture('buildah', ['commit', '--rm', container, image])
