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
        "fmt" : "png",
        "fps" : "Auto",
        "scale" : 1.00, 
        "overwrite" : True,
        "cmd_label" : "Make FFmpeg command first",
        "cmd" : "The FFmpeg command will show here",
        "progress" : "",
        "meta" : ""
        }
        self.hideable = ["meta_head", "preview_head", "progress_bar", "view_button"]
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
        in_button = ttk.Button(main_frame, text="File", command=self.choose_input, padding=(5, 2, 5, 2))
        in_button.grid(column=4, row=2, sticky="W")

        # Auto output folder name option
        self.auto_folder_var = BooleanVar(value=self.defaults["auto_folder"])
        self.folder_check = ttk.Checkbutton(main_frame, text="Auto folder name", variable=self.auto_folder_var, onvalue=True, offvalue=False)
        self.folder_check.grid(column=3, row=3, sticky="NW")

        # Auto output file name option
        self.auto_file_var = BooleanVar(value=self.defaults["auto_file"])
        self.file_check = ttk.Checkbutton(main_frame, text="Auto file name", variable=self.auto_file_var, onvalue=True, offvalue=False)
        self.file_check.grid(column=4, row=3, sticky="NW")

        # Output label
        ttk.Label(main_frame, text="Output folder", font=font_heading).grid(column=1, row=3, sticky="W")

        # Output text entry field
        self.out_var = StringVar(value=self.defaults["out"])
        out_entry = ttk.Entry(main_frame, textvariable=self.out_var)
        out_entry.grid(column=1, columnspan=3, row=4, sticky="EW")

        # Output selector button
        out_button = ttk.Button(main_frame, text="Folder", command=self.choose_output, padding=(5, 2, 5, 2))
        out_button.grid(column=4, row=4, sticky="W")
        
        # Output file name label
        ttk.Label(main_frame, text="Output file name", font=font_heading).grid(column=1, row=5, sticky="W")

        # Output text entry field
        self.out_file_var = StringVar(value=self.defaults["out_file"])
        out_file_entry = ttk.Entry(main_frame, textvariable=self.out_file_var)
        out_file_entry.grid(column=1, columnspan=3, row=6, sticky="WE")

        # Note label
        ttk.Label(main_frame, text="Note: Frame number and extension will be added automatically", font=font_note).grid(column=1, columnspan=3, row=7, sticky="W")

        # Reset the whole tool button
        reset_button = ttk.Button(main_frame, text="Reset tool", command=self.reset_tool, padding=(5, 2, 5, 2))
        reset_button.grid(column=4, row=6, sticky="W")

        # Overwrite Option
        self.overwrite_var = BooleanVar(value=self.defaults["overwrite"])
        self.overwrite_check = ttk.Checkbutton(main_frame, text="Overwrite files", variable=self.overwrite_var, onvalue=True, offvalue=False)
        self.overwrite_check.grid(column=4, row=7, sticky="NW")
        
        # Options label
        ttk.Label(main_frame, text="Options", font=font_heading).grid(column=1, row=8, sticky="W")

        # Format Label
        ttk.Label(main_frame, text="Image format", font=font_italic).grid(column=1, row=9, sticky="W")

        # Image format options
        fmt_list = ["png", "jpg", "exr", "webp", "tif", "bmp", "tga"] # Maybe add a custom option?
        self.fmt_var = StringVar(value=self.defaults["fmt"])
        format_menu = ttk.Combobox(main_frame, width = 6, textvariable = self.fmt_var, values = fmt_list)
        format_menu.grid(column=2, row=9, sticky="NW")
        
        # FPS
        ttk.Label(main_frame, text="FPS", font=font_italic).grid(column=1, row=10, sticky="W")
        
        # FPS options
        fps_list = ["Auto", "12", "15", "20", "23.976", "24", "25", "29.97", "30", "48", "50", "59.94", "60", "96", "119.88", "120"] # Maybe add a custom option?
        self.fps_var = StringVar(value=self.defaults["fps"])
        fps_menu = ttk.Combobox(main_frame, width = 6, values=fps_list, textvariable = self.fps_var)
        fps_menu.grid(column=2, row=10, sticky="NW")
        
        # Scale Label
        ttk.Label(main_frame, text="Scale", font=font_italic).grid(column=1, row=11, sticky="W")
        
        # Scaling options
        scale_list = [0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0] # Maybe add a custom option?
        self.scale_var = StringVar(value=self.defaults["scale"])
        scale_menu = ttk.Combobox(main_frame, width = 6, values=scale_list, textvariable = self.scale_var)
        scale_menu.grid(column=2, row=11, sticky="NW")

        # Metadata from input video file
        self.meta_head = ttk.Label(main_frame, text="Input metadata", font=font_bold, justify="left", width=28)
        self.meta_head.grid(column=3, row=8, sticky="NW")

        # Metadata Label
        self.meta_var = StringVar(value=self.defaults["meta"])
        meta_label_txt = ttk.Label(main_frame, textvariable=self.meta_var, justify="left")
        meta_label_txt.grid(column=3, row=9, rowspan=3, sticky="NW")

        # Preview image heading
        self.preview_head = ttk.Label(main_frame, text="Preview image", font=font_bold, justify="left")
        self.preview_head.grid(column=4, row=8, sticky="NW")
        
        # Empty preview image space
        self.empty_img = PhotoImage()
        self.preview_image = ttk.Label(main_frame, anchor="center")
        self.preview_image.grid(column=4, row=9, rowspan=3, sticky="NESW")

        # Operation label
        ttk.Label(main_frame, text="Operation", font=font_heading).grid(column=1, row=12, sticky="W")

        # FFmpeg command button
        cmd_button = ttk.Button(main_frame, text="Make FFmpeg command", command=self.make_command, padding=(5, 2, 5, 2))
        cmd_button.grid(column=1, columnspan=2, row=13, sticky="EW")

        self.cmd_label_var = StringVar(value=self.defaults["cmd_label"])
        cmd_label = ttk.Label(main_frame, textvariable=self.cmd_label_var, font=font_italic, justify="left", wraplength=460)
        cmd_label.grid(column=3, columnspan=2, row=13, sticky="WE")

        ttk.Separator(main_frame, orient=HORIZONTAL).grid(column=1, columnspan=4, row=14, sticky="EW")

        # FFmpeg command box
        self.cmd_var = StringVar(value=self.defaults["cmd"])
        cmd_label = ttk.Label(main_frame, textvariable=self.cmd_var, font="TkFixedFont", justify="center", wraplength=680)
        cmd_label.grid(column=1, columnspan=4, row=15, sticky="NSEW")

        ttk.Separator(main_frame, orient=HORIZONTAL).grid(column=1, columnspan=4, row=16, sticky="EW")

        # Run FFmpeg tool button
        self.exe_button = ttk.Button(main_frame, text="Run FFmpeg", command=self.run_tool, padding=(5, 2, 5, 2))
        self.exe_button.grid(column=1, columnspan=2, row=17, sticky="EW")
        self.exe_button.config(state="disabled")

        # FFmpeg tool progress report
        self.progress_var = StringVar(value=self.defaults["progress"])
        op_label = ttk.Label(main_frame, textvariable=self.progress_var, font=font_italic, justify="left", wraplength=460)
        op_label.grid(column=3, columnspan=2, row=17, sticky="NSEW")

        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate")
        self.progress_bar.grid(column=1, columnspan=3, row=18, sticky="NESW")

        # View created files Button
        self.view_button = ttk.Button(main_frame, text="View files", command=self.view_folder, padding=(5, 2, 5, 2))
        self.view_button.grid(column=4, columnspan=2, row=18, sticky="EW")

        # Styling, resizing rules, padding, etc.
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0, minsize=50)
        main_frame.columnconfigure(2, weight=0, minsize=50)
        main_frame.columnconfigure(3, weight=1)
        main_frame.columnconfigure(4, weight=1)
        for child in main_frame.winfo_children(): 
            child.grid_configure(padx=3, pady=3)

        # Then center/resize AFTER layout is calculated
        root.update_idletasks()
        root.geometry(self.center_geometry())
        root.geometry("")

        # Hide currently unnecessary parts
        self.hide_widget()

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
                
                self.hide_widget("progress_bar", "view_button")
                
                self.exe_button.config(state="disabled")

            else:
                self.in_var.set("No file selected")
                self.reset_vars("progress", "cmd", "cmd_label", "meta")
                self.hide_widget()
                self.preview_image.configure(image=self.empty_img)
                self.exe_button.config(state="disabled")
        except:
            self.in_var.set("Error selecting file")
            self.reset_vars("progress", "cmd", "cmd_label", "meta")
            self.hide_widget()
            self.preview_image.configure(image=self.empty_img)
            self.exe_button.config(state="disabled")
    
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
            
            elif current_output == sel_dir:
                self.reset_vars("progress", "cmd", "cmd_label")
                self.exe_button.config(state="disabled")
            else:
                self.out_var.set("No folder selected")
                self.reset_vars("progress", "cmd", "cmd_label")
                self.exe_button.config(state="disabled")
        except:
            self.out_var.set("Error selecting folder")
            self.reset_vars("progress", "cmd", "cmd_label")
            self.exe_button.config(state="disabled")
    
    # Process input file metadata and preview image
    def process_file(self, to_process,meta=True, preview=True):
        self.processing = to_process
        processing_path = Path(self.processing)
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
                hours, remaining = divmod(self.duration, 3600)
                minutes, seconds = divmod(remaining, 60)
                in_len = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
                split_rate = frame_rate.split("/", 1)
                self.in_fps = float(split_rate[0]) / float(split_rate[1])
                self.in_frames = int(self.duration * self.in_fps)
                
                meta_txt = textwrap.dedent(f"""\
                    Dimensions:\t{self.in_width} x {self.in_height}
                    Aspect ratio:\t{in_ratio}
                    Duration:\t\t{in_len}
                    FPS:\t\t{round(self.in_fps, 3):g}
                    Frames:\t\t{self.in_frames}""")
                
                # Set fields
                self.meta_head.grid()
                self.meta_var.set(meta_txt)
            
            
            # Preview image
            if preview == True:
                # Make a preview image
                preview_path = self.generate_preview()

                # Set fields
                self.preview_head.grid()
                self.img = PhotoImage(file=preview_path)
                self.preview_image.configure(image=self.img)
            
            # Generate default file name
            if auto_file_var.get() == True:
                self.out_file_var.set(stem)
            
            # Generate default folder name
            if auto_folder_var.get() == True:
                # Split selected path to components
                out_folder = (str(self.in_folder) + "\\image-seq\\" + stem).replace("\\", "/")

                # Set fields
                self.out_var.set(out_folder)
            
            self.progress_var.set(self.defaults["progress"])
            self.cmd_label_var.set(self.defaults["cmd_label"])
            self.cmd_var.set(self.defaults["cmd"])
            self.progress_bar.grid_remove()
            self.view_button.grid_remove()
            self.exe_button.config(state="disabled")
            
            # Store selected file as last processed
            self.last_processed = self.processing
        except:
            pass

    # Get info and make FFmpeg command
    def make_command(self):
        try:
            rel_note = "NOTE: Output folder given is not an absolute path so assumed it should be relative to input folder – please check path is correct"

            # Check whether input has been processed before, process metatdata & preview image if not (assuming folder is manual entry)
            current_input = str(self.in_var.get().strip())
            input_entry = Path(current_input).resolve()
            input_file = input_entry.as_posix()

            if not current_input or current_input in ("No file selected", "Input file path"):
                self.cmd_var.set("No file selected")
                return
            elif not Path(input_entry).is_file():
                self.cmd_var.set("Error: Input file doesn't exist")
                self.reset_vars("progress","cmd_label")
                self.exe_button.config(state="disabled")
                return
                
            else:
                
                if current_input != self.last_processed:
                    self.process_file(current_input)

                if self.in_folder == "":
                    print("init in_folder error")

                # Get output
                current_output = self.out_var.get()
                output_entry = Path(current_output)                
                is_windows = os.name == "nt"
                
                # Checκ not empty
                if not current_output.strip() or current_output in ("No folder selected", "Output folder path"):
                    self.cmd_var.set("No folder selected")
                    self.reset_vars("progress", "cmd_label")
                    self.exe_button.config(state="disabled")
                    return
                elif output_entry.is_absolute() or (is_windows and os.path.splitdrive(current_output)[0]):
                    self.output_folder = output_entry.resolve()
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
                
                
                ext = "." + self.fmt_var.get()
                fps = self.fps_var.get()
                self.num_digits = len(str(self.in_frames))
                padding = f"%0{self.num_digits}d"
                
                # Make output path
                self.file_txt = f"{self.out_file_var.get()}_{padding}" + ext
                path_file = self.output_folder / self.file_txt
                self.resolve_path = path_file.resolve()
                output_file = Path(self.resolve_path).as_posix()
                
                scale_entry = ""
                scale = float(self.scale_var.get())
                
                if scale != 1.0:
                    new_width = int(self.in_width * scale)
                    new_height = int(self.in_height * scale)
                    scale_entry = f"scale={str(new_width)}:{str(new_height)},"

                # Check for errors - TO DO (only checks input exists atm)

                # Make command
                if fps == "Auto":
                    if scale != 1.0:
                        self.ffmpeg_cmd = [
                            "ffmpeg", 
                            "-i", input_file, 
                            "-vf", f"{scale_entry}",
                            output_file
                        ]
                    else:
                        self.ffmpeg_cmd = [
                            "ffmpeg", 
                            "-i", input_file, 
                            output_file
                        ]
                    self.cmd_var.set(self.ffmpeg_cmd)
                    
                else:
                    self.ffmpeg_cmd = [
                        "ffmpeg", 
                        "-i", input_file, 
                        "-vf", f"{scale_entry}fps={fps},setpts=N/FRAME_RATE/TB",
                        output_file
                    ]
                    self.cmd_var.set(self.ffmpeg_cmd)
                    
                    if float(fps) != self.in_fps:
                        self.cmd_label_var.set("Note: Chosen FPS doesn't match input")
                
                self.exe_button.config(state="normal")
                self.progress_var.set("Now run FFmpeg")
        except:
            self.cmd_label_var.set("Error making command")
            self.reset_vars("progress", "cmd")
    
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
                    self.view_button.grid()
                    self.hide_widget("progress_bar")
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
        
        worker = Worker(self.ffmpeg_cmd, self.progress_var, self.progress_bar, self.output_folder, self.duration, fps)
        worker.start()  # Threaded so GUI won't freeze
        
        # Reveal the view folder button to look at output
        self.view_button.grid()

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
    def hide_widget(self, *to_hide):
        if not to_hide:
            # Reset all to defaults.
            for widget in self.hideable:
                getattr(self, widget).grid_remove()
                
        else:
            # Reset only the specified vars; leave others unchanged.
            for widget in to_hide:
                getattr(self, widget).grid_remove()
    
    # One method to reset them all
    def reset_tool(self):
        self.reset_vars()
        self.hide_widget()
        self.preview_image.configure(image=self.empty_img)
        self.exe_button.config(state="disabled")


class Worker(Thread):
    def __init__(self, ffmpeg_cmd, progress_var, progress_bar, output_folder, duration, fps):
        super().__init__()
        self.ffmpeg_cmd = ffmpeg_cmd  # FFmpeg command
        self.progress_var = progress_var  # Label variable
        self.progress_bar = progress_bar    # Progress bar
        self.output_folder = output_folder # Output folder
        self.frames = (duration * fps) + 1 # Number of frames

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
                                percent = (current_frame / total_frames) * 100
                                self.progress_var.set(f"Converting: {current_frame}/{total_frames} ({percent:.1f}%)")
                                self.progress_bar["value"] = percent

                        proc.wait()

                        if proc.returncode != 0:
                            raise subprocess.CalledProcessError(proc.returncode, self.ffmpeg_cmd)
                        
                        else:   
                            self.progress_bar["value"] = 100 # In case the last check was under 100%
                            self.progress_var.set("The FFmpeg tool ran successfully")
                
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