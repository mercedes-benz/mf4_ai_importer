<!-- SPDX-FileCopyrightText: Copyright (c) 2024 MBition GmbH. -->
<!-- SPDX-License-Identifier: MIT -->

<!-- TABLE OF CONTENTS -->
<h2>Table of Contents</h2>
<ol>
  <li><a href="#about-the-project">About The Project</a></li>
  <li><a href="#structure-of-the-repository">Structure of the Repository</a></li>
  <li><a href="#package-installation">Package Installation</a></li>
  <li><a href="#usage">Usage</a></li>
  <li><a href="#contributing">Contributing</a></li>
  <li><a href="#license">License</a></li>
  <li><a href="#contact">Contact</a></li>
</ol>

## Provider Information

<!-- Disclaimler -->
Source code has been tested solely for our own use cases, which might differ from yours.
This project is actively maintained and contributing is endorsed.

<!-- ABOUT THE PROJECT -->
## About The Project
The `mf4_ai_importer` Python package has been developed with the specific purpose of importing  `.MF4` files and transforming them into feature and target dataframes, with the aim of supporting AI applications within the automotive industry. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Structure of the repository
```plaintext
├── MF4_AI_IMPORTER/
├── src/
│   └── mf4_ai_importer/
│       ├── data.py
│       ├── main.py
```
   <p align="right">(<a href="#readme-top">back to top</a>)</p>

## Package installation
1. **Clone the source code:**
   ```bash
   git clone <repository_url>
   ```

2. **Install Python dependencies in your Python environment:**
   ```bash
   python3 -m pip install -e .
   ```

3. **Build a package and install it on the system:**
   ```bash
   python3 -m pip install --upgrade build
   python3 -m build
   pip install dist/*.tar.gz
   ```

4. **Verify if the installation was successful:**
   ```bash
   pip list | grep mf4-ai-importer
   ```

   <p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

This program processes MF4 data files, applying specific features, targets, and blacklists based on provided command-line arguments. Below are the details of the command-line options you can use to run this program:

### Command-line Arguments

- `--filedir`, `-f` **(Required)**
  - Description: Path to the directory containing feature files (`feature.mf4`) and target files (`target.mf4`).
  - Usage: `--filedir <path_to_all_files_directory>`

- `--targetdir`, `-td` **(Optional)**
  - Description: Path to the directory containing all target files `target.mf4`, including a `targetname.txt` file that lists all the target names. See an example in `target_files`.
  - Usage: `--targetdir <path_to_target_directory>`

- `--targetname`, `-tn` **(Required)**
  - Description: Name of the target (If targetdir exists, the targetname will be taken from the `targetname.txt`,in this case, it is A15; otherwise, it can be extracted from features.mf4 using the specified target name.).
  - Usage: `--targetname <target_name>`

- `--bl`, `-b` **(Required)**
  - Description: Path to the file containing signals to be blacklisted.
  - Usage: `--bl <path_to_blacklist_file>`

- `--raster`, `-r` **(Required)**
  - Description: Sampling value for data processing, specified as an integer.
  - Usage: `--raster <sampling_value>`


### Function Description

The `main()` function processes MF4 data files to extract and prepare target and feature datasets, suitable for further analysis or machine learning applications. Here are the details of the outputs:

- **`df_target`**: This DataFrame contains the target data extracted based on the specified `target` parameter. It is crucial for supervised learning tasks where the target variable is predicted.

- **`df_features`**: This DataFrame holds the features extracted from the MF4 files that are relevant for modeling purposes. 

### Example

Here's an example of how you might use these arguments:

- **Example 1:**

   ```bash
   main --filedir ./sample_files --targetdir ./target_files --targetname A15 --bl ./sample_files/blacklist.csv --raster 5 
   
   ```

- **Example 2:**

   ```bash
   main --filedir ./sample_files  --targetname target1 --bl ./sample_files/blacklist.csv --raster 5 
   ```
   <p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing
The instructions on how to contribute can be found in the file [CONTRIBUTING.md](./CONTRIBUTING.md) in this repository.
   <p align="right">(<a href="#readme-top">back to top</a>)</p>

## License
The code is published under the MIT license. Further information on that can be found in the [LICENSE.md](./LICENSE.md) file in this repository.
   <p align="right">(<a href="#readme-top">back to top</a>)</p>
