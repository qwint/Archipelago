import os
import shutil

if __name__ == "__main__":
    with os.scandir("worlds") as it:
        for entry in it:
            if not entry.is_file() and entry.name not in ("generic", "_bizhawk", "v6"):
                # print(entry.path)
                shutil.rmtree(entry.path)
