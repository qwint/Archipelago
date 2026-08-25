from worlds.LauncherComponents import Component, components


def run_client(*args):
    assert len(args) == 1, "must call track_room with a room suuid argument"
    suuid, = args
    from .client import track_suuid
    track_suuid(suuid)

components.append(Component(
    "track_room",
    description="call with a webhost tracker suuid to use UT on the entire room",
    func=run_client,
))
