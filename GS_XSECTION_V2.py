import tkinter as tk
from tkinter import ttk
import sys, os
import xml.dom.minidom as xr
import pandas as pd
import numpy as np
import geopandas as gpd
import rasterio as rio
from rasterio.plot import show
import shapely
from pyproj import _datadir, datadir
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib import pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnchoredOffsetbox
import matplotlib.patches as mpatches
from PIL import Image
from itertools import groupby
from statistics import mean


NavigationToolbar2Tk.toolitems = [t for t in NavigationToolbar2Tk.toolitems if
             t[0] not in ('Subplots',)]

plt.rcParams['savefig.dpi'] = 300
plt.rcParams['axes.axisbelow'] = True

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        menu_file = tk.Menu(self, tearoff=0)
        


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # configure the root window
        self.title('GS Topographic X-Section Tool v2.4')
        self.geometry()
        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())

        self.rowconfigure(1, weight = 1)
        self.columnconfigure(0, weight = 1)
        menubar = MenuBar(self)
        tk.Tk.config(self, menu=menubar)
        # menubar.add_cascade(label="Batch Tools", menu=menubar)
        menubar.add_command(label="Save Configuration", command=self.save_config)
        menubar.add_command(label="Load Configuration", command=self.load_config)
        menubar.add_command(label="Export Vectors", command=self.export_vectors)

