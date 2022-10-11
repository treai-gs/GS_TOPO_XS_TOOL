import tkinter as tk
from tkinter import BooleanVar, messagebox
from tkinter import ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
NavigationToolbar2Tk)
from matplotlib import pyplot as plt
from matplotlib.collections import EllipseCollection
import matplotlib.image as image
from matplotlib.offsetbox import (OffsetImage,AnchoredOffsetbox)
from PIL import Image

import numpy as np
import geopandas as gpd
import rasterio as rio
from rasterio.plot import show
import shapely
from pyproj import _datadir, datadir
import sys, os


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

frame_styles = {"relief": "groove",
                "bd": 3, "bg": "#BEB2A7",
                "fg": "#073bb3", "font": ("Arial", 9, "bold")}



class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        menu_file = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Menu1", menu=menu_file)
        menu_file.add_command(label="All Widgets", command=lambda: parent.show_frame(MainPage))
        menu_file.add_separator()
        menu_file.add_command(label="Exit Application", command=lambda: parent.Quit_application())


class MyApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        main_frame = tk.Frame(self, bg="#84CEEB", height=1024, width=1024)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        # self.resizable(0, 0) prevents the app from being resized
        # self.geometry("1024x600") fixes the applications size
        self.frames = {}
        pages = (MainPage, PageOne)
        for F in pages:
            frame1 = F(main_frame, self)
            self.frames[F] = frame1
            frame1.grid(row=0, column=0, sticky="nsew")
        self.show_frame(MainPage)
        menubar = MenuBar(self)
        tk.Tk.config(self, menu=menubar)

    def show_frame(self, name):
        frame1 = self.frames[name]
        frame1.tkraise()

    def Quit_application(self):
        self.destroy()


class GUI(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.main_frame = tk.Frame(self, bg="#BEB2A7", height=1000, width=1920)
        # self.main_frame.pack_propagate(0)
        self.main_frame.pack(fill="both", expand="true")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)


