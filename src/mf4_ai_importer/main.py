# SPDX-License-Identifier: MIT

import argparse
from .data import Data


def main():
    # Define command-line arguments
    parser = argparse.ArgumentParser(
        description="Process mf4 data files with a target and blacklist."
    )
    parser.add_argument(
        "--filedir",
        "-f",
        required=True,
        help="Path to the directory containing all mf4 files",
    )
    parser.add_argument(
        "--targetdir",
        "-td",
        help="Path to dir with all target files",
    )
    parser.add_argument(
        "--targetname",
        "-tn",
        required=True,
        help="Name of the target file(target.txt) or choose from features.mf4",
    )
    parser.add_argument(
        "--bl", "-b", required=True, help="Path to file with signals to be blacklisted"
    )
    parser.add_argument(
        "--raster",
        "-r",
        type=int,
        required=True,
        help="Sampling value for data processing",
    )

    # Parse command-line arguments
    args = parser.parse_args()

    # Initialize the Data class
    data = Data(
        filedir=args.filedir,
        target=args.targetname,
        modellib=None,  # Here we don't use it
        targetdir=args.targetdir,
        blacklist=args.bl,
    )

    # Load mf4 files
    data.get_mf4files()

    # Process data using the parsed arguments
    df_target, df_features = data.import_data(
        target=args.targetname,
        raster=args.raster,
        use_outer_join=True,
        feature_engineering=None,
    )

    # Print the results
    print("Target Data:")
    print(df_target)
    print("\nFeature Data:")
    print(df_features)


if __name__ == "__main__":
    print("Running the updated main.py script")
    main()