# Frame 1: Data Upload
        self.frame1 = tk.LabelFrame(self, text="Data Upload", width=450, height=450)
        self.frame1.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        self.frame1.grid_propagate(False)

        # Button: Select DEM
        self.upload_dem_button = ttk.Button(self.frame1, text='Select DEM', command=self.load_dem_path)
        self.upload_dem_button.grid(row = 0, column = 0, padx=10, pady=10,sticky="ew")

        # Entry: DEM path
        self.dem_path = ttk.Entry(self.frame1, width=45)
        self.dem_path.insert(0, "DEM Path")
        self.dem_path.grid(row = 0, column = 1, sticky="ew")

        # Scrollbar: DEM path
        self.scroll_dem_path = ttk.Scrollbar(self.frame1, orient='horizontal', command=self.dem_path.xview, )
        self.dem_path.config(xscrollcommand=self.scroll_dem_path.set)
        self.scroll_dem_path.grid(row = 1, column = 1, sticky='ew')

        # Button: Select X Section Lines
        self.upload_lines_button = ttk.Button(self.frame1, text='Select X-section Lines', command=self.load_line_path)
        self.upload_lines_button.grid(row = 2, column = 0, padx=10, pady=10,sticky="ew")

        # Entry: X Section Lines path
        self.lines_path = ttk.Entry(self.frame1, width=45)
        self.lines_path.insert(0, "X-section Lines Path")
        self.lines_path.grid(row = 2, column = 1, sticky="ew")

        # Scrollbar: X Section Lines path
        self.scroll_lines_path = ttk.Scrollbar(self.frame1, orient='horizontal', command=self.lines_path.xview, )
        self.lines_path.config(xscrollcommand=self.scroll_lines_path.set)
        self.scroll_lines_path.grid(row = 3, column = 1, sticky='ew')

        # Label: X Section Lines width
        self.line_width_label = ttk.Label(self.frame1, text="Line width (Map Units)")
        self.line_width_label.grid(row = 4, column = 0, padx=10, pady=10, sticky="ew")

        # Entry: X Section Lines width
        self.line_width_entry = ttk.Entry(self.frame1, width=10)
        self.line_width_entry.grid(row = 4, column = 1, sticky="w")

        # Button: Select Vertical MPs
        self.upload_vmps_button = ttk.Button(self.frame1, text='Select Vertical MPs', command=self.load_vmps_path)
        self.upload_vmps_button.grid(row = 5, column = 0, padx=10, pady=10,sticky="ew")

        # Entry: Vertical MPs path
        self.vmps_path = ttk.Entry(self.frame1, width=45)
        self.vmps_path.insert(0, "Vertical MPs Path")
        self.vmps_path.grid(row = 5, column = 1, sticky="ew")

        # Scrollbar: Vertical MPs path
        self.scroll_vmps_path = ttk.Scrollbar(self.frame1, orient='horizontal', command=self.vmps_path.xview, )
        self.vmps_path.config(xscrollcommand=self.scroll_vmps_path.set)
        self.scroll_vmps_path.grid(row = 6, column = 1, sticky='ew')

        # Button: Select Horizontal MPs
        self.upload_hmps_button = ttk.Button(self.frame1, text='Select East-West MPs', command=self.load_hmps_path)
        self.upload_hmps_button.grid(row = 7, column = 0, padx=10, pady=10,sticky="ew")

        # Entry: Horizontal MPs path
        self.hmps_path = ttk.Entry(self.frame1, width=45)
        self.hmps_path.insert(0, "Horizontal MPs Path")
        self.hmps_path.grid(row = 7, column = 1, sticky="ew")

        # Scrollbar: Horizontal MPs path
        self.scroll_hmps_path = ttk.Scrollbar(self.frame1, orient='horizontal', command=self.hmps_path.xview, )
        self.hmps_path.config(xscrollcommand=self.scroll_hmps_path.set)
        self.scroll_hmps_path.grid(row = 8, column = 1, sticky='ew')        

        # Button: Load Data 
        self.load_data_button = ttk.Button(self.frame1, text='Load Data', command=self.upload_data)
        self.load_data_button.grid(row = 9, column = 0, padx=10, pady=10,sticky="ew")

        # Button: Load Data 
        self.map_button = ttk.Button(self.frame1, text='Map Preview', command=self.plot_map)
        self.map_button.grid(row = 9, column = 1, padx=10, pady=10,sticky="ew")

        # # Progress bar: Upload
        # self.data_upload_pb = ttk.Progressbar(self.frame1, orient="horizontal", mode="indeterminate")
        # self.data_upload_pb.grid(row = 10, column = 0, columnspan=2, padx=10, pady=10,sticky="ew")

        # Label: Upload progress bar
        self.label_pb = ttk.Label(self.frame1)
        self.label_pb.grid(row = 10, column = 0, columnspan=2, padx=10)

        
    # Frame 2: Configure project
        self.frame2 = tk.LabelFrame(self, text="Configure Cross Section", width=450, height=450)
        self.frame2.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")
        # self.frame2.grid_propagate(False)

        # Label: Select x-section
        self.label_xsect = ttk.Label(self.frame2, text="X-section to plot")
        self.label_xsect.grid(row = 0, column = 0, padx=10, pady=10, sticky="w")

        # Combobox: Select x-section to plot
        self.xsect_combo_text = tk.StringVar()
        self.xsect_combo = ttk.Combobox(self.frame2, textvariable=self.xsect_combo_text, state="readonly")
        self.xsect_combo.grid(row = 0, column = 1, columnspan=2,padx=10, pady=10, sticky="ew")

        self.xsect_combo.bind("<<ComboboxSelected>>", self.config_to_entries) 

        # Label: Vector Scale
        self.label_vec_scale = ttk.Label(self.frame2, text='Vector Scale')
        self.label_vec_scale.grid(row = 1, column = 0, padx=10, pady=10, sticky="w")

        # Entry: Vector Scale
        self.vec_scale_entry = ttk.Entry(self.frame2, width=10)
        self.vec_scale_entry.grid(row = 1, column = 1,sticky="w")

        # Label: Vertical exaggeration
        self.label_vert_scale = ttk.Label(self.frame2, text='Vertical Exaggeration')
        self.label_vert_scale.grid(row = 2, column = 0, padx=10, pady=10, sticky="w")

        # Entry: Vertical exaggeration
        self.vert_scale_entry = ttk.Entry(self.frame2, width=10)
        self.vert_scale_entry.grid(row = 2, column = 1,sticky="w")

        # Label: Arrow length
        self.label_arrow_length = ttk.Label(self.frame2, text='Arrow Length (mm)')
        self.label_arrow_length.grid(row = 3, column = 0, padx=10, pady=10, sticky="w")

        # Entry: Arrow length
        self.arrow_length_entry = ttk.Entry(self.frame2, width=10)
        self.arrow_length_entry.grid(row = 3, column = 1,sticky="w")

        # Checkbutton: Average vectors checkbutton
        self.avg_check_button_value = tk.IntVar()
        self.avg_check_button = ttk.Checkbutton(self.frame2, variable=self.avg_check_button_value, text="Average Vectors")
        self.avg_check_button.grid(row = 3, column = 2, sticky="w")

        # Label: X Limits
        self.label_x_lims = ttk.Label(self.frame2, text='X min, X max (m)')
        self.label_x_lims.grid(row = 4, column = 0, padx=10, pady=10, sticky="ew")

        # Entry: X Limits Min
        self.x_min = ttk.Entry(self.frame2, )
        self.x_min.grid(row = 4, column = 1,sticky="ew")     

        # Entry: X Limits Max
        self.x_max = ttk.Entry(self.frame2,)
        self.x_max.grid(row = 4, column = 2,padx=10, pady=10,sticky="w")

        # Label: Y Limits
        self.label_y_lims = ttk.Label(self.frame2, text='Y min, Y max (m)')
        self.label_y_lims.grid(row = 5, column = 0, padx=10, pady=10, sticky="ew")

        # Entry: Y Limits Min
        self.y_min = ttk.Entry(self.frame2, )
        self.y_min.grid(row = 5, column = 1,sticky="ew")     

        # Entry: Y Limits Max
        self.y_max = ttk.Entry(self.frame2,)
        self.y_max.grid(row = 5, column = 2,padx=10, pady=10,sticky="w")

        # Label: Select Start and End date
        self.label_date = ttk.Label(self.frame2, text="Cumulative displacement is calculated between two dates:")
        self.label_date.grid(row = 6, column = 0, columnspan=3, padx=10, pady=10, sticky="w")

        # Label: Select Start and End date
        self.label_date = ttk.Label(self.frame2, text="Start Date, End Date")
        self.label_date.grid(row = 7, column = 0, padx=10, pady=10, sticky="w")

        # Combobox: Select Start Date
        self.start_date_combo_text = tk.StringVar()
        self.start_date_combo = ttk.Combobox(self.frame2, textvariable=self.start_date_combo_text, state="readonly")
        self.start_date_combo.grid(row = 7, column = 1, sticky="ew")

        # Combobox: Select End Date
        self.end_date_combo_text = tk.StringVar()
        self.end_date_combo = ttk.Combobox(self.frame2, textvariable=self.end_date_combo_text, state="readonly")
        self.end_date_combo.grid(row = 7, column = 2, padx=10, pady=10, sticky="ew")

        # Label: Precision checkbutton
        self.precision_check_label = ttk.Label(self.frame2, text="Vector Colours")
        self.precision_check_label.grid(row = 8, column = 0, padx=10, pady=10, sticky="w")     

        # Checkbutton: Precision checkbutton
        self.precision_check_button_value = tk.IntVar()
        self.precision_check_button = ttk.Checkbutton(self.frame2, variable=self.precision_check_button_value, text="Grey <5mm")
        self.precision_check_button.grid(row = 8, column = 1, sticky="w")

        # Checkbutton: Max checkbutton
        self.max_check_button_value = tk.IntVar()
        self.max_check_button = ttk.Checkbutton(self.frame2, variable=self.max_check_button_value, text="Red Maximum")
        self.max_check_button.grid(row = 8, column = 2, padx=10, pady=10, sticky="w")

        # Label: X Label
        self.x_label_label = ttk.Label(self.frame2, text="X Axis Label")
        self.x_label_label.grid(row = 9, column = 0, padx=10, pady=10, sticky="w") 

        # Entry: X Label
        self.x_label_entry = ttk.Entry(self.frame2,)
        self.x_label_entry.grid(row = 9, column = 1,sticky="ew")

        # Checkbutton: xgrid checkbutton
        self.xgrid_check_button_value = tk.IntVar()
        self.xgrid_check_button = ttk.Checkbutton(self.frame2, variable=self.xgrid_check_button_value, text="X Gridlines")
        self.xgrid_check_button.grid(row = 9, column = 2,padx=10, pady=10, sticky="w")

        # Label: Y Label
        self.y_label_label = ttk.Label(self.frame2, text="Y Axis Label")
        self.y_label_label.grid(row = 10, column = 0, padx=10, pady=10, sticky="w") 

        # Entry: Y Label
        self.y_label_entry = ttk.Entry(self.frame2,)
        self.y_label_entry.grid(row = 10, column = 1,sticky="ew")

        # Checkbutton: Ygrid checkbutton
        self.ygrid_check_button_value = tk.IntVar()
        self.ygrid_check_button = ttk.Checkbutton(self.frame2, variable=self.ygrid_check_button_value, text="Y Gridlines")
        self.ygrid_check_button.grid(row = 10, column = 2,padx=10, pady=10, sticky="w")

        # Label: Title
        self.title_label = ttk.Label(self.frame2, text="Plot Title")
        self.title_label.grid(row = 11, column = 0, padx=10, pady=10, sticky="w") 

        # Entry: Title
        self.title_entry = ttk.Entry(self.frame2,)
        self.title_entry.grid(row = 11, column = 1, columnspan=2, padx=10, pady=10, sticky="ew")

        # Button: Plot x-section 
        self.plot_xsect_button = ttk.Button(self.frame2, text='Plot x-section', command=lambda: [self.create_xsection(), self.xsection(), self.update_metadata(), self.plot_popup()])
        self.plot_xsect_button.grid(row = 12, column = 0, columnspan=1, padx=10, pady=10,sticky="ew")

        # Button: Plot ALL x-sections
        self.plot_all_button = ttk.Button(self.frame2, text='Plot All', command=self.plot_all)
        self.plot_all_button.grid(row = 12, column = 1, padx=10, pady=10,sticky="ew")

        # Button: Save ALL x-sections
        self.save_all_button = ttk.Button(self.frame2, text='Save All', command=self.save_plots)
        self.save_all_button.grid(row = 12, column = 2, padx=10, pady=10,sticky="ew")

    # # Frame 3: Cross Section Preview
    #     self.frame3 = tk.LabelFrame(self, text="Cross Section Preview", width=450, height=550)
    #     self.frame3.grid(row=1, column=0, columnspan=3, padx=20, sticky="nsew")
    #     # self.frame3.grid(row=0, column=2, columnspan=3, padx=20, sticky="nsew")

    #     self.frame3.grid_propagate(False)

    #     self.canvas_frame3 = tk.Canvas(self.frame3, width=450, height=200, highlightthickness=0)
    #     self.scrollbar_frame3 = ttk.Scrollbar(self, orient="vertical", command=self.canvas_frame3.yview)
    #     self.sub_frame3 = ttk.Frame(self.canvas_frame3, width=450, height=350)

    #     self.sub_frame3.bind(
    #         "<Configure>",
    #         lambda e: self.canvas_frame3.configure(
    #             scrollregion=self.canvas_frame3.bbox("all")
    #         )
    #     )

    #     self.canvas_frame3.create_window((0, 0), window=self.sub_frame3, anchor="center")

    #     self.canvas_frame3.configure(yscrollcommand=self.scrollbar_frame3.set)

    #     self.canvas_frame3.pack(side="right", fill="both", expand=True)
    #     self.scrollbar_frame3.grid(column=4, row=1, sticky="ns")


    #     # # Frame: Preview
    #     self.frame_preview = tk.Frame(self.sub_frame3, width=400, height=200)
    #     self.frame_preview.grid(row=0, column=0, padx=10, pady=10)

        

