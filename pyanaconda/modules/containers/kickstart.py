#
# Kickstart handler for the containers.
#

from pyanaconda.core.kickstart import VERSION, KickstartSpecification, commands as COMMANDS


class ContainersKickstartSpecification(KickstartSpecification):

    version = VERSION
    commands = {
        "container_registries": COMMANDS.ContainerRegistries,
        "container_storage": COMMANDS.ContainerStorage,
        "container_boot_image": COMMANDS.ContainerBootImage,
        "container_boot_options": COMMANDS.ContainerBootOptions
    }
