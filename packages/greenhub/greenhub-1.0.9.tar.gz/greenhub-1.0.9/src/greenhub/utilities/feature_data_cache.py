import os
import shutil
import tempfile
import pandas as pd
from typing import Optional


TEMP_DIR_DEFAULT_NAME = 'greenhub_feature_data_temp_8410_'


class FeatureDataCache:
    """
    Functionalities that need to repeatedly load feature data from an API can cache this data
    using a `FeatureDataCache` object, thereby avoiding unnecessary reloading.
    The stored data is saved in the background in a dedicated temp directory and remains available even after closing
    the terminal, environment, etc. The cached data is only lost upon restarting the computer.
    """

    def __init__(self):
        """
        Initializes the `FeatureDataCache` instance by setting up the necessary dedicated temp directory,
        where the given data will be cached as csv files.

        Special/Workaround: `tempfile.mkdtemp(...)` creates a temp directory with a specific prefix
        and a random code as the name, ensuring the folder is unique. However, since we want to access
        the data even after the program ends and have no way to securely store this name, we first search
        in the computer's `temp` directory for a directory starting with our `TEMP_DIR_DEFAULT_NAME` prefix.
        """

        self.system_temp_dir_path = tempfile.gettempdir()

        # get greenhub temp dir path, create if not already exists
        self.greenhub_temp_dir_path = None
        for item in os.listdir(self.system_temp_dir_path):
            item_path = f'{self.system_temp_dir_path}/{item}'
            if os.path.isdir(item_path) and item.startswith(TEMP_DIR_DEFAULT_NAME):
                # greenhub temp dir already exists
                self.greenhub_temp_dir_path = item_path
                break
        if self.greenhub_temp_dir_path is None:
            # create new greenhub temp dir
            self.greenhub_temp_dir_path = tempfile.mkdtemp(prefix=TEMP_DIR_DEFAULT_NAME)

    def save_feature_data(self, feature_file_path: str, data: pd.DataFrame):
        """
        Caches the given (feature) `data` as a csv file in the dedicated temp directory.

        :param feature_file_path: the relative, unique path within the temp directory where the data should be stored.
        :data: the (feature) data to be cached.
        """

        file_name = os.path.basename(feature_file_path)
        dir_path = os.path.join(
            self.greenhub_temp_dir_path,
            os.path.dirname(feature_file_path)
        )
        os.makedirs(dir_path, exist_ok=True)
        data.to_csv(os.path.join(dir_path, file_name), index=False)

    def load_feature_data(self, feature_file_path: str) -> Optional[pd.DataFrame]:
        """
        Loads cached (feature) `data` and returns is as a pandas dataframe.
        The stored data is uniquely identified by the passed `feature_file_path`.

        :param feature_file_path: the relative path within the temp directory which uniquely identified the stored data.
        :returns: the loaded data; None is returned if no data is found.
        """

        feature_file_path = os.path.join(
            self.greenhub_temp_dir_path,
            feature_file_path
        )
        if not os.path.exists(feature_file_path):
            return None
        return pd.read_csv(feature_file_path)

    def reset(self):
        """
        Reset entire cache. All cached data is deleted.
        """
        shutil.rmtree(self.greenhub_temp_dir_path)
        self.__init__()

