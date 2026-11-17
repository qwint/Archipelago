from worlds.LauncherComponents import Component, components, Type


def func(*args):
    from . import run
    run.run(*args)


components.append(Component("Host Yaml", component_type=Type.TOOL, func=func, description="Runs a temporary Generate and Host on a single yaml"))
