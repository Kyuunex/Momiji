from appdirs import AppDirs
from pathlib import Path
import os


class FakeDirs:
    def __init__(self, data_dir):
        self.user_data_dir = data_dir
        self.user_cache_dir = data_dir + "/cache"
        self.user_log_dir = data_dir + "/logs"


if os.environ.get('MOMIJI_DATA_DIR'):
    momiji_data_dir = os.environ.get('MOMIJI_DATA_DIR')
    dirs = FakeDirs(momiji_data_dir)
else:
    dirs = AppDirs("Momiji", "Kyuunex")

user_extensions_directory = dirs.user_data_dir + "/user_extensions"
bridged_extensions_directory = dirs.user_data_dir + "/bridged_extensions"
exports_directory = dirs.user_data_dir + "/exports"
art_directory = dirs.user_data_dir + "/art"

Path(dirs.user_data_dir).mkdir(parents=True, exist_ok=True)
Path(dirs.user_cache_dir).mkdir(parents=True, exist_ok=True)
Path(dirs.user_log_dir).mkdir(parents=True, exist_ok=True)
Path(user_extensions_directory).mkdir(parents=True, exist_ok=True)
Path(bridged_extensions_directory).mkdir(parents=True, exist_ok=True)
Path(exports_directory).mkdir(parents=True, exist_ok=True)
# Path(art_directory).mkdir(parents=True, exist_ok=True)

database_file = dirs.user_data_dir + "/maindb.sqlite3"
