# SPDX-License-Identifier: MIT

import os
import glob
import time
import logging
import pandas as pd
from asammdf import MDF
from pathlib import Path
import datetime

##########################################
# Create logger and logfile
##########################################
time_string = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
Path("./Logs").mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=os.path.join("./Logs", time_string + ".log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
    filemode="w",
)
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())


class Data:
    """
    A class to import bus data in mf4 format.

    Attributes
    ----------
    filedir : str
        Path of directory with all mf4 files.
    target : str
        Name of file containing target signal names (target.txt).
    modellib : str
        Path to the model library (not used here but retained
        as per original parameters).
    feature_engineering : bool
        Whether to apply feature engineering.
    blacklist : str
        File containing a textfile of signals not to be used.
    target_dir : str
        Folder which contains all target files.
    """

    def __init__(
        self,
        filedir,
        target,
        modellib=None,
        blacklist=None,
        targetdir=None,
    ):
        self.filedir = filedir
        self.target = target
        self.targetdir = targetdir
        self.df_result = None
        self.df_target = None
        self.df_features = None
        self.modellib = modellib
        self.blacklist = blacklist
        self.dict_files = {}

        if not self.filedir:
            logger.error("No file directory specified!")
            raise ValueError("No file directory specified!")

    ##########################################
    # Method to import all mf4 files from filedir and group them
    ##########################################
    def get_mf4files(self):
        """Method to import all mf4 files from filedir and group them"""
        self.__generate_mf4_file_dict()

    ##########################################
    # Method to import raw data from mf4-files in dataframes
    ##########################################
    def import_data(
        self,
        target,
        raster,
        fi_signalnumber=None,
        fi_signalthreshold=None,
        use_outer_join: bool = False,
        feature_engineering=None,
    ) -> pd.DataFrame | None:
        """Creates pandas data frame containing all bus data from mf4 files"""
        start_time = time.time()

        dict_signallist = {}

        list_blacklist = self.__create_blacklist()

        df_target, df_features = self.__load_files(
            target,
            raster,
            dict_signallist,
            list_blacklist,
            use_outer_join,
            feature_engineering,
            fi_signalnumber=fi_signalnumber,
            fi_signalthreshold=fi_signalthreshold,
        )

        logger.info(
            f"--- {time.time() - start_time} seconds to import filesfor target {target}---"
        )
        return df_target, df_features

    ##########################################
    # Create a list of signals that should not be read
    ##########################################
    def __create_blacklist(self):
        """Create a list of signals that should not be read"""
        blacklist = []
        if self.blacklist:
            if os.path.isfile(self.blacklist):
                with open(self.blacklist, "r") as filestream:
                    # Read all rows of the blacklist.
                    for line in filestream:
                        line = line.strip()
                        blacklist.append(line)
        return blacklist

    ##########################################
    # Creating the signal list with all relevant signals
    ##########################################
    def __create_signallist(
        self, target, fi_signalnumber, fi_signalthreshold, signal_names=None
    ):
        """Create the signal list with all relevant signals"""
        dict_signallist = {}
        # Case 1: Use `targetdir` if it exists
        if self.targetdir:
            logger.info("Using target directory: {}".format(self.targetdir))
            # Load all text files in the specified folder
            txt_files = glob.glob(os.path.join(self.targetdir, "*.txt"))
            for filename in txt_files:
                # Remove the file suffix
                filenameShort = Path(filename).stem
                if filenameShort == target:
                    # Read signal name columns
                    listFI = pd.read_csv(filename, sep=" ", header=None, usecols=[0])
                    # Create the list for signal selection
                    self.__calc_signallist(
                        fi_signalnumber,
                        fi_signalthreshold,
                        filename,
                        filenameShort,
                        listFI,
                        dict_signallist,
                    )

        else:
            logger.info(
                "No signal directory provided. Extracting signals from accumulated signal names."
            )
            if signal_names:
                signal_names = list(signal_names)
                # Check if the target signal exists
                if target in signal_names:
                    # Simulate feature importance data (if needed)
                    listFI = pd.DataFrame(
                        {
                            0: [1] * len(signal_names),  # Simulated importance values
                            1: signal_names,  # Signal names
                        }
                    )

                    # Create the signal list
                    filenameShort = target  # Use target name as key
                    self.__calc_signallist(
                        fi_signalnumber,
                        fi_signalthreshold,
                        target,  # Placeholder filename
                        filenameShort,
                        listFI,
                        dict_signallist,
                    )
                    logger.info(f"Signal list created: {dict_signallist}")
                else:
                    logger.error(
                        f"Target signal '{target}' not found in accumulated signal names."
                    )
            else:
                logger.error("No signal names available to extract signals from.")
        return dict_signallist

    ##########################################
    # Select signals used for signallist
    ##########################################
    def __calc_signallist(
        self,
        fi_signalnumber,
        fi_signalthreshold,
        filename,
        filenameShort,
        listFI,
        dict_signallist,
    ):


        if self.targetdir:
            # If targetdir is provided, include all signals from the targetdir file
            logger.info(
                f"Targetdir is provided. All signals in {filename} will be used!"
            )
            dict_signallist[filenameShort] = list(listFI[0])
        else:
            # If targetdir is not provided, include only the target signal
            logger.info(
                f"No targetdir provided. Only the target signal '{filenameShort}' will be used as the target."
            )
            dict_signallist[filenameShort] = [
                filenameShort
            ]  # Include only the target signal

    def __generate_mf4_file_dict(self):
        # If multiple file paths to directories are passed in `filedir`, they are read sequentially
        types = ("*.MF4", "*.mf4")

        filedirs = self.filedir.split(",")
        for dir in filedirs:
            dir = dir.strip()
            # Load all mf4 files in the respective folder
            mf4_files = []
            for type in types:
                mf4_files.extend(glob.glob(os.path.join(dir, type)))
            # Read all mf4 files in the folder
            for x in mf4_files:
                # Split the file name at "#" this can be modified to any other or no splitter at all
                key = os.path.basename(x).split("#")[0]
                group = self.dict_files.get(key, [])
                group.append(x)
                group_unique = list(set(group))
                self.dict_files[key] = group_unique
        for key, files in self.dict_files.items():
            logger.info(f"Key '{key}' has {len(files)} files: {files}")
        # Sort the dictionary by keys
        self.dict_files = dict(sorted(self.dict_files.items()))

    ##########################################
    # Read all mf4 files
    ##########################################
    def __load_files(
        self,
        target,
        raster,
        dict_signallist,
        list_blacklist,
        use_outer_join: bool,
        feature_engineering,
        fi_signalnumber=None,
        fi_signalthreshold=None,
        file_analysis=False,
    ) -> pd.DataFrame | None:
        """Read all mf4 files"""
        dataframes = []
        datafiles = []
        column_superset = set()
        is_ethernet = False

        accumulated_signal_names = (
            set()
        )  # Accumulate signal names across all dataframes

        # For each measurement period
        for key, value in self.dict_files.items():
            mf4_collection = []
            # For each file in the respective measurement period
            for file in value:
                logger.info(f"reading {file}")
                if not self.modellib:
                    self.__read_bus_files(
                        file,
                        mf4_collection,
                        list_blacklist,
                    )

            # Combine all read MF4 files
            if not self.modellib:
                if feature_engineering is not None:
                    with MDF.stack(mf4_collection) as mf4_stacked:
                        df_mf4_stacked = mf4_stacked.to_dataframe(
                            raster=raster,
                            time_from_zero=True,
                            reduce_memory_usage=True,
                            ignore_value2text_conversions=False,
                        )

                else:
                    with MDF.stack(mf4_collection) as mf4_stacked:
                        df_mf4_stacked = mf4_stacked.to_dataframe(
                            raster=raster,
                            time_from_zero=True,
                            reduce_memory_usage=True,
                            ignore_value2text_conversions=True,
                        )
                    # Replace all "nan" values with 0
                    df_mf4_stacked = df_mf4_stacked.fillna(0)

                # Append a column with the file name to the dataframe
                df_mf4_stacked["file"] = key

                # Update superset of columns
                column_superset = column_superset.union(set(df_mf4_stacked.columns))

                # Collect all signal names
                accumulated_signal_names.update(df_mf4_stacked.columns)

                # List of all dataframes
                dataframes.append(df_mf4_stacked)
                # alternativ for append: pd.concat(axis=1)
                datafiles.append(key)
                logger.info(f"Total number of columns: {len(df_mf4_stacked.columns)}")
            else:
                continue

        if not (self.modellib or file_analysis):
            if len(datafiles) < 2:
                logger.error("More training data is required for model generation.")
                return None

        if feature_engineering is not None:
            # transform bytecode to category type
            for df in dataframes:
                # df[non_numeric_cols] = (df[non_numeric_cols].stack().str.decode("utf-8").unstack())
                non_numeric_cols = [
                    col
                    for col in df
                    if not pd.api.types.is_numeric_dtype(df[col]) and not col == "file"
                ]
                df[non_numeric_cols] = (
                    df[non_numeric_cols]
                    .apply(lambda x: x.str.decode("utf-8"))
                    .astype("category")
                    .apply(lambda x: x.cat.add_categories(["sna", "nan"]))
                )
            df_result = pd.concat(dataframes, join="outer")
            # remove columns containing only a single value
            drop_col = [
                col
                for col in df_result.columns
                if len(df_result[col].unique()) <= 1
                and col != "file"
                and not col.startswith("I_")
            ]
            if len(drop_col) > 0:
                df_result = df_result.drop(drop_col, axis=1)
            # Alphabetic sorting of column names
            # df_result = df_result.reindex(sorted(df_result.columns), axis=1)
            return df_result
        else:
            df_result = pd.concat(
                dataframes, join="outer" if use_outer_join else "inner"
            )

            logger.info(
                f"Total number of files for {target} and timestamp {key}: {len(dataframes)}"
            )
            logger.info(f"Total number of identical columns: {len(df_result.columns)}")

            if not use_outer_join:
                logger.info(
                    f"Unused columns: {column_superset.difference(set(df_result.columns))}"
                )

            # Fill NaN values with zeros
            df_result.fillna(value=0, inplace=True)

            # Remove ethernet specific objects from dataframe:
            if is_ethernet:
                file_column = df_result["file"]
                df_result = df_result.select_dtypes(exclude=["object"])
                df_result["file"] = file_column

            # Alphabetic sorting of column names
            df_result = df_result.reindex(sorted(df_result.columns), axis=1)
            print(df_result)

            # Now split df_result into df_target and df_features
            if not dict_signallist:
                # Create dict_signallist if it's empty
                dict_signallist = self.__create_signallist(
                    target,
                    fi_signalnumber,
                    fi_signalthreshold,
                    accumulated_signal_names,
                )

            if dict_signallist and target in dict_signallist:
                target_signals = dict_signallist[target]
                # Check that the target signals are present in df_result
                existing_target_signals = [
                    col for col in target_signals if col in df_result.columns
                ]
                if existing_target_signals:
                    df_target = df_result[existing_target_signals]
                    print(df_target.shape)
                    df_features = df_result.drop(
                        columns=existing_target_signals + ["file"]
                    )
                    print(df_features.shape)
                else:
                    logger.error(f"No target found in data for {target}")
                    return None, None
            else:
                logger.error(f"No target specified for fuse {target}")
                return None, None

            # Return df_target and df_features
            return df_target, df_features

    ##########################################
    # Import all mf4 files with bus signals
    ##########################################
    def __read_bus_files(
        self,
        file,
        mf4_collection,
        list_blacklist=None,
    ) -> None:
        with MDF(file, raise_on_multiple_occurrences=False) as mf4_bus:
            allSignals = mf4_bus.search("*", case_insensitive=True, mode="wildcard")
            if list_blacklist is not None:
                if len(list_blacklist) > 0:
                    allSignals = [
                        signal for signal in allSignals if signal not in list_blacklist
                    ]
            mf4_collection.append(mf4_bus.filter(allSignals))