# Functions
    # Load DEM file
    def load_dem_path(self):
        fp = tk.filedialog.askopenfilename(
            title='Select DEM GeoTIFF',
            filetypes=(('GeoTIFF Files', '*.tif'),))
        self.dem_path.delete(0, 'end')
        self.dem_path.insert(0, fp)
        return

    # Load X-section lines file
    def load_line_path(self):
        fp = tk.filedialog.askopenfilename(
            title='Select x-section line SHP',
            filetypes=(('Shapefiles', '*.shp'),))
        self.lines_path.delete(0, 'end')
        self.lines_path.insert(0, fp)
        return

    # Load vertical MPs file
    def load_vmps_path(self):
        fp = tk.filedialog.askopenfilename(
            title='Select vertical MPs SHP',
            filetypes=(('Shapefiles', '*.shp'),))
        self.vmps_path.delete(0, 'end')
        self.vmps_path.insert(0, fp)
        return

    # Load horizontal MPs file
    def load_hmps_path(self):
        fp = tk.filedialog.askopenfilename(
            title='Select east-west MPs SHP',
            filetypes=(('Shapefiles', '*.shp'),))
        self.hmps_path.delete(0, 'end')
        self.hmps_path.insert(0, fp)
        return

    # Upload Data
    def upload_data(self):
        # Load the data sequentially
        # Load DEM
        self.label_pb["text"] = "Loading DEM ..."
        self.frame1.update_idletasks()
        self.dem = rio.open(self.dem_path.get()) # DEM object containing the data, CRS, and other useful attributes
        
        # Load x-section lines
        self.label_pb["text"] = "Loading x-section lines..."
        self.frame1.update_idletasks()
        self.xlines = gpd.read_file(self.lines_path.get())
        distance = float(self.line_width_entry.get())
        self.buffer_lines = self.xlines.buffer(distance=distance, cap_style=3)
        self.xsect_combo["values"] = self.xlines["Name"].to_list()
        self.xsect_combo_text.set(self.xsect_combo["values"][0])
        self.title_entry.insert(0, self.xsect_combo["values"][0])
        self.metadata = dict.fromkeys(self.xlines["Name"].to_list()) # Dict that will be used to save the x-section metadata for the batch tool
        self.vecdata = dict.fromkeys(self.xlines["Name"].to_list())
        
        # self.metadata["title"] = self.xsect_combo["values"][0]
        self.figdata = dict.fromkeys(self.xlines["Name"].to_list())
                
        # Create figures
        for xline in self.xlines["Name"].to_list():
            fig, ax = plt.subplots(figsize=(8,6))
            figs = {"fig": fig,
                    "ax": ax,
                    "window": None,
                    "canvas": None}
            self.figdata[xline] = figs
            meta_title = dict(title=xline)
            self.metadata[xline] = meta_title

            vecdata = {"Total Displacement (mm)": None,
                    "Distance (map units)": None,
                    "Elevation (DEM units)": None,
                    "Vertical Displacement (mm)": None,
                    "Horizontal Displacement (mm)": None}
            self.vecdata[xline] = vecdata
            print(self.metadata[xline])

        # Load vertical MPs
        self.label_pb["text"] = "Loading vertical MPs ..."
        self.frame1.update_idletasks()
        self.vert = gpd.read_file(self.vmps_path.get()) # vertical MPs geopandas dataframe
        self.vert_transformed = self.vert.to_crs(self.xlines.crs)

        # Load horizontal MPs
        self.label_pb["text"] = "Loading horizontal MPs ..."
        self.frame1.update_idletasks()
        self.hori = gpd.read_file(self.hmps_path.get()) # horizontal MPs geopandas dataframe
        self.hori_transformed = self.hori.to_crs(self.xlines.crs)
        self.start_date_combo["values"] = [col for col in self.hori_transformed if col.startswith('D')] # populate start and end date dropdowns
        self.end_date_combo["values"] = self.start_date_combo["values"]
        
        self.label_pb["text"] = "Data loaded."
        
    def update_metadata(self):
        inputs_for_x_sect = {"vector_scale": self.vec_scale_entry.get(),
                             "vertical_exaggeration": self.vert_scale_entry.get(),
                             "arrow_length": self.arrow_length_entry.get(),
                             "x_min": self.x_min.get(),
                             "x_max": self.x_max.get(),
                             "y_min": self.y_min.get(),
                             "y_max": self.y_max.get(),
                             "start_date": self.start_date_combo_text.get(),
                             "end_date": self.end_date_combo_text.get(),
                             "prec_checkbox": self.precision_check_button_value.get(),
                             "max_checkbox": self.max_check_button_value.get(),
                             "title": self.title_entry.get(),
                             "x_label": self.x_label_entry.get(),
                             "y_label": self.y_label_entry.get(),
                             "x_grid": self.xgrid_check_button_value.get(),
                             "y_grid": self.xgrid_check_button_value.get(),
                             "avg_vectors": self.avg_check_button_value.get()}
        
        self.metadata[self.xsect_combo_text.get()] = inputs_for_x_sect

    def save_config(self):
        fp = tk.filedialog.asksaveasfilename(
            defaultextension=".csv",
            title='Save config CSV',
            filetypes=(('CSV Files', '*.csv'),))
        configuration = pd.DataFrame(self.metadata)
        # print(configuration)
        configuration.to_csv(fp)

    def load_config(self):
        fp = tk.filedialog.askopenfilename(
            title='Select config CSV',
            filetypes=(('CSV Files', '*.csv'),))
        
        configuration = pd.read_csv(fp, index_col=0)
        self.metadata = configuration.to_dict()
        # print(self.metadata)
        self.config_to_entries("event")

    def export_vectors(self):
        fp = tk.filedialog.askdirectory(title='Select a folder',)
        for xsect in self.vecdata:
            try:
                vector = pd.DataFrame(self.vecdata[xsect]).reset_index(drop=True)
                vector.to_csv(fp+"/"+xsect+"_VECTORS.csv")
                print("Exported "+ xsect+"_VECTORS.csv")
            except ValueError:
                pass
        # print(configuration)
        
    # def config_to_entries_new(self, event):
    #     self.vec_scale_entry.delete(0, 'end')
    #     self.vert_scale_entry.delete(0, 'end')
    #     self.arrow_length_entry.delete(0, 'end')
    #     self.x_min.delete(0, 'end')
    #     self.x_max.delete(0, 'end')
    #     self.y_min.delete(0, 'end')
    #     self.y_max.delete(0, 'end')
    #     self.x_label_entry.delete(0, 'end')
    #     self.y_label_entry.delete(0, 'end')

    #     config_for_entries = self.metadata[self.xsect_combo_text.get()]

    #     all_fields = ["vector_scale", 
    #                   "vertical_exaggeration",
    #                   "arrow_length",
    #                   "x_min",
    #                   "x_max",
    #                   "y_min",
    #                   "y_max",
    #                   "start_date",
    #                   "end_date",
    #                   "prec_checkbox",
    #                   "max_checkbox",
    #                   "title",
    #                   "x_label",
    #                   "y_label",
    #                   "x_grid",
    #                   "y_grid",
    #                   "avg_vectors"]
    #     for field in all_fields:
    #         if field not in config_for_entries:
    #             config_for_entries[field]=None

    def config_to_entries(self, event):
        
        all_fields = ["vector_scale", 
                    "vertical_exaggeration",
                    "arrow_length",
                    "x_min",
                    "x_max",
                    "y_min",
                    "y_max",
                    "start_date",
                    "end_date",
                    "prec_checkbox",
                    "max_checkbox",
                    "title",
                    "x_label",
                    "y_label",
                    "x_grid",
                    "y_grid",
                    "avg_vectors"]
        config_for_entries = self.metadata[self.xsect_combo_text.get()]
        for field in all_fields:
            if field not in config_for_entries:
                config_for_entries[field]=0

        self.vec_scale_entry.delete(0, 'end')
        self.vert_scale_entry.delete(0, 'end')
        self.arrow_length_entry.delete(0, 'end')
        self.x_min.delete(0, 'end')
        self.x_max.delete(0, 'end')
        self.y_min.delete(0, 'end')
        self.y_max.delete(0, 'end')
        self.x_label_entry.delete(0, 'end')
        self.y_label_entry.delete(0, 'end')


        try:
            self.title_entry.delete(0, 'end')
            self.title_entry.insert(0, config_for_entries["title"])
        except:
            pass

        # print(config_for_entries)
        try:
            self.vec_scale_entry.insert(0, config_for_entries["vector_scale"])
            self.vert_scale_entry.insert(0, config_for_entries["vertical_exaggeration"])
            self.arrow_length_entry.insert(0, config_for_entries["arrow_length"])
            self.x_min.insert(0, config_for_entries["x_min"])
            self.x_max.insert(0, config_for_entries["x_max"])
            self.y_min.insert(0, config_for_entries["y_min"])
            self.y_max.insert(0, config_for_entries["y_max"])
            self.x_label_entry.insert(0, config_for_entries["x_label"])
            self.y_label_entry.insert(0, config_for_entries["y_label"])
            
            self.start_date_combo_text.set(config_for_entries["start_date"])
            self.end_date_combo_text.set(config_for_entries["end_date"])
            self.precision_check_button_value.set(config_for_entries["prec_checkbox"])
            self.max_check_button_value.set(config_for_entries["max_checkbox"])
            self.xgrid_check_button_value.set(config_for_entries["x_grid"])
            self.ygrid_check_button_value.set(config_for_entries["y_grid"])
            self.avg_check_button_value.set(config_for_entries["avg_vectors"])
        except:
            print("No configuration loaded.")

    def plot_map(self):
        self.mapWindow = tk.Toplevel(app)
        self.mapWindow.title("Map Preview")
        self.mapWindow.geometry("600x600")
        frame_map = tk.LabelFrame(self.mapWindow)
        frame_map.grid(row=0, column=0)
        distance = float(self.line_width_entry.get())
        self.buffer_lines = self.xlines.buffer(distance=distance, cap_style=3)
        fig_map, ax = plt.subplots(1,1)
        dem_ax = show(self.dem, ax=ax)
        self.vert_transformed.plot("VEL_V", vmin=-100, vmax=100, cmap="jet_r", markersize=4, ax=ax)
        self.buffer_lines.plot(ax=ax, color="blue", alpha=0.5)
        canvas_map = FigureCanvasTkAgg(fig_map, master = self.mapWindow)
        canvas_map.draw()
        canvas_map.get_tk_widget().grid(row = 0, column = 0, padx=10)
        # creating the Matplotlib toolbar
        toolbar = NavigationToolbar2Tk(canvas_map, self.mapWindow, pack_toolbar=False)
        toolbar.grid(row=1, column=0)


    def add_watermark(self, ax, fig, dpi=None):
        if dpi == None:
            set_dpi = fig.dpi
        else:
            set_dpi = dpi
        img = Image.open(resource_path("img\TREA-logo1_rgb_hi.png"))
        width, height = ax.figure.get_size_inches()*set_dpi
        wm_width = int(width/25) # make the watermark 1/4 of the figure size
        scaling = (wm_width / float(img.size[0]))
        wm_height = int(float(img.size[1])*float(scaling))
        img = img.resize((wm_width, wm_height))

        imagebox = OffsetImage(img, zoom=1, alpha=0.4)
        imagebox.image.axes = ax

        self.ao = AnchoredOffsetbox(2, pad=0.5, borderpad=0, child=imagebox)
        self.ao.patch.set_alpha(0)
        ax.add_artist(self.ao)

    def create_xsection(self):
        res = np.min(self.dem.res) # DEM resolution

        mp_hd = []
        mp_vd = []
        mp_dist_along_profile = []
        mp_height_along_profile = []
        profile_distances = []
        profile_heights = []
        start_date = self.start_date_combo_text.get()
        end_date = self.end_date_combo_text.get()

        for prf, buff in zip(self.xlines["geometry"], self.buffer_lines): # for all x-section lines
            # Get angle coefficient of the line
            p0 = prf.boundary.geoms[0]
            p1 = prf.boundary.geoms[1]
            angle_coef = np.abs(np.sin(np.arctan2(p1.x - p0.x, p1.y - p0.y))) # Used to account for offset in angle from E-W

            # Get MPs within the buffer
            within = self.vert_transformed.within(buff) # Mask for MPs within buffer
            mp_h = self.hori_transformed[within==True] # Horizontal MPs within buffer
            mp_v = self.vert_transformed[within==True] # Vertical MPs within buffer
            mp_h = mp_h.replace(999, np.nan, )
            mp_v= mp_v.replace(999, np.nan, )

            # Get MP displacements
            d_h = (mp_h[end_date] - mp_h[start_date]) * angle_coef # Account for the angle of the profile when calculating displacement vector
            d_v = mp_v[end_date] - mp_v[start_date]
            mp_hd.append(d_h)
            mp_vd.append(d_v)

            # Project MPs onto the profile
            mp_coords = []
            mp_coords += [list(p.coords)[0] for p in mp_h["geometry"]]
            mp_dists = [prf.project(shapely.geometry.Point(p)) for p in mp_coords]
            # mp_dist_along_profile.append(mp_dists)

            # Get height of projected MPs
            mp_projected_coords = [prf.interpolate(prf.project(shapely.geometry.Point(p))).coords[0] for p in mp_coords] # Coordinates of the projected MPs along the line
            # mp_heights = np.array([x for x in self.dem.sample(mp_projected_coords)]).ravel()
            

            # Get height of the DEM surface
            s_dists = np.arange(0, prf.length, res/2) # Distances along the line with a sampling frequency adequate for the DEM resolution
            s_coords = [prf.interpolate(distance).coords[0] for distance in s_dists] # Coordinates for the DEM samples [prf.boundary.geoms[1].coords[0]]
            s_heights = np.array([x for x in self.dem.sample(s_coords)]).ravel()

            # Get height of the MPs, at positions equal to to the closest DEM coordinates
            mp_dist_nearest = s_dists[abs(np.array(mp_dists)[None, :] - s_dists[:, None]).argmin(axis=0)]
            mp_coords_shift = [prf.interpolate(distance).coords[0] for distance in mp_dist_nearest]
            mp_heights = np.array([x for x in self.dem.sample(mp_coords_shift)]).ravel() # the heights of the MPs along the profile, shifted to nearest DEM sampling coord
            mp_height_along_profile.append(mp_heights)
            mp_dist_along_profile.append(mp_dist_nearest)
            profile_distances.append(s_dists)
            profile_heights.append(s_heights)
        
        self.xlines["mp_hd"] = mp_hd
        self.xlines["mp_vd"] = mp_vd
        self.xlines["mp_dist_along_profile"] = mp_dist_along_profile
        self.xlines["mp_height_along_profile"] = mp_height_along_profile
        self.xlines["profile_distances"] = profile_distances
        self.xlines["profile_heights"] = profile_heights

    def xsection(self):
        self.xlines_select = self.xlines[self.xlines["Name"] == self.xsect_combo_text.get()]
        # print(self.xlines_select)
        # print(self.xlines_select["mp_dist_along_profile"].iloc[0])
        V = self.xlines_select["mp_vd"].iloc[0].to_numpy()
        U = self.xlines_select["mp_hd"].iloc[0].to_numpy()
        X = self.xlines_select["mp_dist_along_profile"].iloc[0]
        Y = self.xlines_select["mp_height_along_profile"].iloc[0]
        X_round = np.round(X, 1)

        print(X_round)
        X_nodup, dup_i = np.unique(X, return_index=True)
        Y_without_duplicates = Y[dup_i]

        X_without_duplicates, U_avg = zip(*(
             (k, mean(list(zip(*g))[1])) for k, g in
             groupby(sorted(zip(X, U)),
                     lambda x: x[0])))

        X_without_duplicates, V_avg = zip(*(
             (k, mean(list(zip(*g))[1])) for k, g in
             groupby(sorted(zip(X, V)),
                     lambda x: x[0])))
        
        if self.avg_check_button_value.get() == 1:
            U = U_avg
            V = V_avg
            X = X_without_duplicates
            Y = Y_without_duplicates

        print(U)
        label = self.xlines_select["Name"]

        lengths = np.sqrt(np.square(U) + np.square(V))
        angles = np.arctan2(V, U)

        colours = np.ones((len(lengths), 3))
        if self.precision_check_button_value.get() == 1:
            i_normal = np.argwhere(lengths>=5)
            i_lowp = np.argwhere(lengths<5)
            colours[i_lowp] = colours[i_lowp]*162/256
            colours[i_normal] = colours[i_normal]*0
        else:
            colours = colours*0

        if self.max_check_button_value.get() == 1:
            i_max = np.argmax(lengths)
            val_max = np.max(lengths)
            colours[i_max] = np.array([255, 0, 0])/256
        
        self.vecdata[self.xsect_combo_text.get()]["Total Displacement (mm)"] = lengths
        self.vecdata[self.xsect_combo_text.get()]["Distance (map units)"] = X
        self.vecdata[self.xsect_combo_text.get()]["Elevation (DEM units)"] = Y
        self.vecdata[self.xsect_combo_text.get()]["Vertical Displacement (mm)"] = V
        self.vecdata[self.xsect_combo_text.get()]["Horizontal Displacement (mm)"] = U

        ymin = float(self.y_min.get())
        ymax = float(self.y_max.get())
        vert_scale = float(self.vert_scale_entry.get())
        vec_scale = float(self.vec_scale_entry.get())
        mm_scale = 1 / vec_scale # scale of the arrows in mm

        key_scale = float(self.arrow_length_entry.get()) # m, y units of DEM

        fig = self.figdata[self.xsect_combo_text.get()]["fig"]
        ax = self.figdata[self.xsect_combo_text.get()]["ax"]
        ax.cla()
        legend_handles = []
        red_patch = mpatches.Patch(color='red', label='Maximum vector')
        grey_patch = mpatches.Patch(color='gray', label='Below precision (< 5 mm)')
        
        # fig, ax = plt.subplots(figsize=(8,6))
        ax.plot(self.xlines_select["profile_distances"].iloc[0], self.xlines_select["profile_heights"].iloc[0])
        ax.set_title(self.title_entry.get())
        ax.set_xlabel(self.x_label_entry.get())
        ax.set_ylabel(self.y_label_entry.get())
        q = ax.quiver(X, Y, U, V, scale=mm_scale, scale_units="x", angles="xy", width=0.002, color=colours)
        ax.quiverkey(q, X=0.8, Y=1.05, U=key_scale,
                    label="Scale: "+str(key_scale)+' mm', labelpos='E', color="k")
                    
        if self.precision_check_button_value.get() == 1:
            # ax.quiverkey(q, X=0.13, Y=1.10, U=key_scale,
            # label='<5 mm', labelpos='W', color="gray")
            legend_handles.append(grey_patch)
            

        
        if self.max_check_button_value.get() == 1:
            # ax.quiverkey(q, X=0.13, Y=1.05, U=key_scale,
            #             label="Max:", labelpos='W', color="red")
            legend_handles.append(red_patch)

        ax.set_aspect(vert_scale)
        ax.set_ylim([ymin, ymax])

        if self.xgrid_check_button_value.get() == 1 and self.ygrid_check_button_value.get() == 1:
            ax.grid(visible=True)
        elif self.xgrid_check_button_value.get() == 1 and self.ygrid_check_button_value.get() == 0:
            ax.grid(visible=True, axis="x")
        elif self.xgrid_check_button_value.get() == 0 and self.ygrid_check_button_value.get() == 1:
            ax.grid(visible=True, axis="y")
        else:
            ax.grid(visible=False)
            

        try:
            xmin = float(self.x_min.get())
            xmax = float(self.x_max.get())
        except ValueError:
            xmin, xmax = ax.get_xlim()
            self.x_min.delete(0, "end")
            self.x_max.delete(0, "end")
            self.x_min.insert(0, str(xmin))
            self.x_max.insert(0, str(xmax))

        ax.set_xlim([xmin, xmax])
        if legend_handles: 
            ax.legend(handles=legend_handles,frameon=False)        

        self.add_watermark(ax, fig)


        # self.xsectWindow = tk.Toplevel(app)
        # self.xsectWindow.title("Cross Section Preview")
        # self.xsectWindow.geometry("900x900")
        # frame_xsect = tk.LabelFrame(self.xsectWindow)
        # frame_xsect.grid(row=0, column=0)

        # frame_xsect_opts = tk.LabelFrame(self.xsectWindow)
        # frame_xsect_opts.grid(row=0, column=1)

        # button = ttk.Button(frame_xsect_opts, text='size') 
        # button.grid(row=0, column=0)
        # # creating the Tkinter canvas
        # # containing the Matplotlib figure
        # canvas = FigureCanvasTkAgg(fig,
        #                         master = self.xsectWindow)
        # canvas.draw()

        # # placing the canvas on the Tkinter window
        # canvas.get_tk_widget().grid(row = 6, column = 1, columnspan=2, padx = 5, pady = 5)

        # # creating the Matplotlib toolbar
        # toolbar = NavigationToolbar2Tk(canvas,
        #                             self.xsectWindow, pack_toolbar=False)
        # # toolbar.update()
        # toolbar.grid(row = 7, column = 1, padx = 5, pady = 5)

        # # placing the toolbar on the Tkinter window
        # canvas.get_tk_widget().grid(row = 6, column = 1, padx = 5, pady = 5)

    def plot_popup(self):
        def remove_window(window):
            window.withdraw()
        window = self.figdata[self.xsect_combo_text.get()]["window"]
        fig = self.figdata[self.xsect_combo_text.get()]["fig"]
        canvas = self.figdata[self.xsect_combo_text.get()]["canvas"]
        # ax = self.figdata[self.xsect_combo_text.get()]["ax"]
        if window == None:
            self.figdata[self.xsect_combo_text.get()]["window"] = tk.Toplevel(app)
            window = self.figdata[self.xsect_combo_text.get()]["window"]
            window.protocol("WM_DELETE_WINDOW", lambda window=window: remove_window(window))
            window.title("Cross Section Preview")
            self.figdata[self.xsect_combo_text.get()]["canvas"] = FigureCanvasTkAgg(fig, master = window)
            canvas = self.figdata[self.xsect_combo_text.get()]["canvas"]
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, columnspan=1)
            self.figdata[self.xsect_combo_text.get()]["plot_open"] = True
            toolbar = NavigationToolbar2Tk(canvas, window, pack_toolbar=False)
            toolbar.grid(row=1, column=0)
            # # Button: Select DEM
            # self.save_plot_button = ttk.Button(window, text='Select DEM', command=self.save_plot)
            # self.save_plot_button.grid(row = 1, column = 1, padx=10, pady=10,sticky="ew")
        else:
            # canvas.get_tk_widget().delete("all")
            window.deiconify()
            # canvas = FigureCanvasTkAgg(fig, master = window)
            canvas.draw()
            # canvas.get_tk_widget().grid(row=0, column=0)

    
    def plot_all(self):
        self.create_xsection()
        # fp = tk.filedialog.askdirectory(title='Select a folder', initialdir='/',)
        for xsect in self.xsect_combo["values"]:
            self.update_metadata()
            self.xsect_combo_text.set(xsect)
            
            
            self.config_to_entries("event")
            # self.update_metadata()
            self.xsection()
            self.plot_popup()

    def save_plots(self):
        dpi=300
        self.create_xsection()
        fp = tk.filedialog.askdirectory(title='Select a folder',)
        for xsect in self.xsect_combo["values"]:
            self.update_metadata()
            self.xsect_combo_text.set(xsect)
            
            
            self.config_to_entries("event")
            # self.update_metadata()
            self.xsection()

        for figname, figdata in self.figdata.items():
            try:
                print(figname, figdata)
                figdata = figdata["fig"]
                # print(fp+figname+".png")
                figdata.savefig(fp+"/"+figname+".png", dpi=dpi)
            except ValueError:
                # print(fp+figname+".png")
                pass
    
    def test(self):
        test = ["a", "b", "c"]
        for val in test:
            self.xsect_combo_text.set(val)
            print(val)
            self.test2()
    
    def test2(self):
        print("cb 2 triggered")
        
            
        # fig = self.figdata[self.xsect_combo_text.get()]["fig"]
        # ax = self.figdata[self.xsect_combo_text.get()]["ax"]
        # self.ao.remove()
        # self.add_watermark(ax, fig, dpi=dpi)
        # fig.savefig("test_img.png", dpi=dpi)

        

        # # self.xsectWindow.geometry("900x900")
        # # fig, ax = plt.subplots(figsize=(8,6))
        # self.canvas = FigureCanvasTkAgg(fig,
        #                         master = self.xsectWindow)
        
        # self.canvas.draw()
        # self.canvas.get_tk_widget().pack()
        

    # def edit_plot(self):
    #     self.canvas.get_tk_widget().delete("all")
    #     # self.fig, self.ax = plt.subplots(figsize=(8,6))
    #     self.ax.set_title(self.entry_set_title.get())
    #     self.canvas = FigureCanvasTkAgg(self.fig,
    #                             master = self.xsectWindow)
    #     self.canvas.draw()
    #     self.canvas.get_tk_widget().grid(row = 0, column = 0, padx = 5, pady = 5)        
# 

if __name__ == "__main__":
  app = App()
  app.protocol("WM_DELETE_WINDOW", sys.exit)
  app.mainloop()
