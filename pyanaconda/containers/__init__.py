# TODO: implement it as a Kickstart module
from configparser import ConfigParser
from core import util
import json

def configure_registries(urls, path='/etc/containers/registries.conf'):
    # TODO: keep formatting
    config = ConfigParser()
    config.read(path)
    config.set('registries.search', 'registries', json.dumps(urls))
    with open(path, 'w') as f:
        config.write(f)

def configure_storage(options, path='/etc/containers/storage.conf'):
    # TODO: keep formatting
    config = ConfigParser()
    config.read(path)
    
    for key, value in options.items():
        section, _sep, key = key.rpartition('.')
        section = "storage." + section if section else "storage"
        config.set(section, key, json.dumps(value))

    with open(path, 'w') as f:
        config.write(f)

def create(image, container, options):
    return util.execWithCapture('buildah', 'from', '--name', container, *options, image)

def mount(container):
    return util.execWithCapture('buildah', 'mount', container)

def unmount(container):
    util.execWithRedirect('buildah', 'umount', container)

def run(container, options, command, args):
    return util.execWithCapture('buildah', 'run', *options, container, command, args)

def commit(container, image):
    return util.execWithCapture('buildah', 'commit', '--rm', container, image)
