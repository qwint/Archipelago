from worlds.LauncherComponents import launch_subprocess, components, Component, Type


def launch_client():
    """
    Launch the Animal Well Client
    """
    from .client import launch
    from CommonClient import gui_enabled
    if gui_enabled:
        launch_subprocess(launch, name="Spoiler Free Client")
    else:
        launch()


class SpoilerFreeWorld:
    pass


components.append(Component("Spoiler Free Client", None, func=launch_client, component_type=Type.CLIENT))
