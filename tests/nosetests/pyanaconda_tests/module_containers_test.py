import toml
import textwrap
import json
import unittest
from unittest.mock import Mock
import tempfile
import shutil

from pyanaconda.modules.common.constants.services import CONTAINERS
from pyanaconda.modules.containers.containers import ContainersModule
from pyanaconda.modules.containers.containers_interface import ContainersInterface
from tests.nosetests.pyanaconda_tests import check_kickstart_interface, check_dbus_property

STORAGE = {
    'runroot': '/var/lib/containers',
    'graphroot': '/var/run/containers',
    'driver': 'overlay'
}

BOOT_CONTAINER_OPTIONS = ['-v', '/boot:/boot', '-v', '/etc:/etc']

class ContainersInterfaceTestCase(unittest.TestCase):
    """Test DBus interface for the containers module."""
    def setUp(self):
        self.module = ContainersModule()
        self.interface = ContainersInterface(self.module)

        # Connect to the properties changed signal.
        self.callback = Mock()
        self.interface.PropertiesChanged.connect(self.callback)

    def kickstart_properties_test(self):
        self.assertEqual(self.interface.KickstartCommands,
                ["container_registries",
                 "container_storage",
                 "container_boot_image",
                 "container_boot_options"])
        self.assertEqual(self.interface.KickstartSections, [])
        self.assertEqual(self.interface.KickstartAddons, [])
        self.callback.assert_not_called()

    def default_property_values_test(self):
        self.assertEqual(self.interface.SearchRegistries, [])
        self.assertEqual(self.interface.InsecureRegistries, [])
        self.assertEqual(self.interface.Storage, {})
        self.assertEqual(self.interface.BootImage, '')
        self.assertEqual(self.interface.BootContainerOptions, [])

    def set_insecure_registries_test(self):
        registries = ['registry.fedoraproject.org', 'quay.io']
        self.interface.SetInsecureRegistries(registries)
        self.assertEqual(self.interface.InsecureRegistries, registries)
        self.callback.assert_called_once_with(CONTAINERS.interface_name, {'InsecureRegistries': registries}, [])

    def set_search_registries_test(self):
        registries = ['registry.fedoraproject.org', 'quay.io']
        self.interface.SetSearchRegistries(registries)
        self.assertEqual(self.interface.SearchRegistries, registries)
        self.callback.assert_called_once_with(CONTAINERS.interface_name, {'SearchRegistries': registries}, [])

    def set_storage_test(self):
        self.interface.SetStorage(STORAGE)
        self.assertEqual(self.interface.Storage, STORAGE)
        self.callback.assert_called_once_with(CONTAINERS.interface_name, {'Storage': STORAGE}, [])

    def set_boot_image_test(self):
        boot_image = 'boot-image'
        self.interface.SetBootImage(boot_image)
        self.assertEqual(self.interface.BootImage, boot_image)
        self.callback.assert_called_once_with(CONTAINERS.interface_name, {'BootImage': boot_image}, [])

    def set_boot_container_options_test(self):
        self.interface.SetBootContainerOptions(BOOT_CONTAINER_OPTIONS)
        self.assertEqual(self.interface.BootContainerOptions, BOOT_CONTAINER_OPTIONS)
        self.callback.assert_called_once_with(CONTAINERS.interface_name, {'BootContainerOptions': BOOT_CONTAINER_OPTIONS}, [])

    def ks_registries_test(self):
        self.interface.ReadKickstart('container_registries --search localhost:8000,registry.fedoraproject.org --insecure localhost:8000')
        self.assertEqual(self.interface.SearchRegistries, ['localhost:8000', 'registry.fedoraproject.org'])
        self.assertEqual(self.interface.InsecureRegistries, ['localhost:8000'])

    def ks_storage_test(self):
        self.interface.ReadKickstart('container_storage runroot=/var/lib/containers graphroot=/var/run/containers driver=overlay')
        self.assertEqual(self.interface.Storage, STORAGE)

    def ks_boot_image_test(self):
        self.interface.ReadKickstart('container_boot_image fedora:latest')
        self.assertEqual(self.interface.BootImage, 'fedora:latest')

    def ks_container_boot_options_test(self):
        self.interface.ReadKickstart('container_boot_options --nodefaults -- -v /boot:/boot -v /etc:/etc')
        self.assertEqual(self.interface.BootContainerOptions, BOOT_CONTAINER_OPTIONS)
        # TODO: handle nodefaults

class ContainersTestCase(unittest.TestCase):
    def setUp(self):
        # Create test configuration files
        self.tmpdir = tempfile.mkdtemp()
        self.registries_conf = self.tmpdir + "/registries.conf"
        self.storage_conf = self.tmpdir + "/storage.conf"
        self.module = ContainersModule()

        with open(self.registries_conf, 'w') as f:
            f.write(textwrap.dedent("""\
                    [registries.search]
                    registries = ["quay.io"]
                    [registries.insecure]
                    registries = ["localhost"]
                    [registries.block]
                    registries = ["docker.io"]
                    """))

        with open(self.storage_conf, 'w') as f:
            f.write(textwrap.dedent("""\
                    [storage]
                    driver = "overlay"
                    runroot = "/var/run/containers/storage"
                    graphroot = "/var/lib/containers/storage"
                    [storage.options]
                    additionalimagestores = []
                    size = ""
                    """))

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_configure_registries_test(self):
        self.module.set_search_registries(['registry.fedoraproject.org', 'localhost:5000'])
        self.module.set_insecure_registries(['localhost:5000'])

        self.module.configure_registries(path=self.registries_conf)

        config = toml.load(self.registries_conf)

        self.assertEqual(config['registries']['search']['registries'], self.module.search_registries)
        self.assertEqual(config['registries']['insecure']['registries'], self.module.insecure_registries)
        self.assertEqual(config['registries']['block']['registries'], ['docker.io'])

    def test_configure_storage_test(self):
        additional_stores = [
            '/net/172.20.17.2/storage',
            '/net/172.20.17.3/storage'
        ]

        self.module.set_storage({
            'graphroot': '/storage',
            'options.size': '10G',
            'options.additionalimagestores': additional_stores
        })

        self.module.configure_storage(path=self.storage_conf)

        config = toml.load(self.storage_conf)

        self.assertEqual(config['storage']['graphroot'], '/storage')
        self.assertEqual(config['storage']['runroot'], '/var/run/containers/storage')
        self.assertEqual(config['storage']['options']['size'], '10G')
        self.assertEqual(config['storage']['options']['additionalimagestores'], additional_stores)