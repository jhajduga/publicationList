# Publication Database Toolkit 🚀

Welcome to the **Publication Database Toolkit** – a sleek suite of two applications designed for managing, filtering, and converting publication data with style and ease! 😎

> **Publication Database Viewer**: A modern, interactive GUI for exploring your publication database.  
> **Converter App**: A modest CLI tool for transforming raw data files (CSV/Excel) into a beautifully formatted and filterable dataset.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
  - [Publication Database Viewer](#publication-database-viewer)
  - [Converter App](#converter-app)
- [Installation](#installation)
  - [Using pip](#using-pip)
  - [Using Conda](#using-conda)
- [Usage](#usage)
  - [Publication Database Viewer](#publication-database-viewer-usage)
  - [Converter App](#converter-app-usage)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [License](#license)
- [Contact](#contact)

---

## Overview

The **Publication Database Toolkit** offers two complementary applications:

- **Publication Database Viewer**  
  A sleek, modern GUI built with Tkinter and ttk that allows you to filter, search, and customize your view of publication data. Enjoy dynamic column selection with checkboxes neatly arranged in two rows, responsive filtering, and a polished modern interface using the "Segoe UI" font and the "clam" theme.

- **Converter App**  
  A robust CLI tool designed to convert raw publication data files (CSV or Excel) into clean, processed formats. It guides you through selecting relevant columns, filters rows based on your criteria (i.e., checking for the letter 'x'), and generates both a pickle file and an Excel workbook with elegantly styled tables.

---

## Features

### Publication Database Viewer
- **Interactive GUI**: Explore your publication data with a dynamic table that updates in real time.
- **Advanced Filtering**: Set minimum/maximum points and filter by categories.
- **Customizable Display**: Choose which columns to display via checkboxes (neatly arranged in two rows).
- **Modern Styling**: Enjoy a modern look with the "clam" theme and a chic "Segoe UI" font.
- **Detailed Logging**: Integrated logging with Loguru for in-depth diagnostics and troubleshooting.

### Converter App
- **Flexible Data Import**: Load CSV or Excel files or download data from a default URL if no file is provided.
- **Smart Data Processing**: Convert all columns to strings, rename columns for clarity, and filter rows based on user-selected criteria.
- **Output Versatility**: Export the processed data as a pickle file for quick future loading and an Excel file with dynamically generated, styled sheets.
- **Interactive Command Line**: Follow intuitive prompts to select filtering columns and generate your dataset.
- **Robust Logging**: Comprehensive logging throughout the conversion process ensures a smooth and traceable workflow.

---

## Installation

### Using pip

Ensure you have **Python 3.7+** installed, then install the required packages with:

```bash
pip install pandas loguru requests openpyxl xlsxwriter
```

### Using Conda

If you prefer using Conda, you can create a new environment and install the necessary packages:

1. **Create a new Conda environment:**

   ```bash
   conda create -n publication-db python=3.8 -y
   ```

2. **Activate the environment:**

   ```bash
   conda activate publication-db
   ```

3. **Install required packages:**

   ```bash
   conda install pandas -y
   conda install -c conda-forge loguru requests openpyxl xlsxwriter -y
   ```

Alternatively, you can create an `environment.yml` file with the following content:

```yaml
name: publication-db
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.8
  - pandas
  - loguru
  - requests
  - openpyxl
  - xlsxwriter
```

Then run:

```bash
conda env create -f environment.yml
conda activate publication-db
```

---

## Usage

### Converter App Usage

1. **Run the Converter App A.K.A. database_maker.py**:  
   Provide a file path as a command-line argument or leave blank to download the default file.

    ```bash
    python database_maker.py [path/to/your/file.xlsx]
    ```

2. **Follow the Prompts**:  
   - The app will list available categorical columns (those not part of the metadata).
   - Enter the numbers of the columns (comma-separated) you want to use for filtering rows marked with 'x'.
3. **Output**:  
   The application will generate:
   - A pickle file (`dane_filtered.pkl`) with the filtered dataset.
   - An Excel file (`baza_czasopism.xlsx`) featuring a full dataset sheet and additional sheets for each selected category (with styled tables and adjusted column widths).

### Publication Database Viewer Usage

1. **Prepare your data**: Ensure that a processed data file (`dane_filtered.pkl`) exists (generated via the Converter App).
2. **Run the Viewer**:

    ```bash
    python database_viewer.py
    ```

3. **Interact with the GUI**:  
   - Use the filter controls at the top to set minimum/maximum points and select a category.
   - Customize the table view by checking/unchecking the desired columns.
   - Enjoy a responsive, modern interface that updates the table dynamically.

---

## Configuration

Both applications allow you to adjust settings via source code:

- **Metadata Columns**: The list of columns always retained in your dataset.
- **Default URL**: (Converter App) URL used to download the original data file if no local file is provided.
- **Logging Settings**: Configured via Loguru for detailed diagnostics.

Modify these variables in the code as needed to tailor the applications to your workflow.

---

## Dependencies

- **Tkinter** (GUI for Publication Database Viewer)
- **pandas** (Data manipulation)
- **loguru** (Advanced logging)
- **requests** (File downloading for Converter App)
- **openpyxl** (Excel file reading)
- **xlsxwriter** (Excel file writing and styling)

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

For questions, suggestions, or contributions, please contact:  
**Jakub Hajduga** – [jhajduga@agh.edu.pl](mailto:jhajduga@agh.edu.pl) 📧

Feel free to open issues or submit pull requests. Enjoy the Publication Database Toolkit and happy data processing! ✨👍
