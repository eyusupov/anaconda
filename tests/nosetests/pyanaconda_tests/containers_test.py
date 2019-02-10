from pyanaconda import containers
from configparser import ConfigParser
import textwrap
import json
import unittest
import tempfile
import shutil
import os

class ContainersTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.registries_conf = self.tmpdir + "/registries.conf"
        self.storage_conf = self.tmpdir + "/storage.conf"

        with open( self.registries_conf, 'w') as f:
            f.write(textwrap.dedent("""\
                    [registries.search]
                    registries = ["quay.io"]
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
        #shutil.rmtree(self.tmpdir)
        pass

    def configure_registries_test(self):
        registries = ['registry.fedoraproject.org', 'registry.centos.org']

        containers.configure_registries(registries, path=self.registries_conf)
        
        config = ConfigParser()
        config.read(self.registries_conf)

        self.assertEqual(config.get('registries.search', 'registries'), json.dumps(registries))
        self.assertEqual(config.get('registries.block', 'registries'), json.dumps(['docker.io']))

    def configure_storage_test(self):
        additional_stores = [
            '/net/172.20.17.2/storage',
            '/net/172.20.17.3/storage'
        ]

        options = {
            'graphroot': '/storage',
            'options.size': '10G',
            'options.additionalimagestores': additional_stores
        }

        containers.configure_storage(options, path=self.storage_conf)
        
        config = ConfigParser()
        config.read(self.storage_conf)

        self.assertEqual(config.get('storage', 'graphroot'), '"/storage"')
        self.assertEqual(config.get('storage', 'runroot'), '"/var/run/containers/storage"')
        self.assertEqual(config.get('storage.options', 'size'), '"10G"')
        self.assertEqual(config.get('storage.options', 'additionalimagestores'), json.dumps(additional_stores))
