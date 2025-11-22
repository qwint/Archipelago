from worlds.LauncherComponents import Component, components, Type
from worlds.LauncherComponents import launch as launch_component


def launch_client(*args):
    from .fancy_client import run_fancy_textclient
    launch_component(run_fancy_textclient, name="Fancy Client", args=args)


components.append(Component("Fancy Client", func=launch_client, component_type=Type.CLIENT))
