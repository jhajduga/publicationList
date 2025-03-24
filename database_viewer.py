import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from loguru import logger
import math

# Configure logging
logger.add("db_viewer.log", rotation="1 MB", level="DEBUG")

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

def load_database() -> pd.DataFrame:
    try:
        df = pd.read_pickle("dane_filtered.pkl")
        # Convert "Punkty" column to numeric
        df["Punkty"] = pd.to_numeric(df["Punkty"], errors="coerce")
        logger.info("Database loaded – {} rows, {} columns.", len(df), len(df.columns))
        return df
    except Exception as e:
        logger.exception("Error loading database.")
        messagebox.showerror("Error", f"Error loading database: {e}")
        return None

class DatabaseViewer(tk.Tk):
    def __init__(self, df: pd.DataFrame):
        super().__init__()
        self.title("Publication Database Viewer")
        self.geometry("1000x600")
        
        # Create and configure style
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        # Updated fonts to a more modern "sexy" look: Segoe UI
        self.style.configure("Treeview", font=("Segoe UI", 9), rowheight=25)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        self.style.configure("TCheckbutton", font=("Segoe UI", 9))
        
        # Create menu bar for additional polish
        self.create_menu()
        
        self.df = df
        self.current_df = self.df  # Store the currently displayed DataFrame
        # Categorical columns are those not in metadata
        self.cat_columns = [col for col in self.df.columns if col not in METADATA_COLUMNS]
        logger.debug("Categorical columns: {}", self.cat_columns)
        
        self.create_widgets()
        self.populate_table(self.df)

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
    
    def show_about(self):
        messagebox.showinfo("About", "Publication Database Viewer\nVersion 1.0\nBy Your Name")
    
    def create_widgets(self):
        # Filter frame using ttk for consistent styling
        filter_frame = ttk.Frame(self)
        filter_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        ttk.Label(filter_frame, text="Min Points:", font=("Segoe UI", 9)).grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.min_points_entry = ttk.Entry(filter_frame, width=10, font=("Segoe UI", 9))
        self.min_points_entry.grid(row=0, column=1, padx=5, pady=5)
        self.min_points_entry.insert(0, "0")

        ttk.Label(filter_frame, text="Max Points:", font=("Segoe UI", 9)).grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        self.max_points_entry = ttk.Entry(filter_frame, width=10, font=("Segoe UI", 9))
        self.max_points_entry.grid(row=0, column=3, padx=5, pady=5)
        self.max_points_entry.insert(0, "200")

        ttk.Label(filter_frame, text="Category:", font=("Segoe UI", 9)).grid(row=0, column=4, padx=5, pady=5, sticky=tk.E)
        self.category_var = tk.StringVar()
        options = ["All"] + self.cat_columns
        self.category_menu = ttk.Combobox(filter_frame, textvariable=self.category_var, values=options, state="readonly", font=("Segoe UI", 9))
        self.category_menu.grid(row=0, column=5, padx=5, pady=5)
        self.category_menu.current(0)

        filter_button = ttk.Button(filter_frame, text="Apply Filters", command=self.apply_filters)
        filter_button.grid(row=0, column=6, padx=5, pady=5)

        # Column selection frame – arranged in two rows using grid
        column_selection_frame = ttk.Frame(self)
        column_selection_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        ttk.Label(column_selection_frame, text="Select columns to display:", font=("Segoe UI", 9))\
            .grid(row=0, column=0, columnspan=100, sticky="w")
        
        self.column_vars = {}
        total_columns = len(self.df.columns)
        cols_per_row = math.ceil(total_columns / 2)
        # Default columns: "Tytuł 1", "Punkty", "issn" and all category columns
        default_cols = set(["Tytuł 1", "Punkty", "issn"])
        default_cols.update(self.cat_columns)
        
        # First row of checkboxes
        for i, col in enumerate(self.df.columns[:cols_per_row]):
            default_value = col in default_cols
            var = tk.BooleanVar(value=default_value)
            self.column_vars[col] = var
            cb = ttk.Checkbutton(
                column_selection_frame,
                text=col,
                variable=var,
                command=self.update_visible_columns
            )
            cb.grid(row=1, column=i, padx=2, sticky="w")
        
        # Second row of checkboxes (if any)
        for j, col in enumerate(self.df.columns[cols_per_row:]):
            default_value = col in default_cols
            var = tk.BooleanVar(value=default_value)
            self.column_vars[col] = var
            cb = ttk.Checkbutton(
                column_selection_frame,
                text=col,
                variable=var,
                command=self.update_visible_columns
            )
            cb.grid(row=2, column=j, padx=2, sticky="w")
        
        # Separator for a clean division between controls and table
        separator = ttk.Separator(self, orient="horizontal")
        separator.pack(fill="x", padx=10, pady=5)

        # Table frame using ttk.Frame
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(table_frame, show="headings")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.configure(xscrollcommand=hsb.set)

    def populate_table(self, df: pd.DataFrame):
        # Use only the columns that are selected
        visible_cols = [col for col in self.df.columns if self.column_vars[col].get()]
        
        if not visible_cols:
            messagebox.showinfo("Info", "No columns are selected.")
            return

        # Clear current table content
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        self.tree["columns"] = visible_cols
        for col in visible_cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)
        
        for _, row in df.iterrows():
            values = [str(row[col]) for col in visible_cols]
            self.tree.insert("", tk.END, values=values)
        logger.info("Table populated with {} rows.", len(df))

    def update_visible_columns(self):
        # Refresh table view using currently filtered data
        self.populate_table(self.current_df)

    def apply_filters(self):
        try:
            min_points = float(self.min_points_entry.get())
            max_points = float(self.max_points_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Min and Max points must be numbers.")
            return

        logger.debug("Filtering: Points from {} to {}.", min_points, max_points)
        filtered_df = self.df[(self.df["Punkty"] >= min_points) & (self.df["Punkty"] <= max_points)]
        selected_category = self.category_var.get()
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df[selected_category].str.lower() == 'x']
            logger.debug("Filtering: Selected category {}.", selected_category)
        filtered_df = filtered_df.sort_values(by="Punkty", ascending=False)
        logger.info("After filtering, {} records remain.", len(filtered_df))
        
        self.current_df = filtered_df
        self.populate_table(filtered_df)

def main():
    df = load_database()
    if df is None:
        return
    app = DatabaseViewer(df)
    app.mainloop()

if __name__ == "__main__":
    main()
