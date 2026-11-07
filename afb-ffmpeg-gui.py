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

        root.title("AFB FFmpeg Video to Image Sequence GUI")

        # Create main window frame
        main_frame = ttk.Frame(root, padding=(10, 10, 10, 10))
        main_frame.grid(column=0, row=0, sticky="NSEW")

        # Input label
        ttk.Label(main_frame, text="Input file", font=font_heading).grid(column=1, row=1, sticky="W")

        # Input text entry field
        self.in_var = StringVar(value="Input file path")
        in_entry = ttk.Entry(main_frame, width=50, textvariable=self.in_var)
        in_entry.grid(column=1, columnspan=3, row=2, sticky="EW")

        # Input selector button
        in_button = ttk.Button(main_frame, text="File", command=self.choose_input, padding=(5, 2, 5, 2)).grid(column=4, row=2, sticky="W")

        # Output label
        ttk.Label(main_frame, text="Output folder", font=font_heading).grid(column=1, row=3, sticky="W")

        # Output text entry field
        self.out_var = StringVar(value="Output folder path")
        out_entry = ttk.Entry(main_frame, textvariable=self.out_var)
        out_entry.grid(column=1, columnspan=3, row=4, sticky="EW")

        # Output selector button
        out_button = ttk.Button(main_frame, text="Folder", command=self.choose_output, padding=(5, 2, 5, 2)).grid(column=4, row=4, sticky="W")

        # Output file name label
        ttk.Label(main_frame, text="Output file name", font=font_heading).grid(column=1, row=5, sticky="W")

        # Output text entry field
        self.out_file_var = StringVar(value="image")
        out_file_entry = ttk.Entry(main_frame, textvariable=self.out_file_var)
        out_file_entry.grid(column=1, columnspan=3, row=6, sticky="WE")

        # Note label
        ttk.Label(main_frame, text="Note: Frame number and extension will be added automatically", font=font_note).grid(column=1, columnspan=3, row=7, sticky="W")

        # Options label
        ttk.Label(main_frame, text="Options", font=font_heading).grid(column=1, row=8, sticky="W")

        # Format Label
        ttk.Label(main_frame, text="Image format", font=font_italic).grid(column=1, row=9, sticky="W")

        # Image format options
        fmt_list = ["png", "jpg", "exr", "webp", "tif", "bmp", "tga", "gif"] # Maybe add a custom option?
        self.fmt_var = StringVar(value="png")
        format_menu = ttk.Combobox(main_frame, width = 6, textvariable = self.fmt_var, values = fmt_list).grid(column=1, row=11, sticky="NW")
        self.fmt_var.set("png")
        
        # FPS Label
        ttk.Label(main_frame, text="FPS", font=font_italic).grid(column=2, row=9, sticky="W")
        
        # FPS options
        fps_list = ["Auto", "12", "15", "20", "23.976", "24", "25", "29.97", "30", "48", "50", "59.94", "60", "96", "119.88", "120"] # Maybe add a custom option?
        self.fps_var = StringVar()
        fps_menu = ttk.Combobox(main_frame, width = 6, values=fps_list, textvariable = self.fps_var).grid(column=2, row=11, sticky="NW")
        self.fps_var.set(value="Auto")
        
        # Operation label
        ttk.Label(main_frame, text="Operation", font=font_heading).grid(column=1, row=12, sticky="W")

        # FFmpeg command button
        cmd_button = ttk.Button(main_frame, text="Make FFmpeg command", command=self.make_command, padding=(5, 2, 5, 2)).grid(column=1, columnspan=2, row=13, sticky="EW")

        self.cmd_label_default = "Make FFmpeg command first"
        self.cmd_label_var = StringVar(value=self.cmd_label_default)
        cmd_label = ttk.Label(main_frame, textvariable=self.cmd_label_var, font=font_italic, justify="left", wraplength=460).grid(column=3, columnspan=2, row=13, sticky="WE")

        ttk.Separator(main_frame, orient=HORIZONTAL).grid(column=1, columnspan=4, row=14, sticky="EW")

        # FFmpeg command Label
        self.cmd_placeholder = "The FFmpeg command will show here."
        self.cmd_var = StringVar(value=self.cmd_placeholder)
        cmd_label = ttk.Label(main_frame, textvariable=self.cmd_var, font="TkFixedFont", justify="center", wraplength=680)
        cmd_label.grid(column=1, columnspan=4, row=15, sticky="NSEW")

        ttk.Separator(main_frame, orient=HORIZONTAL).grid(column=1, columnspan=4, row=16, sticky="EW")

        # Run FFmpeg tool button
        exe_button = ttk.Button(main_frame, text="Run FFmpeg", command=self.run_tool, padding=(5, 2, 5, 2)).grid(column=1, columnspan=2, row=17, sticky="EW")

        # FFmpeg tool progress report
        self.progress_var = StringVar(value="")
        op_label = ttk.Label(main_frame, textvariable=self.progress_var, font=font_italic, justify="left", wraplength=460)
        op_label.grid(column=3, columnspan=2, row=17, sticky="NSEW")

        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate")
        self.progress_bar.grid(column=1, columnspan=4, row=18, sticky="NESW")

        # Metadata from input video file
        self.meta_head = ttk.Label(main_frame, text="Metadata", font=font_bold, justify="left", width=28)
        self.meta_head.grid(column=3, row=8, sticky="NW")

        # Metadata Label
        self.meta_var = StringVar()
        meta_label_txt = ttk.Label(main_frame, textvariable=self.meta_var, justify="left")
        meta_label_txt.grid(column=3, row=9, rowspan=3, sticky="NW")

        # Preview image heading
        self.preview_head = ttk.Label(main_frame, text="Preview image", font=font_bold, justify="left")
        self.preview_head.grid(column=4, row=8, sticky="NW")
        
        # Empty preview image space
        self.empty_img = PhotoImage()
        self.preview_image = ttk.Label(main_frame, anchor="center")
        self.preview_image.grid(column=4, row=9, rowspan=3, sticky="NESW")

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
        self.meta_head.grid_remove()
        self.preview_head.grid_remove()
        self.progress_bar.grid_remove()

        # Give first entry field focus, bind returns
        in_entry.focus()
        in_entry.bind("<Return>", self.choose_input)
        out_entry.bind("<Return>", self.choose_output)
        out_file_entry.bind("<Return>", self.make_command)

    # Input button action
    def choose_input(self):
        try:
            # Prompt user for a video file
            self.sel_file = filedialog.askopenfilename(
                title="Select a file",
                initialdir=None,        # starting folder - to add later
                filetypes=[
                    ("Video files", "*.mp4 *.mkv *.mov *.avi *.webm *.flv *.wmv *.m4v *.mpg *.mpeg *.ts *.m2ts *.3gp *.ogv"),
                    ("MP4", "*.mp4"),
                    ("MKV", "*.mkv"),
                    ("All files", "*.*"),
                ],
            )       # Returns file path or empty string (need to return None if sending to separate function)
            current_text = str(self.in_var.get())
            if current_text != self.sel_file and self.sel_file != "":
                # Split selected path to components
                split_sel = self.sel_file.rsplit("/", 1)
                split_file = split_sel[1].rsplit(".", 1)
                self.in_folder = split_sel[0]
                out_folder = self.in_folder + "/image-seq/" + split_file[0]
                # file_type = split_file[1] # In case need to know later?
                file_name = split_file[0]

                # Get metadata
                meta = self.get_metadata()
                stream = meta["streams"][0]
                in_width = stream["width"]
                in_height = stream["height"]
                frame_rate = stream["r_frame_rate"]
                self.duration = float(stream["duration"])
                
                # Convert metadata
                divisor = gcd(in_width, in_height)
                in_ratio = f"{int(in_width / divisor)}:{int(in_height / divisor)}"
                hours, remaining = divmod(self.duration, 3600)
                minutes, seconds = divmod(remaining, 60)
                in_len = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
                split_rate = frame_rate.split("/", 1)
                self.in_fps = float(split_rate[0]) / float(split_rate[1])
                self.in_frames = int(self.duration * self.in_fps) + 1
                
                meta_txt = textwrap.dedent(f"""\
                    Dimensions:\t{in_width} x {in_height}
                    Aspect ratio:\t{in_ratio}
                    Duration:\t\t{in_len}
                    FPS:\t\t{round(self.in_fps, 3):g}
                    Frames:\t\t{self.in_frames}""")

                # Make a preview image
                preview_path = self.generate_preview()
                                
                # Set fields
                self.in_var.set(self.sel_file)
                self.out_var.set(out_folder)
                self.out_file_var.set(file_name)
                self.meta_head.grid()
                self.meta_var.set(meta_txt)
                self.preview_head.grid()
                self.img = PhotoImage(file=preview_path)
                self.preview_image.configure(image=self.img)
                self.progress_var.set("")
                self.cmd_label_var.set(self.cmd_label_default)
                self.cmd_var.set(self.cmd_placeholder)

            elif current_text == self.sel_file:
                self.progress_var.set("")
                self.cmd_label_var.set(self.cmd_label_default)
                self.cmd_var.set(self.cmd_placeholder)

            else:
                self.in_var.set("No file selected")
                self.meta_var.set("")
                self.meta_head.grid_remove()
                self.preview_head.grid_remove()
                self.progress_bar.grid_remove()
                self.preview_image.configure(image=self.empty_img)
                self.progress_var.set("")
                self.cmd_label_var.set(self.cmd_label_default)
                self.cmd_var.set(self.cmd_placeholder)
        except:
            self.in_var.set("Error selecting file")
    
    # Output button action
    def choose_output(self):
        try:
            # Prompt user for a video file
            sel_dir = filedialog.askdirectory(
                title="Select a folder",
                initialdir=None,        # starting folder
            )       # Returns folder path or empty string (need to return None if sending to separate function)
            current_text = str(self.in_var.get())
            if current_text != sel_dir and sel_dir != "":
                self.out_var.set(sel_dir)
                self.progress_var.set("")
                self.cmd_label_var.set(self.cmd_label_default)
                self.cmd_var.set(self.cmd_placeholder)
            
            elif current_text == sel_dir:
                self.progress_var.set("")
                self.cmd_label_var.set(self.cmd_label_default)
                self.cmd_var.set(self.cmd_placeholder)

            else:
                self.out_var.set("No folder selected")
                self.progress_var.set("")
                self.cmd_label_var.set(self.cmd_label_default)
                self.cmd_var.set(self.cmd_placeholder)
        except:
            self.out_var.set("Error selecting folder")
    
    # Get info and make FFmpeg command
    def make_command(self):
        try:
            rel_note = "NOTE: Output folder given is not an absolute path so assumed it should be relative to input folder – please check path is correct"

            # Get input
            input_entry = Path(self.in_var.get().strip()).resolve()
            input_file = Path(input_entry).as_posix()
            
            # Check input first
            if not Path(input_file).exists():
                self.cmd_var.set("Error: Input file doesn't exist")
                self.cmd_label_var.set(self.cmd_label_default)
            
            else:
                # Get output
                output_entry = self.out_var.get().strip()
                
                # Checκ not empty
                if not output_entry.strip() or output_entry in ("No folder selected", "Output folder path"):
                    self.cmd_label_var.set("No folder selected")
                    self.cmd_var.set(self.cmd_placeholder)
                    self.progress_var.set("")
                else:
                    output_entry = Path(output_entry)
                    # Check for text instead of path
                    is_windows = os.name == "nt"
                    if is_windows and str(output_entry).startswith("/") or str(output_entry).startswith("\\"):
                        prepend = f".{output_entry}"

                        self.output_folder = Path(self.in_folder + prepend).resolve()

                        self.cmd_label_var.set(rel_note)
                    else:
                        if Path(output_entry).is_absolute():
                            self.output_folder = Path(output_entry).resolve()

                            self.cmd_label_var.set("READY: double-check FFmpeg command is correct")
                        else:
                            self.output_folder = Path(self.in_folder / output_entry).resolve()
                            
                            self.cmd_label_var.set(rel_note)

                    file_name = self.out_file_var.get().strip()
                    ext = "." + self.fmt_var.get()
                    fps = self.fps_var.get()
                    num_digits = len(str(self.in_frames))
                    padding = f"%0{num_digits}d"

                    # Make output path
                    file_txt = f"{file_name}_{padding}"
                    path_file = self.output_folder / file_txt
                    resolve_path = path_file.with_suffix(ext).resolve()
                    output_file = Path(resolve_path).as_posix()
                    
                    
                    # Check for errors - TO DO (only checks input exists atm)

                    # Make command
                    
                    if fps == "Auto":
                        self.ffmpeg_cmd = [
                            "ffmpeg", 
                            "-y", 
                            "-i", input_file, 
                            output_file
                        ]
                        self.cmd_var.set(self.ffmpeg_cmd)
                        
                    else:
                        self.ffmpeg_cmd = [
                            "ffmpeg", 
                            "-y", 
                            "-i", input_file, 
                            "-vf", f"fps={fps}", 
                            output_file
                        ]
                        self.cmd_var.set(self.ffmpeg_cmd)
                        
                        if float(fps) != self.in_fps:
                            self.cmd_label_var.set("Note: Chosen FPS doesn't match input")

                    self.progress_var.set("Now run FFmpeg")
        except:
            self.cmd_label_var.set("Error making command")
            self.cmd_var.set(self.cmd_placeholder)
            self.progress_var.set("")
    
    def run_tool(self):
        fps = self.fps_var.get()
        if fps == "Auto":
            fps = self.in_fps
        else:
            fps = float(fps)
        worker = Worker(self.ffmpeg_cmd, self.progress_var, self.progress_bar, self.output_folder, self.duration, fps)
        worker.start()  # Threaded so GUI won't freeze

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
            self.sel_file
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
        
        cmd = [
            "ffmpeg", 
            "-y", "-i", 
            self.sel_file, 
            "-vf", "scale=200:100:force_original_aspect_ratio=decrease", 
            "-frames:v", "1", 
            preview_path
        ]
        
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return preview_path

        except subprocess.CalledProcessError as e:
            print("FFmpeg failed:")
            print(e.stderr)
            return None

class Worker(Thread):
    def __init__(self, ffmpeg_cmd, progress_var, progress_bar, output_folder, duration, fps):
        super().__init__()
        self.ffmpeg_cmd = ffmpeg_cmd  # FFmpeg command
        self.progress_var = progress_var  # Label variable
        self.progress_bar = progress_bar    # Progress bar
        self.output_folder = output_folder # Output folder
        self.frames = (duration * fps) + 1 # Number of frames

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

                    if not Path(self.output_folder).exists():
                        self.cmd_var.set("Error: Output folder doesn't exist")
                    else:
                        # Run FFmpeg
                        proc = subprocess.Popen(
                            self.ffmpeg_cmd, 
                            stderr=subprocess.PIPE, 
                            universal_newlines=True
                            )
                        
                        # Show progress bar
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
                        
                        self.progress_bar["value"] = 100 # In case the last check was under 100%
                        self.progress_var.set("The FFmpeg tool ran successfully")
                
                except Exception as e:
                    self.progress_var.set(f"Error: FFmpeg failed ({str(e)})")
            else:
                self.progress_var.set("Error: No FFmpeg command to run")
        except:
            self.progress_var.set("Error: Tool failed")
            pass

root = Tk()
MainWindow(root)
root.mainloop()