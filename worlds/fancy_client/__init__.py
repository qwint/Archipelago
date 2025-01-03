from worlds.LauncherComponents import Component, components, Type, launch_subprocess


def launch_client():
    import sys
    from .fancy_client import run_fancy_textclient
    if not sys.stdout or "--nogui" not in sys.argv:
        launch_subprocess(run_fancy_textclient, name="Fancy Client")
    else:
        run_fancy_textclient()


components.append(Component("Fancy Client", None, func=launch_client, component_type=Type.CLIENT))
