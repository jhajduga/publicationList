import os
import sys
import tempfile
import requests
import pandas as pd
from loguru import logger

# Configure logging
logger.add("converter_app.log", rotation="1 MB", level="DEBUG")

# Metadata columns – these will always be retained
METADATA_COLUMNS = [
    "Lp.",
    "Unikatowy Identyfikator Czasopisma",
    "Tytuł 1",
    "issn",
    "e-issn",
    "Tytuł 2",
    "issn 2",
    "e-issn 2",
    "Punkty"
]

# Default URL for the original XLSX file if no file is provided
DEFAULT_URL = "https://www.gov.pl/attachment/c2510527-171a-451e-b3c4-74ea5a5c6c94"

def download_file(url: str, output_path: str) -> None:
    """Downloads a file from the given URL and saves it to output_path."""
    logger.info("Downloading file from URL: {}", url)
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(response.content)
        logger.info("File downloaded and saved to: {}", output_path)
    except Exception as e:
        logger.exception("Error downloading file from URL: {}", url)
        raise e

def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads data from a CSV or Excel file.
    For Excel, skips the second row (skiprows=[1]) and renames columns.
    Converts all columns to string.
    """
    logger.debug("Loading data from file: {}", file_path)
    try:
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path, dtype=str)
            logger.debug("CSV file loaded.")
        elif file_path.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path, skiprows=[1], engine="openpyxl")
            # Rename columns – adjust the dictionary as needed
            rename_dict = {
                'Unnamed: 0':  "Lp.",
                'Unnamed: 1':  "Unikatowy Identyfikator Czasopisma",
                'Unnamed: 2':  "Tytuł 1",
                'Unnamed: 3':  "issn",
                'Unnamed: 4':  "e-issn",
                'Unnamed: 5':  "Tytuł 2",
                'Unnamed: 6':  "issn 2",
                'Unnamed: 7':  "e-issn 2",
                'Unnamed: 8':  "Punkty"
            }
            df.rename(columns=rename_dict, inplace=True)
            logger.debug("Columns renamed for Excel file.")
        else:
            logger.error("Unsupported file format: {}", file_path)
            raise ValueError("Unsupported file format. Use CSV or Excel.")
        df = df.astype(str)
        logger.info("Data loaded – {} rows, {} columns.", len(df), len(df.columns))
        return df
    except Exception as e:
        logger.exception("Error loading file: {}", file_path)
        raise e

def run_conversion(original_file: str) -> None:
    """
    Runs the interactive conversion process:
    - Loads the original file (CSV or Excel),
    - Displays available categorical columns (those not in metadata) and prompts the user to select columns (by number) to check for 'x',
    - Filters rows (keeps only rows where at least one selected column equals 'x'),
    - Retains only metadata columns plus the chosen categorical columns,
    - Saves the final dataset to a pickle file and generates an Excel file.
    """
    try:
        df = load_data(original_file)
    except Exception as e:
        print("Error loading original file. Check logs.")
        return

    # Display available categorical columns
    cat_columns = [col for col in df.columns if col not in METADATA_COLUMNS]
    print("\nAvailable categorical columns:")
    for i, col in enumerate(cat_columns, start=1):
        print(f"{i}. {col}")
    logger.debug("Available categorical columns: {}", cat_columns)

    cols_input = input("\nEnter the NUMBERS of the columns (separated by commas) to check for 'x': ").strip()
    try:
        chosen_indexes = [int(x.strip()) for x in cols_input.split(',') if x.strip()]
    except ValueError:
        logger.error("Invalid format for column numbers.")
        print("Error: Invalid column numbers provided.")
        return

    max_index = len(cat_columns)
    invalid = [idx for idx in chosen_indexes if idx < 1 or idx > max_index]
    if invalid:
        logger.error("Invalid column numbers: {}", invalid)
        print(f"Error: Invalid column numbers: {invalid}")
        return
    chosen_cat_columns = [cat_columns[idx - 1] for idx in chosen_indexes]
    logger.debug("Selected columns for filtering: {}", chosen_cat_columns)

    # Filtering – keep only rows where at least one selected column has 'x'
    mask = df[chosen_cat_columns].apply(lambda col: col.str.strip().str.lower() == 'x')
    df_filtered = df[mask.any(axis=1)]
    logger.info("After filtering, {} rows remain.", len(df_filtered))

    # Retain only metadata and the chosen categorical columns
    columns_to_keep = METADATA_COLUMNS + chosen_cat_columns
    df_final = df_filtered[columns_to_keep]
    logger.info("Final dataset has {} rows and {} columns.", len(df_final), len(df_final.columns))

    # Save the pickle file
    pickle_file = "dane_filtered.pkl"
    try:
        df_final.to_pickle(pickle_file)
        logger.info("Pickle file saved: {}", pickle_file)
        print(f"Pickle file saved: {pickle_file}")
    except Exception as e:
        logger.exception("Error saving pickle file.")
        print("Error saving pickle file. Check logs.")
        return

    # Save the Excel file
    from pandas import ExcelWriter
    output_file = "baza_czasopism.xlsx"
    try:
        with ExcelWriter(output_file, engine="xlsxwriter") as writer:
            workbook = writer.book
            # Sheet "All" with the entire dataset
            df_final.to_excel(writer, sheet_name="All", index=False)
            worksheet_all = writer.sheets["All"]
            (max_row, max_col) = df_final.shape
            worksheet_all.add_table(0, 0, max_row, max_col - 1, {
                'columns': [{'header': col} for col in df_final.columns],
                'style': 'Table Style Medium 2'
            })
            # Adjust column widths for "All"
            for col_num, header in enumerate(df_final.columns):
                col_width = max(12, len(header) + 2)
                worksheet_all.set_column(col_num, col_num, col_width)
            logger.info("Sheet 'All' saved.")

            # For each chosen category, create a sheet with metadata + that category
            for cat in chosen_cat_columns:
                df_cat = df_final[df_final[cat].str.strip().str.lower() == 'x']
                if df_cat.empty:
                    logger.debug("No rows for category '{}'; sheet will not be created.", cat)
                    continue
                columns_to_include = METADATA_COLUMNS + [cat]
                df_cat_filtered = df_cat[columns_to_include]
                sheet_name = cat[:31]  # Excel sheet names are limited to 31 characters
                df_cat_filtered.to_excel(writer, sheet_name=sheet_name, index=False)
                worksheet_cat = writer.sheets[sheet_name]
                (max_row_cat, max_col_cat) = df_cat_filtered.shape
                worksheet_cat.add_table(0, 0, max_row_cat, max_col_cat - 1, {
                    'columns': [{'header': col} for col in df_cat_filtered.columns],
                    'style': 'Table Style Medium 2'
                })
                # Adjust column widths for this sheet
                for col_num, header in enumerate(df_cat_filtered.columns):
                    col_width = max(12, len(header) + 2)
                    worksheet_cat.set_column(col_num, col_num, col_width)
                logger.info("Sheet '{}' saved with {} records.", sheet_name, len(df_cat_filtered))
        logger.info("Excel file '{}' generated successfully.", output_file)
        print(f"Excel file saved successfully: {output_file}")
    except Exception as e:
        logger.exception("Error saving Excel file.")
        print("Error saving Excel file. Check logs.")
        return

def main():
    # Check if a file path was provided as a command-line argument
    if len(sys.argv) > 1:
        original_input = sys.argv[1]
    else:
        original_input = input("Enter the path to the original file (CSV or Excel) or leave blank to download from the net: ").strip()
    if not original_input:
        original_input = DEFAULT_URL
        # Download the file to a temporary location
        temp_dir = tempfile.gettempdir()
        downloaded_file = os.path.join(temp_dir, "original.xlsx")
        try:
            download_file(original_input, downloaded_file)
            original_input = downloaded_file
        except Exception as e:
            print("Error downloading the file. Check logs.")
            return
    run_conversion(original_input)

if __name__ == "__main__":
    main()
