import asyncio
import os
import shutil
import sys
import tempfile

import Main
import MultiServer
import Generate
import Utils

def run(*args):
    if args:
        # assume arg1 is a yaml path
        target = args[0]
    else:
        filetypes = (("Player Yaml", (".yaml", ".json")),)
        target = Utils.open_filename("Select Player Yaml", filetypes)
        assert target, "no file selected"
    # TODO: not hardcode this
#    target = "/home/qwint/.local/share/Archipelago/Players/Templates/APQuest.yaml"
    with tempfile.TemporaryDirectory() as d:
        args = Generate.mystery_argparse([])
        args.spoiler = 0
        args.player_files_path = os.path.join(d, "Players")
        args.outputpath = os.path.join(d, "output")
        os.makedirs(args.player_files_path)
        os.makedirs(args.outputpath)

        # copy target to args.player_file_path
        shutil.copy(target, args.player_files_path)

        multiworld = Main.main(*Generate.main(args))
        filepath = Utils.output_path(f"AP_{multiworld.seed_name}.zip")
        run_server(filepath)

def run_server(filepath):
    sys.argv[:] = sys.argv[:1]
    args = MultiServer.parse_args()
    args.multidata = filepath
    asyncio.run(MultiServer.main(args))

