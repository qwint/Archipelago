"""
Animal Well Archipelago Client
"""

import ModuleUpdate
import Utils
from worlds.animal_well.client import launch

ModuleUpdate.update()

if __name__ == "__main__":
    Utils.init_logging("AnimalWellClient", exception_logger="Client")
    launch()
