from worlds.LauncherComponents import Component, components, Type, launch_subprocess


def launch_client(*args):
    try:
        from worlds.LauncherComponents import launch
        from .fancy_client import run_fancy_textclient
        launch(run_fancy_textclient, name="Fancy Client", args=args)
    except ImportError:
        launch_if_needed(*args)


# TODO remove eventually once 0.6.0 is old enough
def launch_if_needed(*args):
    import sys
    from .fancy_client import run_fancy_textclient
    if not sys.stdout or "--nogui" not in sys.argv:
        launch_subprocess(run_fancy_textclient, name="Fancy Client", args=args)
    else:
        run_fancy_textclient(*args)


components.append(Component("Fancy Client", None, func=launch_client, component_type=Type.CLIENT))