class MainPage(GUI):  # inherits from the GUI class
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        frame1 = tk.LabelFrame(self, frame_styles, text="Data Upload")
        frame1.place(rely=0.01, relx=0.02, height=600, width=800)

        frame2 = tk.LabelFrame(self, frame_styles, text="Map Preview")
        frame2.place(rely=0.25, relx=0.02, height=600, width=800)

        frame3 = tk.LabelFrame(self, frame_styles, text="Cross Section Options")
        frame3.place(rely=0.01, relx=0.45, height=400, width=900)

        frame4 = tk.LabelFrame(self, frame_styles, text="Cross Section Preview")
        frame4.place(rely=0.25, relx=0.45, height=700, width=900)

        # Functions
        dem_fp = ""
        xlines_fp = ""
        mp_v_fp = ""
        mp_h_fp = ""

        # function for selecting DEM input
        def select_dem():
            global dem
            global dem_fp
            filetypes = (
                ('GeoTIFF files', '*.tif'),
                ('All files', '*.*')
            )

            dem_fp = tk.filedialog.askopenfilename(
                title='Open a file',
                initialdir='/',
                filetypes=filetypes)
            dem = rio.open(dem_fp) # DEM object containing the data, CRS, and other useful attributes
            dem_path.config(text=dem_fp)

        def select_xlines():
            global xlines, xlines_fp
            filetypes = (
                ('Shapefiles', '*.shp'),
                ('All files', '*.*')
            )

            xlines_fp = tk.filedialog.askopenfilename(
                title='Open a file',
                initialdir='/',
                filetypes=filetypes)
            xlines = gpd.read_file(xlines_fp) # horizontal MPs geopandas dataframe
            xlines_path.config(text=xlines_fp)



        def select_mp_v():
            global vert_transformed, mp_v_fp
            filetypes = (
                ('Shapefiles', '*.shp'),
                ('All files', '*.*')
            )

            mp_v_fp = tk.filedialog.askopenfilename(
                title='Open a file',
                initialdir='/',
                filetypes=filetypes)
            vert = gpd.read_file(mp_v_fp) # vertical MPs geopandas dataframe
            vert_transformed = vert.to_crs(xlines.crs)
            mp_v_path.config(text=mp_v_fp)
            list_items.set([col for col in vert_transformed if col.startswith('D')])


        def select_mp_h():
            global hori_transformed, mp_h_fp
            filetypes = (
                ('Shapefiles', '*.shp'),
                ('All files', '*.*')
            )

            mp_h_fp = tk.filedialog.askopenfilename(
                title='Open a file',
                initialdir='/',
                filetypes=filetypes)
            hori = gpd.read_file(mp_h_fp) # horizontal MPs geopandas dataframe
            hori_transformed = hori.to_crs(xlines.crs)
            mp_h_path.config(text=mp_h_fp)

        def buffer_size():
            global buffer_lines
            distance = float(buffer_entry.get())
            buffer_lines = xlines.buffer(distance=distance, cap_style=3)
        
        def create_xsection():
            res = np.min(dem.res) # DEM resolution

            mp_hd = []
            mp_vd = []
            mp_std_h = []
            mp_std_v = []
            mp_dist_along_profile = []
            mp_height_along_profile = []
            profile_distances = []
            profile_heights = []
            date = w.get(w.curselection()[0])
            print(date)


            for prf, buff in zip(xlines["geometry"], buffer_lines): # for all x-section lines
                # Get angle coefficient of the line
                p0 = prf.boundary.geoms[0]
                p1 = prf.boundary.geoms[1]
                angle_coef = np.abs(np.sin(np.arctan2(p1.x - p0.x, p1.y - p0.y))) # Used to account for offset in angle from E-W

                # Get MPs within the buffer
                within = vert_transformed.within(buff) # Mask for MPs within buffer
                mp_h = hori_transformed[within==True] # Horizontal MPs within buffer
                mp_v = vert_transformed[within==True] # Vertical MPs within buffer

                # Get MP displacements
                d_h = mp_h[date] * angle_coef # Account for the angle of the profile when calculating displacement vector
                d_v = mp_v[date]
                mp_hd.append(d_h)
                mp_vd.append(d_v)

                # Get MP STD for error ellipses
                std_h =  mp_h["V_STDEV_E"] * angle_coef
                std_v =  mp_v["V_STDEV_V"]
                mp_std_h.append(std_h)
                mp_std_v.append(std_v)

                # Project MPs onto the profile
                mp_coords = []
                mp_coords += [list(p.coords)[0] for p in mp_h["geometry"]]
                mp_dists = [prf.project(shapely.geometry.Point(p)) for p in mp_coords]
                mp_dist_along_profile.append(mp_dists)

                # Get height of projected MPs
                mp_projected_coords = [prf.interpolate(prf.project(shapely.geometry.Point(p))).coords[0] for p in mp_coords] # Coordinates of the projected MPs along the line
                mp_heights = np.array([x for x in dem.sample(mp_projected_coords)]).ravel()
                mp_height_along_profile.append(mp_heights)

                # Get height of the DEM surface
                s_dists = np.arange(0, prf.length, res/2) # Distances along the line with a sampling frequency adequate for the DEM resolution
                s_coords = [prf.interpolate(distance).coords[0] for distance in s_dists] # Coordinates for the DEM samples [prf.boundary.geoms[1].coords[0]]
                s_heights = np.array([x for x in dem.sample(s_coords)]).ravel()
                profile_distances.append(s_dists)
                profile_heights.append(s_heights)
            
            xlines["mp_hd"] = mp_hd
            xlines["mp_vd"] = mp_vd
            xlines["mp_std_h"] = mp_std_h
            xlines["mp_std_v"] = mp_std_v
            xlines["mp_dist_along_profile"] = mp_dist_along_profile
            xlines["mp_height_along_profile"] = mp_height_along_profile
            xlines["profile_distances"] = profile_distances
            xlines["profile_heights"] = profile_heights

        def xsection():
            xi = 0
            V = xlines["mp_vd"][xi]
            U = xlines["mp_hd"][xi]
            X = xlines["mp_dist_along_profile"][xi]
            Y = xlines["mp_height_along_profile"][xi]
            s_h = xlines["mp_std_h"][xi]
            s_v = xlines["mp_std_v"][xi]
            label = xlines["Name"][xi]

            ymin = float(ylim_min_entry.get())
            ymax = float(ylim_max_entry.get())
            aspect = float(aspect_entry.get())
            scale_factor = float(scale_entry.get())
            mm_scale = 1 / scale_factor # scale of the arrows in mm

            key_scale = float(arrow_size_entry.get()) # m, y units of DEM


            fig, ax = plt.subplots(figsize=(8,6))
            ax.plot(xlines["profile_distances"][xi], xlines["profile_heights"][xi])
            ax.set_title(label)
            q = ax.quiver(X, Y, U, V, scale=mm_scale, scale_units="xy", angles="xy", width=0.002)
            ax.quiverkey(q, X=0.87, Y=1.05, U=key_scale,
                        label=str(key_scale)+' mm', labelpos='E')
            ax.set_aspect(aspect)
            ax.set_ylim([ymin, ymax])

            if ellipse_on.get() == True:
                ec = EllipseCollection(s_h, s_v, angles=np.ones_like(s_h)*0, units="y", offsets=np.array([X+U/mm_scale, Y+V/mm_scale]).T, offset_transform=ax.transData)
                ec.set_edgecolor("red")
                ec.set_facecolor("none")
                ax.add_collection(ec)            

            add_watermark(ax, fig)

            # creating the Tkinter canvas
            # containing the Matplotlib figure
            canvas = FigureCanvasTkAgg(fig,
                                    master = frame4)
            canvas.draw()

            # placing the canvas on the Tkinter window
            canvas.get_tk_widget().grid(row = 6, column = 1, columnspan=2, padx = 5, pady = 5)

            # creating the Matplotlib toolbar
            toolbar = NavigationToolbar2Tk(canvas,
                                        frame4, pack_toolbar=False)
            # toolbar.update()
            toolbar.grid(row = 7, column = 1, padx = 5, pady = 5)

            # placing the toolbar on the Tkinter window
            canvas.get_tk_widget().grid(row = 6, column = 1, padx = 5, pady = 5)

        def plot():
            # the figure that will contain the plot
            fig, ax = plt.subplots(figsize=(5,5))
            # plotting the graph
            dem_ax = show(dem, ax=ax)
            vert_transformed.plot("VEL_V", vmin=-100, vmax=100, cmap="Spectral", markersize=4, ax=ax)
            buffer_lines.plot(ax=ax, color="blue", alpha=0.5)
            


            
            # creating the Tkinter canvas
            # containing the Matplotlib figure
            canvas = FigureCanvasTkAgg(fig,
                                    master = frame2)
            canvas.draw()

            # placing the canvas on the Tkinter window
            canvas.get_tk_widget().grid(row = 6, column = 1, columnspan=2, padx = 5, pady = 5)

            # creating the Matplotlib toolbar
            toolbar = NavigationToolbar2Tk(canvas,
                                        frame2, pack_toolbar=False)
            # toolbar.update()
            toolbar.grid(row = 7, column = 1, padx = 5, pady = 5)

            # placing the toolbar on the Tkinter window
            canvas.get_tk_widget().grid(row = 6, column = 1, padx = 5, pady = 5)

        def openNewWindow(xsection):

            label = xsection["Name"]
            # Toplevel object which will
            # be treated as a new window
            newWindow = tk.Toplevel(root)
        
            # sets the title of the
            # Toplevel widget
            newWindow.title("New Window")
        
            # sets the geometry of toplevel
            newWindow.geometry("900x900")
            fr = tk.LabelFrame(newWindow, text=label)
            fr.place(rely=0.01, relx=0.02, height=800, width=800)
            V = xsection["mp_vd"]
            U = xsection["mp_hd"]
            X = xsection["mp_dist_along_profile"]
            Y = xsection["mp_height_along_profile"]
            s_h = xsection["mp_std_h"]
            s_v = xsection["mp_std_v"]

            ymin = float(ylim_min_entry.get())
            ymax = float(ylim_max_entry.get())
            aspect = float(aspect_entry.get())
            # ymin = np.min(xsection["profile_distances"])
            # ymax = np.max(xsection["profile_distances"])
            

            scale_factor = float(scale_entry.get())
            mm_scale = 1 / scale_factor # scale of the arrows 

            key_scale = float(arrow_size_entry.get()) # m, y units of DEM


            fig, ax = plt.subplots(figsize=(8,6))
            ax.plot(xsection["profile_distances"], xsection["profile_heights"])
            ax.set_title(label)

            q = ax.quiver(X, Y, U, V, scale=mm_scale, scale_units="xy", angles="xy", width=0.002)
            ax.quiverkey(q, X=0.87, Y=1.05, U=key_scale,
                        label=str(key_scale)+' mm', labelpos='E')
            ax.set_aspect(aspect)
            ax.set_ylim([ymin, ymax])

            if ellipse_on.get() == True:
                ec = EllipseCollection(s_h, s_v, angles=np.ones_like(s_h)*0, units="y", offsets=np.array([X+U/mm_scale, Y+V/mm_scale]).T, offset_transform=ax.transData)
                ec.set_edgecolor("red")
                ec.set_facecolor("none")
                ax.add_collection(ec)

            add_watermark(ax, fig)

            # creating the Tkinter canvas
            # containing the Matplotlib figure
            canvas = FigureCanvasTkAgg(fig, master = fr)
            canvas.draw()
            # placing the canvas on the Tkinter window
            canvas.get_tk_widget().grid(row = 6, column = 1, columnspan=2, padx = 5, pady = 5)

            # creating the Matplotlib toolbar
            toolbar = NavigationToolbar2Tk(canvas,
                                        fr, pack_toolbar=False)
            # toolbar.update()
            toolbar.grid(row = 7, column = 1, padx = 5, pady = 5)

            # placing the toolbar on the Tkinter window
            canvas.get_tk_widget().grid(row = 6, column = 1, padx = 5, pady = 5)

            

        
        def openAllWindows():
            for i, xsection in xlines.iterrows():
                openNewWindow(xsection)

        dem_button = ttk.Button(
            frame1,
            text='Load DEM',
            command=select_dem
        )
        dem_button.grid(row = 0, column = 0, padx = 5, pady = 5, sticky="W")

        dem_path = tk.Label(frame1, text=dem_fp, anchor='w')
        dem_path.grid(row = 0, column = 1, padx = 5, pady = 5, sticky="W")


        def add_watermark(ax, fig):
            img = Image.open(resource_path("img\TREA-logo1_rgb_hi.png"))
            width, height = ax.figure.get_size_inches()*fig.dpi
            wm_width = int(width/25) # make the watermark 1/4 of the figure size
            scaling = (wm_width / float(img.size[0]))
            wm_height = int(float(img.size[1])*float(scaling))
            img = img.resize((wm_width, wm_height))

            imagebox = OffsetImage(img, zoom=1, alpha=0.4)
            imagebox.image.axes = ax

            ao = AnchoredOffsetbox(2, pad=0.5, borderpad=0, child=imagebox)
            ao.patch.set_alpha(0)
            ax.add_artist(ao)


        # xlines button
        xlines_button = ttk.Button(
            frame1,
            text='Load cross section lines',
            command=select_xlines
        )
        xlines_button.grid(row = 1, column = 0, padx = 5, pady = 5, sticky="W")

        xlines_path = tk.Label(frame1, text=xlines_fp, anchor='w')
        xlines_path.grid(row = 1, column = 1, padx = 5, pady = 5, sticky="W")

        # Vert MPs button
        mp_v_button = ttk.Button(
            frame1,
            text='Load Vertical MPs',
            command=select_mp_v
        )
        mp_v_button.grid(row = 2, column = 0, padx = 5, pady = 5, sticky="W")

        mp_v_path = tk.Label(frame1, text=mp_v_fp, anchor='w')
        mp_v_path.grid(row = 2, column = 1, padx = 5, pady = 5, sticky="W")

        # Hori MPs button
        mp_h_button = ttk.Button(
            frame1,
            text='Load Horizontal MPs',
            command=select_mp_h
        )
        mp_h_button.grid(row = 3, column = 0, padx = 5, pady = 5, sticky="W")

        mp_h_path = tk.Label(frame1, text=mp_h_fp, anchor='w')
        mp_h_path.grid(row = 3, column = 1, padx = 5, pady = 5, sticky="W")

        buffer_entry = tk.Entry(frame1)
        buffer_entry.grid(row = 4, column = 1, padx = 5, pady = 5,sticky="W")
        buffer_label = tk.Label(frame1, text="Cross Section Width", anchor='w')
        buffer_label.grid(row = 4, column = 0, padx = 5, pady = 5, sticky="W")

        # button that displays the map plot
        plot_button = tk.Button(master = frame1,
                            command = lambda: [buffer_size(), plot()],
                            height = 2,
                            width = 10,
                            text = "Plot")
        plot_button.grid(row = 5, column = 1, padx = 5, pady = 5, sticky="W")

        # button that displays the map plot
        plot_xsection = tk.Button(master = frame3,
                            command = lambda: [create_xsection(), xsection()],
                            height = 2,
                            width = 10,
                            text = "Plot")
        plot_xsection.grid(row = 1, column = 0, padx = 5, pady = 5, sticky="W")

        # button that displays the map plot
        plot_all = tk.Button(master = frame3,
                            command = lambda: [openAllWindows()],
                            height = 2,
                            width = 10,
                            text = "Plot All")
        plot_all.grid(row = 1, column = 1, padx = 5, pady = 5, sticky="W")


        scale_label = tk.Label(frame3, text="Vector Scale")
        scale_label.grid(row = 5, column = 0, padx = 5, pady = 5, sticky="W")

        scale_entry = tk.Entry(frame3)
        scale_entry.insert(tk.END, "1.0")
        scale_entry.grid(row = 5, column = 1, padx = 5, pady = 5,sticky="W")

        aspect_label = tk.Label(frame3, text="Vertical Exaggeration")
        aspect_label.grid(row = 5, column = 2, padx = 5, pady = 5, sticky="W")

        aspect_entry = tk.Entry(frame3)
        aspect_entry.insert(tk.END, "1.0")
        aspect_entry.grid(row = 5, column = 3, padx = 5, pady = 5,sticky="W")

        ylim_label = tk.Label(frame3, text="Y Min, Y Max (m)")
        ylim_label.grid(row = 6, column = 0, padx = 5, pady = 5, sticky="W")

        ylim_min_entry = tk.Entry(frame3)
        ylim_min_entry.grid(row = 6, column = 1, padx = 5, pady = 5,sticky="W")

        ylim_max_entry = tk.Entry(frame3)
        ylim_max_entry.grid(row = 6, column = 2, padx = 5, pady = 5,sticky="W")

        date_label = tk.Label(frame3, text="Displacement Date")
        date_label.grid(row = 1, column = 2, padx = 5, pady = 5, sticky="W")

        list_items = tk.Variable(value=[""])

        w = tk.Listbox(frame3, height=4, listvariable=list_items, selectmode="SINGLE")
        w.grid(row = 1, column = 3, rowspan=4, padx = 5, pady = 5,sticky="NS")

        # link a scrollbar to a list
        scrollbar = ttk.Scrollbar(
            frame3,
            orient=tk.VERTICAL,
            command=w.yview,
        )

        w['yscrollcommand'] = scrollbar.set

        scrollbar.grid(row=1, column=4, rowspan=4, sticky='nsw')
        ellipse_on = BooleanVar()
        ellipse_toggle = tk.Checkbutton(frame3, text = "Error Ellipses", variable=ellipse_on)
        ellipse_toggle.grid(row = 6, column = 3, rowspan=4, padx = 5, pady = 5,sticky="W")

        arrow_size_label = tk.Label(frame3, text="Arrow Length (mm)")
        arrow_size_label.grid(row = 7, column = 0, padx = 5, pady = 5, sticky="W")

        arrow_size_entry = tk.Entry(frame3)
        arrow_size_entry.grid(row = 7, column = 1, padx = 5, pady = 5,sticky="W")

class PageOne(GUI):
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        label1 = tk.Label(self.main_frame, font=("Verdana", 20), text="Page One")
        label1.pack(side="top")





top = MyApp()
top.title("Tkinter App Template - Login Page")
root = MyApp()
root.withdraw()
root.title("Tkinter App Template")

root.mainloop()
