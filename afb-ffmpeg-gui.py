"""
    AFB FFmpeg GUI
    A simple interface made using Python & Tkinter to speed up FFmpeg video to image sequence conversions. 
    (fourth draft adds threading, still only a little error checking)
"""
import os
from pathlib import Path
import subprocess
import json
from math import gcd
from decimal import Decimal, ROUND_HALF_DOWN
import textwrap
import tempfile
import re
from threading import Thread
from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import PhotoImage


class MainWindow:

    def __init__(self, root):

        # Define custom fonts
        font_heading = font.Font(size=13, weight="bold")
        font_bold = font.Font(weight="bold")
        font_italic = font.Font(slant="italic")
        font_note = font.Font(size=10, slant="italic")

        # Default variables
        self.defaults = {
        "in" : "Input file path",
        "auto_folder" : True,
        "auto_file" : True,
        "out" : "Output folder path",
        "out_file" : "image",
        "sep" : "_", 
        "pad_check" : True,
        "fmt" : "png",
        "fps" : "Auto",
        "scale" : 1.00,
        "trim_check" : False,
        "trim_method" : "Frames",
        "trim_start_f" : 1,
        "trim_end_f" : 2,
        "trim_start_h" : 0,
        "trim_start_m" : 0,
        "trim_start_s" : 0,
        "trim_end_h" : 0,
        "trim_end_m" : 0,
        "trim_end_s" : 0,
        "start_frame_check" : False,
        "overwrite" : True,
        "process_label" : "Select a file first, or click to process file added manually",
        "cmd_label" : "Select desired options then click to make the FFmpeg command",
        "cmd" : "The FFmpeg command will show here",
        "progress" : "",
        "meta" : ""
        }
        self.hideable = ["options_frame", "cmd_button", "cmd_label", "meta_head", "preview_head", "progress_bar", "view_button", "trim_frame", "copy_cmd_button"]
        self.last_processed = ""
        self.in_folder = ""

        root.title("AFB FFmpeg Video to Image Sequence GUI")

        # Create main window frame
        main_frame = ttk.Frame(root, padding=(10, 10, 10, 10))
        main_frame.grid(column=0, row=0, sticky="NSEW")

        # Input label
        ttk.Label(main_frame, text="Input file", font=font_heading).grid(column=1, row=1, sticky="W")

        # Input text entry field
        self.in_var = StringVar(value=self.defaults["in"])
        in_entry = ttk.Entry(main_frame, width=50, textvariable=self.in_var)
        in_entry.grid(column=1, columnspan=3, row=2, sticky="EW")

        # Input selector button
        in_button = ttk.Button(main_frame, text="File", command=self.choose_input, padding=(5, 2, 5, 2), cursor="hand2")
        in_button.grid(column=4, row=2, sticky="EW")

        # Auto output folder name option
        self.auto_folder_var = BooleanVar(value=self.defaults["auto_folder"])
        self.folder_check = Checkbutton(main_frame, text="Auto folder name", variable=self.auto_folder_var, font=font_italic, cursor="hand2")
        self.folder_check.grid(column=3, row=3, sticky="NW")

        # Auto output file name option
        self.auto_file_var = BooleanVar(value=self.defaults["auto_file"])
        self.file_check = Checkbutton(main_frame, text="Auto file name", variable=self.auto_file_var, font=font_italic, cursor="hand2")
        self.file_check.grid(column=4, row=3, sticky="NW")

        # Output label
        ttk.Label(main_frame, text="Output folder", font=font_heading).grid(column=1, row=3, sticky="W")

        # Output text entry field
        self.out_var = StringVar(value=self.defaults["out"])
        out_entry = ttk.Entry(main_frame, textvariable=self.out_var)
        out_entry.grid(column=1, columnspan=3, row=4, sticky="EW")

        # Output selector button
        out_button = ttk.Button(main_frame, text="Folder", command=self.choose_output, padding=(5, 2, 5, 2), cursor="hand2")
        out_button.grid(column=4, row=4, sticky="EW")
        
        # Output file name label
        ttk.Label(main_frame, text="Output file name", font=font_heading).grid(column=1, row=5, sticky="W")

        # Output text entry field
        self.out_file_var = StringVar(value=self.defaults["out_file"])
        out_file_entry = ttk.Entry(main_frame, textvariable=self.out_file_var)
        out_file_entry.grid(column=1, columnspan=3, row=6, sticky="WE")

        # Note label
        ttk.Label(main_frame, text="Note: Frame number and extension will be added automatically based on options below (e.g. image_%02d.png), so do not add them manually here", font=font_note, wraplength=475, justify="center").grid(column=1, columnspan=3, row=7, sticky="W")

        # Reset the whole tool button
        reset_button = ttk.Button(main_frame, text="Reset tool", command=self.reset_tool, padding=(5, 2, 5, 2), cursor="hand2")
        reset_button.grid(column=4, row=6, sticky="EW")

        # Options Frame
        self.options_frame = ttk.Frame(main_frame)
        self.options_frame.grid(column=1, columnspan=4, row=8, sticky="NSEW")
         
        # Options label
        ttk.Label(self.options_frame, text="Options", font=font_heading, width=15).grid(column=1, row=1, sticky="W")

        # Format Label
        ttk.Label(self.options_frame, text="Image format", font=font_italic).grid(column=1, row=2, sticky="W")

        # Image format options
        fmt_list = ["png", "jpg", "exr", "webp", "tif", "bmp", "tga"] # Maybe add a custom option?
        self.fmt_var = StringVar(value=self.defaults["fmt"])
        format_menu = ttk.Combobox(self.options_frame, width = 8, textvariable = self.fmt_var, values = fmt_list, state="readonly", cursor="hand2")
        format_menu.grid(column=2, row=2, sticky="NW")
        
        # FPS
        ttk.Label(self.options_frame, text="FPS", font=font_italic).grid(column=1, row=3, sticky="W")
        
        # FPS options
        fps_list = ["Auto", "1", "5", "10", "12", "15", "20", "23.976", "24", "25", "29.97", "30", "48", "50", "59.94", "60", "96", "119.88", "120"] # Maybe add a custom option?
        self.fps_var = StringVar(value=self.defaults["fps"])
        fps_menu = ttk.Combobox(self.options_frame, width = 8, values=fps_list, textvariable = self.fps_var, state="readonly", cursor="hand2")
        fps_menu.grid(column=2, row=3, sticky="NW")
        
        # Scale Label
        ttk.Label(self.options_frame, text="Scale", font=font_italic).grid(column=1, row=4, sticky="W")
        
        # Scaling options
        scale_list = [0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0] # Maybe add a custom option?
        self.scale_var = StringVar(value=self.defaults["scale"])
        scale_menu = ttk.Combobox(self.options_frame, width = 8, values=scale_list, textvariable = self.scale_var, cursor="hand2")
        scale_menu.grid(column=2, row=4, sticky="NW")

        # File number separator label
        ttk.Label(self.options_frame, text="Suffix separator", font=font_italic).grid(column=1, row=5, sticky="W")

        # File number separator options
        sep_list = ["_", "-", ".", "~", "Space", "@", "None"] # Maybe add a custom option?
        self.sep_var = StringVar(value=self.defaults["sep"])
        sep_menu = ttk.Combobox(self.options_frame, width = 8, textvariable = self.sep_var, values = sep_list, state="readonly", cursor="hand2")
        sep_menu.grid(column=2, row=5, sticky="NW")
        
        # File number padding check option
        self.pad_check_var = BooleanVar(value=self.defaults["pad_check"])
        self.pad_check = Checkbutton(self.options_frame, text="Pad numbers", variable=self.pad_check_var, font=font_italic, cursor="hand2")
        self.pad_check.grid(column=3, row=5, sticky="NW", padx=38)

        # Overwrite Option
        self.overwrite_var = BooleanVar(value=self.defaults["overwrite"])
        self.overwrite_check = Checkbutton(self.options_frame, text="Overwrite files", variable=self.overwrite_var, font=font_italic, cursor="hand2")
        self.overwrite_check.grid(column=4, row=5, sticky="NW")
        
        # Metadata from input video file
        self.meta_head = ttk.Label(self.options_frame, text="Input metadata", font=font_bold, justify="left", width=22)
        self.meta_head.grid(column=3, row=1, sticky="NW", padx=40)

        # Metadata Label
        self.meta_var = StringVar(value=self.defaults["meta"])
        meta_label_txt = ttk.Label(self.options_frame, textvariable=self.meta_var, justify="left")
        meta_label_txt.grid(column=3, row=2, rowspan=3, sticky="NW", padx=40)

        # Preview image heading
        self.preview_head = ttk.Label(self.options_frame, text="Preview image", font=font_bold, justify="left")
        self.preview_head.grid(column=4, row=1, sticky="NW")
        
        # Empty preview image space
        self.empty_img = PhotoImage()
        self.preview_image = ttk.Label(self.options_frame, anchor="center")
        self.preview_image.grid(column=4, row=2, rowspan=3, sticky="NESW")

        # Trim clip check option
        self.trim_check_var = BooleanVar(value=self.defaults["trim_check"]) # False by default
        self.trim_check = Checkbutton(self.options_frame, text="Trim clip", variable=self.trim_check_var, command = self.toggle_trim, font=font_italic, cursor="hand2")
        self.trim_check.grid(column=1, row=6, sticky="NW")

        # Trim options hideable frame
        self.trim_frame = ttk.Frame(self.options_frame)
        self.trim_frame.grid(column=2, columnspan=3, row=6, sticky="NSEW")

        # Trim method options
        self.trim_method_var = StringVar(value=self.defaults["trim_method"])
        
        trim_by_frame = ttk.Radiobutton(self.trim_frame, variable=self.trim_method_var, text = "Frames", value = "Frames", width=8, command=self.toggle_method, cursor="hand2")
        trim_by_frame.grid(column=1, row=1, sticky="NW")

        trim_by_time = ttk.Radiobutton(self.trim_frame, variable=self.trim_method_var, text = "Time", value = "Time", width=8, command=self.toggle_method, cursor="hand2")
        trim_by_time.grid(column=1, row=2, sticky="NW")

        # Trim spinbox hideable frames
        # By Frame
        self.trim_f_frame = ttk.Frame(self.trim_frame)
        self.trim_f_frame.grid(column=2, columnspan=2, row=1, rowspan=2, sticky="NSEW")
        
        # Trim start label
        ttk.Label(self.trim_f_frame, text="Start frame:").grid(column=1, row=1, sticky="NE", padx=10, pady=3)
        
        # Trim end label
        ttk.Label(self.trim_f_frame, text="End frame:").grid(column=1, row=2, sticky="NE", padx=10)
        
        # Trim start / end spin boxes
        self.trim_start_f_var = StringVar(value=self.defaults["trim_start_f"]) # First frame by default

        self.start_f_spinbox = ttk.Spinbox(self.trim_f_frame, from_=1, textvariable=self.trim_start_f_var, justify="left", width=7) # max last frame number minus 1 so that there aren't no frames after trim
        self.start_f_spinbox.grid(column=2, row=1, sticky="NE", padx=5)
        
        self.trim_end_f_var = StringVar(value=self.defaults["trim_end_f"]) # Last frame by default

        self.end_f_spinbox = ttk.Spinbox(self.trim_f_frame, from_=1, textvariable=self.trim_end_f_var, justify="left", width=7) # min second frame so that there aren't no frames after trim
        self.end_f_spinbox.grid(column=2, row=2, sticky="NE", padx=5)

        # By Time
        self.trim_t_frame = ttk.Frame(self.trim_frame)
        self.trim_t_frame.grid(column=2, columnspan=2, row=1, rowspan=2, sticky="NSEW")
        self.trim_t_frame.grid_remove()
        
        # Trim start labels
        ttk.Label(self.trim_t_frame, text="Start time:").grid(column=1, row=1, sticky="NE", padx=10, pady=3)
        ttk.Label(self.trim_t_frame, text="h").grid(column=3, row=1, sticky="NW", padx=3)
        ttk.Label(self.trim_t_frame, text="m").grid(column=5, row=1, sticky="NW", padx=3)
        ttk.Label(self.trim_t_frame, text="s").grid(column=7, row=1, sticky="NW", padx=3)

        
        # Trim end labels
        ttk.Label(self.trim_t_frame, text="End time:").grid(column=1, row=2, sticky="NE", padx=10)
        ttk.Label(self.trim_t_frame, text="h").grid(column=3, row=2, sticky="NW", padx=3)
        ttk.Label(self.trim_t_frame, text="m").grid(column=5, row=2, sticky="NW", padx=3)
        ttk.Label(self.trim_t_frame, text="s").grid(column=7, row=2, sticky="NW", padx=3)

        # Trim start / end spin boxes
        self.trim_start_h_var = StringVar(value=self.defaults["trim_start_h"])
        self.trim_start_m_var = StringVar(value=self.defaults["trim_start_m"])
        self.trim_start_s_var = StringVar(value=self.defaults["trim_start_s"])

        self.start_h_spinbox = ttk.Spinbox(self.trim_t_frame, from_=0, to=999, textvariable=self.trim_start_h_var, justify="left", width=3)
        self.start_h_spinbox.grid(column=2, row=1, sticky="NE", padx=5)
        
        self.start_m_spinbox = ttk.Spinbox(self.trim_t_frame, from_=0, to=59, textvariable=self.trim_start_m_var, justify="left", width=3)
        self.start_m_spinbox.grid(column=4, row=1, sticky="NE", padx=5)
        
        self.start_s_spinbox = ttk.Spinbox(self.trim_t_frame, from_=0, to=59, textvariable=self.trim_start_s_var, justify="left", width=4)
        self.start_s_spinbox.grid(column=6, row=1, sticky="NE", padx=5)

        self.trim_end_h_var = StringVar(value=self.defaults["trim_end_h"])
        self.trim_end_m_var = StringVar(value=self.defaults["trim_end_m"])
        self.trim_end_s_var = StringVar(value=self.defaults["trim_end_s"])

        self.end_h_spinbox = ttk.Spinbox(self.trim_t_frame, from_=0, to=999, textvariable=self.trim_end_h_var, justify="left", width=3)
        self.end_h_spinbox.grid(column=2, row=2, sticky="NE", padx=5)

        self.end_m_spinbox = ttk.Spinbox(self.trim_t_frame, from_=0, to=59, textvariable=self.trim_end_m_var, justify="left", width=3) # min second frame so that there aren't no frames after trim
        self.end_m_spinbox.grid(column=4, row=2, sticky="NE", padx=5)

        self.end_s_spinbox = ttk.Spinbox(self.trim_t_frame, from_=0, to=59, textvariable=self.trim_end_s_var, justify="left", width=4)
        self.end_s_spinbox.grid(column=6, row=2, sticky="NE", padx=5)

        # Notes for trimming
        ttk.Label(self.trim_f_frame, text="Note: Trim is inclusive (e.g. 'start 4 end 5' = frames 4 and 5); start frame will be 1 less in FFmpeg command", font=font_note, wraplength=225).grid(column=3, row=1, rowspan=2, sticky="NW", padx=20)
        ttk.Label(self.trim_t_frame, text="Note: Subseconds allowed but trim by frame may be simpler", font=font_note, wraplength=200).grid(column=8, row=1, sticky="NW", padx=10)
        self.time_per_frame_var = StringVar()
        ttk.Label(self.trim_t_frame, textvariable=self.time_per_frame_var, font=font_note, wraplength=200).grid(column=8, row=2, sticky="NW", padx=10)

        # File number start check option
        self.start_frame_check_var = BooleanVar(value=self.defaults["start_frame_check"]) # False by default
        self.start_frame_check = Checkbutton(self.trim_frame, text="Number files from trim start frame instead of from 1", variable=self.start_frame_check_var, font=font_italic, cursor="hand2")
        self.start_frame_check.grid(column=1, columnspan=3, row=3, sticky="W")

        # Operation label
        ttk.Label(main_frame, text="Operation", font=font_heading).grid(column=1, row=10, sticky="W")

        # Process file button
        self.process_button = ttk.Button(main_frame, text="Process file manually", command=self.process_manually, padding=(5, 2, 5, 2), cursor="hand2")
        self.process_button.grid(column=1, row=11, sticky="EW")

        self.process_label_var = StringVar(value=self.defaults["process_label"])
        self.process_label = ttk.Label(main_frame, textvariable=self.process_label_var, font=font_italic, justify="left", wraplength=500)
        self.process_label.grid(column=2, columnspan=3, row=11, sticky="WE")
        
        # FFmpeg command button
        self.cmd_button = ttk.Button(main_frame, text="Make command", command=self.make_command, padding=(5, 2, 5, 2), cursor="hand2")
        self.cmd_button.grid(column=1, row=11, sticky="EW")

        self.cmd_label_var = StringVar(value=self.defaults["cmd_label"])
        self.cmd_label = ttk.Label(main_frame, textvariable=self.cmd_label_var, font=font_italic, justify="left", wraplength=500)
        self.cmd_label.grid(column=2, columnspan=3, row=11, sticky="WE")

        ttk.Separator(main_frame, orient=HORIZONTAL).grid(column=1, columnspan=4, row=12, sticky="EW")

        # FFmpeg command box
        self.cmd_var = StringVar(value=self.defaults["cmd"])
        self.cmd = ttk.Label(main_frame, textvariable=self.cmd_var, font="TkFixedFont", justify="center", wraplength=742)
        self.cmd.grid(column=1, columnspan=4, row=13, sticky="NSEW")

        ttk.Separator(main_frame, orient=HORIZONTAL).grid(column=1, columnspan=4, row=14, sticky="EW")

        # Run FFmpeg tool button
        self.exe_button = ttk.Button(main_frame, text="Run FFmpeg", command=self.run_tool, padding=(5, 2, 5, 2))
        self.exe_button.grid(column=1, row=15, sticky="EW")
        self.exe_button.config(state="disabled", cursor="")

        # FFmpeg tool progress report
        self.progress_var = StringVar(value=self.defaults["progress"])
        op_label = ttk.Label(main_frame, textvariable=self.progress_var, font=font_italic, justify="left", wraplength=460, width=40)
        op_label.grid(column=2, columnspan=3, row=15, sticky="NSEW")

        # Copy FFmpeg command button
        self.copy_cmd_button = ttk.Button(main_frame, text="Copy command", command=self.copy_command, padding=(5, 2, 5, 2), cursor="hand2")
        self.copy_cmd_button.grid(column=4, row=15, sticky="E")

        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate")
        self.progress_bar.grid(column=1, columnspan=3, row=16, sticky="NESW")

        # View created files Button
        self.view_button = ttk.Button(main_frame, text="View files", command=self.view_folder, padding=(5, 2, 5, 2), cursor="hand2")
        self.view_button.grid(column=4, columnspan=2, row=16, sticky="EW")

        # Styling, resizing rules, padding, etc.
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0, minsize=50)
        main_frame.columnconfigure(2, weight=0, minsize=50)
        main_frame.columnconfigure(3, weight=0)
        main_frame.columnconfigure(4, weight=0)
        for child in main_frame.winfo_children(): 
            child.grid_configure(padx=3, pady=3)

        # Then center/resize AFTER layout is calculated
        root.update_idletasks()
        root.geometry(self.center_geometry())
        root.geometry("")

        # Hide currently unnecessary parts
        self.widget_vis()

        # Give first entry field focus, bind returns
        in_entry.focus()
        in_entry.bind("<Return>", lambda event: self.choose_input())
        out_entry.bind("<Return>", lambda event: self.choose_output())
        out_file_entry.bind("<Return>", lambda event: self.make_command())

    # Input button action
    def choose_input(self):
        try:
            # Prompt user for a video file
            sel_file = filedialog.askopenfilename(
                title="Select a file",
                initialdir=None,        # starting folder - to add later
                filetypes=[
                    ("Video files", "*.mp4 *.mkv *.mov *.avi *.webm *.flv *.wmv *.m4v *.mpg *.mpeg *.ts *.m2ts *.3gp *.ogv"),
                    ("MP4", "*.mp4"),
                    ("MKV", "*.mkv"),
                    ("All files", "*.*"),
                ],
            )       # Returns file path or empty string (need to return None if sending to separate function)
            
            current_input = str(self.in_var.get())

            if current_input != sel_file and sel_file != "":
                self.in_var.set(sel_file)
                self.process_file(sel_file)

            elif current_input == sel_file:
                self.reset_vars("progress", "cmd", "cmd_label")
                self.widget_vis(False, "progress_bar", "view_button", "copy_cmd_button")
                self.exe_button.config(state="disabled", cursor="")

            else:
                self.in_var.set("No file selected")
                self.reset_vars("progress", "cmd", "cmd_label", "meta")
                self.widget_vis()
                self.widget_vis(True, "process_button", "process_label")
                self.preview_image.configure(image=self.empty_img)
                self.exe_button.config(state="disabled", cursor="")
        except:
            self.in_var.set("Error selecting file")
            self.reset_vars("progress", "cmd", "cmd_label", "meta")
            self.widget_vis()
            self.widget_vis(True, "process_button", "process_label")
            self.preview_image.configure(image=self.empty_img)
            self.exe_button.config(state="disabled", cursor="")
    
    # Output button action
    def choose_output(self):
        try:
            # Prompt user for a video file
            sel_dir = filedialog.askdirectory(
                title="Select a folder",
                initialdir=None,        # starting folder
            )       # Returns folder path or empty string (need to return None if sending to separate function)
            current_output = str(self.out_var.get())
            if current_output != sel_dir and sel_dir != "":
                self.out_var.set(sel_dir)
                self.reset_vars("progress", "cmd", "cmd_label")
                self.widget_vis(False, "progress_bar", "view_button","copy_cmd_button")
            
            elif current_output == sel_dir:
                self.reset_vars("progress", "cmd", "cmd_label")
                self.widget_vis(False, "progress_bar", "view_button","copy_cmd_button")
                self.exe_button.config(state="disabled", cursor="")
            else:
                self.out_var.set("No folder selected")
                self.cmd_label_var.set("No folder selected")
                self.reset_vars("progress", "cmd")
                self.widget_vis(False, "progress_bar", "view_button","copy_cmd_button")
                self.exe_button.config(state="disabled", cursor="")
        except:
            self.out_var.set("Error selecting folder")
            self.reset_vars("progress", "cmd", "cmd_label")
            self.widget_vis(False, "progress_bar", "view_button","copy_cmd_button")
            self.exe_button.config(state="disabled", cursor="")
    
    # Process input file metadata and preview image
    def process_file(self, to_process, meta=True, preview=True):
        self.processing = to_process
        processing_path = Path(self.processing)
        
        video_extensions = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".wmv", ".m4v", ".mpg", ".mpeg", ".ts", ".m2ts", ".3gp", ".ogv"}
        # Check whether input is a video
        if not any(str(to_process).lower().endswith(ext) for ext in video_extensions):
            self.reset_vars("progress", "cmd_label")
            self.widget_vis(True, "process_button", "process_label")
            self.widget_vis(False, "progress_bar", "view_button", "cmd_button", "cmd_label", "options_frame", "copy_cmd_button")
            self.exe_button.config(state="disabled", cursor="")
            self.cmd_var.set("Error: Input file is not a video")
            return False

        self.widget_vis(True, "options_frame")
        self.reset_vars("trim_check", "trim_method", "start_frame_check")
        self.widget_vis(False, "trim_frame")

        if processing_path.is_absolute():
            self.in_folder = processing_path.parent
        else:
            self.in_folder = processing_path.relative_to(Path.cwd())
        
        stem = processing_path.stem
        
        #extension = processing_path.suffix # If needed?      
        
        try:
            # Metadata
            if meta == True:
                meta = self.get_metadata()
                stream = meta["streams"][0]
                self.in_width = stream["width"]
                self.in_height = stream["height"]
                frame_rate = stream["r_frame_rate"]
                self.duration = float(stream["duration"])
                
                # Convert metadata
                divisor = gcd(self.in_width, self.in_height)
                in_ratio = f"{int(self.in_width / divisor)}:{int(self.in_height / divisor)}"
                self.hours, remaining = divmod(self.duration, 3600)
                self.minutes, self.seconds = divmod(remaining, 60)
                in_len = f"{int(self.hours):02d}:{int(self.minutes):02d}:{int(self.seconds):02d}"
                split_rate = frame_rate.split("/", 1)
                self.in_fps = float(split_rate[0]) / float(split_rate[1])
                self.in_frames = int(self.duration * self.in_fps)
                self.time_per_frame = 1 / self.in_fps
                self.total_expected_frames = self.in_frames
                
                meta_txt = textwrap.dedent(f"""\
                    Dimensions:\t{self.in_width} x {self.in_height}
                    Aspect ratio:\t{in_ratio}
                    Duration:\t\t{in_len}
                    FPS:\t\t{round(self.in_fps, 3):g}
                    Frames:\t\t{self.in_frames}""")
                
                # Set fields
                self.widget_vis(True, "meta_head")
                self.meta_var.set(meta_txt)
            
            
            # Preview image
            if preview == True:
                # Make a preview image
                preview_path = self.generate_preview()

                # Set fields
                self.widget_vis(True, "preview_head")
                self.img = PhotoImage(file=preview_path)
                self.preview_image.configure(image=self.img)
            
            # Generate default file name
            if self.auto_file_var.get() == True:
                self.out_file_var.set(stem)
            
            # Generate default folder name
            if self.auto_folder_var.get() == True:
                # Split selected path to components
                out_folder = (str(self.in_folder) + "\\image-seq\\" + stem).replace("\\", "/")

                # Set fields
                self.out_var.set(out_folder)
            
            self.reset_vars("progress", "cmd_label", "cmd")
            self.widget_vis(False, "progress_bar", "view_button", "process_button", "process_label", "copy_cmd_button")
            self.widget_vis(True, "cmd_button", "cmd_label")
            self.exe_button.config(state="disabled", cursor="")
            
            # Store selected file as last processed
            self.last_processed = self.processing
        except:
            pass

    # Manually process file in input
    def process_manually(self):
        # Check whether input has been processed before, process metatdata & preview image if not (assuming folder is manual entry)
        current_input = str(self.in_var.get().strip())
        input_entry = Path(current_input).resolve()
        input_file = input_entry.as_posix()
        
        if not current_input or current_input in ("No file selected", "Input file path"):
            self.cmd_var.set("No file selected")
            self.widget_vis(True, "process_button", "process_label")
            self.widget_vis()
            self.reset_vars("progress","cmd_label")
            self.exe_button.config(state="disabled", cursor="")
            return False
        elif not Path(input_entry).is_file():
            self.cmd_var.set("Error: Input file doesn't exist")
            self.reset_vars("progress","cmd_label")
            self.widget_vis(True, "process_button", "process_label")
            self.widget_vis()
            self.exe_button.config(state="disabled", cursor="")
            return False
            
        else:
            # Check whether current file has been processed (or if options are hidden)
            if current_input != self.last_processed or not any(w.winfo_viewable() for w in self.options_frame.winfo_children()):
                process = self.process_file(current_input)
                if process == False:
                    return False
                else:
                    return True
            else:
                return None
    
    # Get info and make FFmpeg command
    def make_command(self):
        try:
            rel_note = "NOTE: Output folder given is not an absolute path so assumed it should be relative to input folder – please check path is correct"
            
            # Check whether input has been processed before, process metatdata & preview image if not (assuming folder is manual entry)
            current_input = str(self.in_var.get().strip())
            input_entry = Path(current_input).resolve()
            input_file = input_entry.as_posix()

            process = self.process_manually()
            if process == False:
                return
            else:
                if self.in_folder == "":
                    print("init in_folder error")
    
                # Get output
                current_output = self.out_var.get()
                output_entry = Path(current_output)                
                is_windows = os.name == "nt"
                
                # Checκ not empty
                if not current_output.strip() or current_output in ("No folder selected", "Output folder path"):
                    self.cmd_label_var.set("No folder selected")
                    self.reset_vars("progress", "cmd")
                    self.exe_button.config(state="disabled", cursor="")
                    return
                elif output_entry.is_absolute() or (is_windows and os.path.splitdrive(current_output)[0]):
                    self.output_folder = output_entry.resolve()
                    if process == True:
                        self.cmd_label_var.set("INPUT FILE CHANGED: double-check FFmpeg command is correct")
                    else:
                        self.cmd_label_var.set("READY: double-check FFmpeg command is correct")
                elif (is_windows == True and str(current_output).startswith("/") or str(current_output).startswith("\\")):
                    prepend = f".{current_output}"
                    self.output_folder = Path(str(self.in_folder) + prepend).resolve()
                    self.cmd_label_var.set(rel_note)
                elif not output_entry.is_relative_to(self.in_folder):
                    
                    prepend = f"/{current_output}"
                    combo = str(self.in_folder) + "/" + current_output
                    self.output_folder = Path(combo).resolve()
                    self.cmd_label_var.set(rel_note)
                
                
                self.ffmpeg_cmd = ["ffmpeg", "-i", input_file]
                filters = []
                ext = "." + self.fmt_var.get()
                fps = self.fps_var.get()
                scale = float(self.scale_var.get())
                self.num_digits = len(str(self.in_frames))
                start_number = "1"
                if self.pad_check_var.get():
                    padding = f"%0{self.num_digits}d"
                else:
                    padding = "%d"
                sep = self.sep_var.get()
                if sep == "Space":
                    sep = " "
                elif sep == "None":
                    sep = ""
                
                # Make output path
                self.file_txt = f"{self.out_file_var.get()}{sep}{padding}" + ext
                path_file = self.output_folder / self.file_txt
                self.resolve_path = path_file.resolve()
                output_file = Path(self.resolve_path).as_posix()
                
                # Check whether to trim frame range
                if self.trim_check_var.get(): 
                    if self.trim_method_var.get() == "Time":
                        # Gather input times
                        start_h = int(self.trim_start_h_var.get())
                        start_m = int(self.trim_start_m_var.get())
                        start_s = float(self.trim_start_s_var.get())
                        total_start = (start_h * 3600) + (start_m * 60) + start_s
                        end_h = int(self.trim_end_h_var.get())
                        end_m = int(self.trim_end_m_var.get())
                        end_s = float(self.trim_end_s_var.get())
                        total_end = (end_h * 3600) + (end_m * 60) + end_s
                        
                        if (total_start < 0 or total_start > self.duration) and (total_end < 0 or total_end > self.duration):
                            # Cancel making command
                            self.cmd_label_var.set("Error: Both trim times out of range; check and try again")
                            self.reset_vars("progress", "cmd")
                            self.widget_vis(False, "progress_bar", "view_button", "copy_cmd_button")
                            self.exe_button.config(state="disabled", cursor="")
                            return

                        elif total_start < 0 or total_start > self.duration:
                            # Reset to default value (on hold, prefer to cancel)
                            # total_start = 0
                            # self.cmd_label_var.set("Note: Trim start time out of range so changed to default; please check")
                            
                            self.cmd_label_var.set("Error: Start trim time out of range; check and try again")
                            self.reset_vars("progress", "cmd")
                            self.widget_vis(False, "progress_bar", "view_button", "copy_cmd_button")
                            self.exe_button.config(state="disabled", cursor="")
                            return

                        elif total_end < 0 or total_end > self.duration:
                            # Reset to default value (on hold, prefer to cancel)
                            # total_end = self.duration
                            # self.cmd_label_var.set("Note: Trim end time out of range so changed to default; please check")
                            
                            self.cmd_label_var.set("Error: End trim time out of range; check and try again")
                            self.reset_vars("progress", "cmd")
                            self.widget_vis(False, "progress_bar", "view_button", "copy_cmd_button")
                            self.exe_button.config(state="disabled", cursor="")
                            return
                        
                        # Flip reversed trim entries
                        if total_start > total_end:
                            total_start, total_end = total_end, total_start
                            self.cmd_label_var.set("Note: Trim start time higher than end; switched them around")
                        
                        # Adjust to save 1 frame if both trim entries are the same
                        if total_start == total_end:
                            if total_start == self.duration or round(total_start - self.time_per_frame, 5) >= 0:
                                total_start = round(total_start - self.time_per_frame, 5)
                            else:
                                total_end = round(total_end + self.time_per_frame, 5)
                            self.cmd_label_var.set("Note: Trim times both the same; adjusted them to get one frame")
                        # Adjust to save 1 frame if trim entries are too close to make a frame
                        elif total_end - total_start < round(self.time_per_frame, 5):
                            # Find the closest frames to the input values
                            closest_start = round(total_start / self.time_per_frame) * self.time_per_frame
                            closest_end = round(total_end / self.time_per_frame) * self.time_per_frame

                            # Change start/end times as needed to get 1 frame
                            if closest_start != closest_end:
                                total_start = round(closest_start, 5)
                                total_end = round(closest_end, 5)
                            elif round(closest_end + self.time_per_frame, 5) <= self.duration:
                                total_start = round(closest_start, 5)
                                total_end = round(closest_end + self.time_per_frame, 5)
                            else:
                                total_start = round(self.duration - self.time_per_frame, 5)
                                total_end = self.duration
                                
                            self.cmd_label_var.set("Note: Trim times too close; adjusted them to get one frame")
                        
                        # Ignore if set to full range
                        if not (total_start == 0 and total_end == self.duration):
                            # Add times to command
                            self.ffmpeg_cmd += ["-ss", str(total_start)]
                            self.ffmpeg_cmd += ["-to", str(total_end)]

                            start_number = str(round((total_start * self.in_fps)+ 1))
                            self.total_expected_frames = round((total_end - total_start) * self.in_fps)
                        
                    else:
                        # Get frames and validate
                        start_frame = int(self.trim_start_f_var.get()) - 1
                        end_frame = int(self.trim_end_f_var.get())
                        
                        # Check out of range
                        if (start_frame < 0 or start_frame > self.in_frames) and (end_frame < 0 or end_frame > self.in_frames):
                            # Cancel making command
                            self.cmd_label_var.set("Error: Both trim frames out of range; check and try again")
                            self.reset_vars("progress", "cmd")
                            self.widget_vis(False, "progress_bar", "view_button", "copy_cmd_button")
                            self.exe_button.config(state="disabled", cursor="")
                            return

                        elif start_frame < 0 or start_frame > self.in_frames:
                            # Reset to default value (on hold, prefer to cancel)
                            # start_frame = 0
                            # self.cmd_label_var.set("Note: Trim start out of range so changed to default; please check")
                            
                            self.cmd_label_var.set("Error: Start trim frame out of range; check and try again")
                            self.reset_vars("progress", "cmd")
                            self.widget_vis(False, "progress_bar", "view_button", "copy_cmd_button")
                            self.exe_button.config(state="disabled", cursor="")
                            return

                        elif end_frame < 0 or end_frame > self.in_frames:
                            # Reset to default value (on hold, prefer to cancel)
                            # end_frame = self.in_frames
                            # self.cmd_label_var.set("Note: Trim end frame out of range so changed to default; please check")
                            
                            self.cmd_label_var.set("Error: End trim frame out of range; check and try again")
                            self.reset_vars("progress", "cmd")
                            self.widget_vis(False, "progress_bar", "view_button", "copy_cmd_button")
                            self.exe_button.config(state="disabled", cursor="")
                            return
                        
                        # Flip reversed trim entries
                        if start_frame >= end_frame:
                            start_frame, end_frame = end_frame - 1, start_frame + 1
                            self.cmd_label_var.set("Note: Trim start frame higher than end; switched them around")
                        
                        # Ignore if set to full range
                        if not (start_frame == 0 and end_frame == self.in_frames):
                            # Append frame range to filters
                            filters.append(f"trim=start_frame={start_frame}:end_frame={end_frame}")
                            filters.append("setpts=PTS-STARTPTS")

                            start_number = str(start_frame + 1)
                            self.total_expected_frames = (end_frame - start_frame)
                
                if fps != "Auto":
                    filters.append(f"fps={fps}")
                    if float(fps) != round(self.in_fps, 3):
                        self.cmd_label_var.set("Note: FPS differs from source so output frame numbers will shift")

                if scale != 1.0:
                    new_width = int(self.in_width * scale)
                    new_height = int(self.in_height * scale)
                    filters.append(f"scale={str(new_width)}:{str(new_height)}")

                # Add filters to command
                if filters:
                    self.ffmpeg_cmd += ["-vf", ",".join(filters)]

                # Number files from original frame?
                if self.start_frame_check_var.get() and not start_number == "1":
                    self.ffmpeg_cmd += ["-start_number", start_number]
                
                # Add output path to command
                self.ffmpeg_cmd += [output_file]

                # Check for errors - TO DO (only checks input exists atm)                

                self.cmd_var.set(" ".join(self.ffmpeg_cmd))
                self.exe_button.config(state="normal", cursor="hand2")
                self.progress_var.set(f"Now run FFmpeg; expected output: {self.total_expected_frames} images")
                self.widget_vis(True, "copy_cmd_button")
        except:
            self.cmd_label_var.set("Error making command: check entries are valid")
            self.reset_vars("progress", "cmd")
            self.widget_vis(False, "progress_bar", "view_button","copy_cmd_button")
            self.exe_button.config(state="disabled", cursor="")
                
    def run_tool(self):
        # Check overwrite status
        if not self.overwrite_var.get():
            check = self.check_existing()

            if check in ("No folder", "No files"):
                pass # Folder doesn't exist, or there are no files in it: continue
            elif check == "Not dir":
                # Error
                self.progress_var.set("Error: Output path is not a folder; please check")
                return
            elif isinstance(check, (int, float)):
                if check != 0:
                    self.progress_var.set(f"Error: {str(check)}/{str(self.in_frames)} files exist but \"overwrite\" is off; click to view")
                    # Reveal the view folder button to look at output
                    self.widget_vis(True, "view_button")
                    self.widget_vis(False, "progress_bar")
                    return
                else:
                    pass # There are files but none match, continue
            else:
                self.progress_var.set("Error: unknown")
                return


        fps = self.fps_var.get()
        if fps == "Auto":
            fps = self.in_fps
        else:
            fps = float(fps)
        
        worker = Worker(self.ffmpeg_cmd, self.progress_var, self.progress_bar, self.output_folder, self.total_expected_frames)
        worker.start()  # Threaded so GUI won't freeze
        
        # Reveal the view folder button to look at output
        self.widget_vis(True, "view_button")

    # Get the monitor size and locate window in the centre
    def center_geometry(self):
        w = root.winfo_reqwidth()
        h = root.winfo_reqheight()+10
        x = (root.winfo_screenwidth() // 2) - (w // 2)
        y = (root.winfo_screenheight() // 2) - (h // 2)
        return f"{w}x{h}+{x}+{y}"
    
    # FFmpeg metadata query
    def get_metadata(self):
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", 
            "stream=width,height,r_frame_rate,duration",
            "-of", "json",
            self.processing
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            metadata = json.loads(result.stdout)
            
            return metadata
        except:
            return None
    
    # Generate a preview image using FFmpeg
    def generate_preview(self):
        cache_dir = Path(tempfile.gettempdir())
        
        make = cache_dir.mkdir(parents=True, exist_ok=True)
        
        preview_path = f"{cache_dir}\\afb-ffmpeg-gui-preview-image.png".replace("\\", "/")

        mid_frame = int(self.in_frames / 2)

        cmd = [
            "ffmpeg", 
            "-y", "-i", 
            self.processing, 
            "-vf", f"select='eq(n,{str(mid_frame)})',setpts=N/FRAME_RATE/TB, scale=200:100:force_original_aspect_ratio=decrease", 
            "-frames:v", "1", 
            preview_path
        ]
        
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return preview_path

        except subprocess.CalledProcessError as e:
            print("FFmpeg failed to make preview image:")
            print(e.stderr)
            return None

    # Check for existing files (only if overwrite is off)
    def check_existing(self):
        # Check whether intended path exists
        if not os.path.exists(self.output_folder):
            return "No folder"
        # Checκ whether it is a folder
        elif not os.path.isdir(self.output_folder):
            return "Not dir"
        else:
            # Check for files
            files = [f for f in os.listdir(self.output_folder) if os.path.isfile(os.path.join(self.output_folder, f))]
            if not files:
                return "No files"
            else:
                num = 0
                # Checκ whether exisiting files match intended creations
                for frame in range(1, self.in_frames + 1):
                    padded = f"{frame:0{self.num_digits}d}"

                    to_match = re.sub(r"%(\d+)d", str(padded), str(self.file_txt))
                    
                    if to_match in files:
                        num = num + 1
                    else:
                        continue

                return num
        
        # Run through each intended file name and check if it also exists
        # Return number of files / total that already exist
        # Cancel operation
    
    def view_folder(self):
        folder = self.output_folder
        if not folder:
            return  None # Handle empty path

        if os.name == "nt":  # Windows.
            subprocess.Popen(["explorer", str(folder)])
        elif sys.platform == "darwin":  # macOS.
            subprocess.Popen(["open", str(folder)])
        else:  # Linux/Unix.
            subprocess.Popen(["xdg-open", str(folder)])
    
    # Set variables back to defaults
    def reset_vars(self, *vars_to_reset):
        if not vars_to_reset:
            # Reset all to defaults.
            for var_name, default_value in self.defaults.items():
                getattr(self, f"{var_name}_var").set(default_value)
        else:
            # Reset only the specified vars; leave others unchanged.
            for var_name in vars_to_reset:
                if var_name in self.defaults:
                    getattr(self, f"{var_name}_var").set(self.defaults[var_name])
    
    # Hide unnecessary widgets
    def widget_vis(self, vis=False, *widgets):
        if vis == False:
            if not widgets:
                # Hide all
                for widget in self.hideable:
                    getattr(self, widget).grid_remove()
            else:
                # Hide only the specified widgets
                for widget in widgets:
                    getattr(self, widget).grid_remove()
            
        else:
            if not widgets:
                # Show all
                for widget in self.hideable:
                    getattr(self, widget).grid()
            else:
                # Show only the specified widgets
                for widget in widgets:
                    getattr(self, widget).grid()
    
    # One method to reset them all
    def reset_tool(self):
        self.reset_vars()
        self.widget_vis()
        self.widget_vis(True, "process_button", "process_label")
        self.preview_image.configure(image=self.empty_img)
        self.exe_button.config(state="disabled", cursor="")

    # Reveal or hide the trim options   
    def toggle_trim(self):
        if self.trim_check_var.get():
            # Force method to populate data
            self.toggle_method()
            # Show trim widgets
            self.widget_vis(True, "trim_frame")
        else:
            # Hide trim widgets
            self.reset_vars("trim_method", "start_frame_check")
            self.widget_vis(False, "trim_frame")

    def toggle_method(self):
        if self.trim_method_var.get() == "Frames":
            # Hide by time options frame & show by frames option
            self.widget_vis(False, "trim_t_frame")
            self.widget_vis(True, "trim_f_frame")

            # Configure boxes based on metadata
            self.start_f_spinbox.configure(to=self.in_frames)
            self.end_f_spinbox.configure(to=self.in_frames)

            # Set options based on metadata
            self.start_f_spinbox.set(value=1)
            self.end_f_spinbox.set(self.in_frames)

        elif self.trim_method_var.get() == "Time":
            # Hide by frames options frame & show by time options
            self.widget_vis(False, "trim_f_frame")
            self.widget_vis(True, "trim_t_frame")

            # Configure boxes based on metadata
            if self.hours > 0:
                self.start_h_spinbox.configure(to=self.hours)
                self.end_h_spinbox.configure(to=self.hours)
            elif self.minutes > 0:
                self.start_h_spinbox.configure(to=0)
                self.end_h_spinbox.configure(to=0)
                self.start_m_spinbox.configure(to=self.minutes)
                self.end_m_spinbox.configure(to=self.minutes)
            else:
                self.start_h_spinbox.configure(to=0)
                self.end_h_spinbox.configure(to=0)
                self.start_m_spinbox.configure(to=0)
                self.end_m_spinbox.configure(to=0)
                self.start_s_spinbox.configure(to=self.seconds)
                self.end_s_spinbox.configure(to=self.seconds)

            # Set options based on metadata
            self.start_h_spinbox.set(0)
            self.start_m_spinbox.set(0)
            self.start_s_spinbox.set(0)
            self.end_h_spinbox.set(int(self.hours))
            self.end_m_spinbox.set(int(self.minutes))
            self.end_s_spinbox.set(round(float(self.seconds), 2))
            self.time_per_frame_var.set(f"Seconds per frame ≈ {round(self.time_per_frame, 5)}")
        else:
            print("Error: Trim method uncertain")
    
    # Copy FFmpeg command to clipboard
    def copy_command(self):
        root.clipboard_clear()
        root.clipboard_append(self.cmd_var.get())



class Worker(Thread):
    def __init__(self, ffmpeg_cmd, progress_var, progress_bar, output_folder, frames):
        super().__init__()
        self.ffmpeg_cmd = ffmpeg_cmd  # FFmpeg command
        self.progress_var = progress_var  # Label variable
        self.progress_bar = progress_bar    # Progress bar
        self.output_folder = output_folder # Output folder
        self.frames = frames # Number of frames

        self.result = None  # Store result here
        self.error = None   # Store error report here

    # Run FFmpeg
    def run(self):
        # Execute your placeholder FFmpeg command here.
        self.progress_var.set("Starting conversion ...")

        try:
            
            # Check for errors - TO DO

            if str(self.ffmpeg_cmd).startswith("['ffmpeg'"):
                # Try to run
                try:
                    # Make missing folders
                    self.output_folder.mkdir(parents=True, exist_ok=True)

                    if not Path(self.output_folder).is_dir():
                        self.cmd_var.set("Error: Output folder doesn't exist")
                    else:
                        # Run FFmpeg
                        proc = subprocess.Popen(
                            self.ffmpeg_cmd, 
                            stderr=subprocess.PIPE, 
                            universal_newlines=True
                            )
                        
                        # Show progress bar
                        self.progress_bar["value"] = 0
                        self.progress_bar.grid()
                        
                        # Parse FFmpeg output for progress
                        total_frames = int(self.frames)  # Total expected frame number
                        for line in proc.stderr:
                            if "frame=" in line:
                                parts = line.split("frame=")[1].split()[0].strip().split("/")
                                current_frame = int(parts[0])
                                percent = round(((current_frame + 1) / total_frames) * 100, 3)
                                self.progress_var.set(f"Converting: {current_frame}/{total_frames} ({percent:.1f}%)")
                                self.progress_bar["value"] = percent

                        proc.wait()

                        if proc.returncode != 0:
                            raise subprocess.CalledProcessError(proc.returncode, self.ffmpeg_cmd)
                        
                        else:   
                            self.progress_bar["value"] = 100 # In case the last check was under 100%
                            self.progress_var.set(f"The FFmpeg tool ran successfully")
                
                except Exception as e:
                    self.result = 1
                    self.error = f"Failed: {str(e)}"
            else:
                self.progress_var.set("Error: No FFmpeg command to run")
        except:
            self.progress_var.set("Error: Tool failed")

root = Tk()
MainWindow(root)
root.mainloop()