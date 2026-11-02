"""
    AFB FFmpeg GUI
    A simple interface made using Python & Tkinter to speed up FFmpeg video to image sequence conversions. 
    (Second draft adds basic functionality, no error checking)
"""
from pathlib import Path
import subprocess
from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import filedialog

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
        main_frame.grid(column=0, row=0, sticky=(N, W, E, S))

        # Input label
        ttk.Label(main_frame, text="Input file", font=font_heading).grid(column=1, row=1, sticky=W)

        # Input text entry field
        self.in_var = StringVar(value="Input file path")
        in_entry = ttk.Entry(main_frame, width=50, textvariable=self.in_var)
        in_entry.grid(column=1, columnspan=3, row=2, sticky=(W,E))

        # Input selector button
        in_button = ttk.Button(main_frame, text="File", command=self.choose_input, padding=(5, 2, 5, 2)).grid(column=4, row=2, sticky=W)

        # Output label
        ttk.Label(main_frame, text="Output folder", font=font_heading).grid(column=1, row=3, sticky=W)

        # Output text entry field
        self.out_var = StringVar(value="Output folder path")
        out_entry = ttk.Entry(main_frame, width=50, textvariable=self.out_var)
        out_entry.grid(column=1, columnspan=3, row=4, sticky=(W,E))

        # Output selector button
        out_button = ttk.Button(main_frame, text="Folder", command=self.choose_output, padding=(5, 2, 5, 2)).grid(column=4, row=4, sticky=W)

        # Output file name label
        ttk.Label(main_frame, text="Output file name", font=font_heading).grid(column=1, row=5, sticky=W)

        # Output text entry field
        self.out_file_var = StringVar(value="image")
        out_file_entry = ttk.Entry(main_frame, width=50, textvariable=self.out_file_var)
        out_file_entry.grid(column=1, columnspan=3, row=6, sticky=(W,E))

        # Note label
        ttk.Label(main_frame, text="Note: Frame number and extension will be added automatically", font=font_note).grid(column=1, columnspan=3, row=7, sticky="W")

        # Options label
        ttk.Label(main_frame, text="Options", font=font_heading).grid(column=1, row=8, sticky=W)

        # Format Label
        ttk.Label(main_frame, text="Image format", font=font_italic).grid(column=1, row=9, sticky=W)

        # Image format options
        fmt_list = ["png", "jpg", "exr", "webp", "tif", "bmp", "tga", "gif"] # Maybe add a custom option?
        self.format_var = StringVar(value="png")
        format_menu = ttk.Combobox(main_frame, width = 6, textvariable = self.format_var, values = fmt_list).grid(column=1, row=11, sticky=(W, N))
        self.format_var.set("png")
        
        # FPS Label
        ttk.Label(main_frame, text="FPS", font=font_italic).grid(column=2, row=9, sticky=W)
        
        # FPS options
        fps_list = ["Auto", "23.98", "24", "25", "29.97", "30", "59.94", "60", "120"] # Maybe add a custom option?
        self.fps_var = StringVar()
        fps_menu = ttk.Combobox(main_frame, width = 6, values=fps_list, textvariable = self.fps_var).grid(column=2, row=11, sticky=(W, N))
        self.fps_var.set(value="Auto")
        
        # Operation label
        ttk.Label(main_frame, text="Operation", font=font_heading).grid(column=1, row=12, sticky=W)

        # FFmpeg command button
        cmd_button = ttk.Button(main_frame, text="Make FFmpeg command", command=self.make_command, padding=(5, 2, 5, 2)).grid(column=1, columnspan=2, row=13, sticky="W, E")

        ttk.Label(main_frame, text="Make FFmpeg command first", font=font_italic).grid(column=3, row=13, sticky="W, E")

        ttk.Separator(main_frame, orient=HORIZONTAL).grid(column=1, columnspan=4, row=14, sticky="W, E")

        # FFmpeg command Label
        self.cmd_var = StringVar(value="The FFmpeg command will show here.")
        cmd_label = ttk.Label(main_frame, textvariable=self.cmd_var, font="TkFixedFont", justify="center", wraplength=500)
        cmd_label.grid(column=1, columnspan=4, row=15, sticky=(W,E,N,S))

        ttk.Separator(main_frame, orient=HORIZONTAL).grid(column=1, columnspan=4, row=16, sticky="W, E")

        # Run FFmpeg tool button
        exe_button = ttk.Button(main_frame, text="Run FFmpeg", command=self.run_tool, padding=(5, 2, 5, 2)).grid(column=1, columnspan=2, row=17, sticky="W, E")

        # FFmpeg tool operation report
        self.op_var = StringVar(value="")
        op_label = ttk.Label(main_frame, textvariable=self.op_var, font=font_italic, justify="left", wraplength=450)
        op_label.grid(column=3, columnspan=2, row=17, sticky="W, E, N, S")

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

        # Give first entry field focus
        in_entry.focus()
        root.bind("<Return>", self.choose_input)

    # Input button action
    def choose_input(self, *args):
        try:
            # Prompt user for a video file
            select = filedialog.askopenfilename(
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
            if current_text != select and select != "":
                # Split selected path to components
                split_sel = select.rsplit("/", 1)
                split_file = split_sel[1].rsplit(".", 1)
                folder = split_sel[0] + "/image-seq/" + split_file[0]
                # file_type = split_file[1]
                file_name = split_file[0]
                
                # Set fields
                self.in_var.set(select)
                self.out_var.set(folder)
                self.out_file_var.set(file_name)
            else:
                self.in_var.set("No file selected")
        except:
            pass
    
    # Output button action
    def choose_output(self, *args):
        try:
            # Prompt user for a video file
            select = filedialog.askdirectory(
                title="Select a folder",
                initialdir=None,        # starting folder
            )       # Returns folder path or empty string (need to return None if sending to separate function)
            current_text = str(self.in_var.get())
            if current_text != select and select != "":
                self.out_var.set(select)
            else:
                self.out_var.set("No folder selected")
        except:
            pass
    
    # Get info and make FFmpeg command
    def make_command(self, *args):
        try:
            # Gather variables
            input_file = self.in_var.get().strip()
            output_folder = self.out_var.get().strip()
            output_file = self.out_file_var.get().strip()
            ext = self.format_var.get()
            fps = self.fps_var.get()
            
            # Check for errors - TO DO (only checks input exists atm)

            if not Path(input_file).exists():
                self.cmd_var.set("Error: Input file doesn't exist")
            else:
                # Make command
                if fps == "Auto":
                    self.cmd_var.set("ffmpeg -i {0} {1}/{2}_%04d.{3}".format(input_file, output_folder, output_file, ext))
                else:
                    self.cmd_var.set("ffmpeg -i {0} -vf fps={1} {2}/{3}_%04d.{4}".format(input_file, fps, output_folder, output_file, ext))
        except:
            pass
    
    # Run FFmpeg
    def run_tool(self, *args):
        try:
            cmd = self.cmd_var.get()
            output_folder = Path(self.out_var.get())
            # Check for errors - TO DOTBOX

            if cmd.startswith("ffmpeg"):
                # Try to run
                try:
                    # Make missing folders
                    output_folder.mkdir(parents=True, exist_ok=True)
                    
                    # Run FFmpeg
                    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    self.op_var.set("The FFmpeg tool ran successfully")
                except:
                    self.op_var.set("Error: FFmpeg failed")
            else:
                self.op_var.set("Error: No FFmpeg command to run")
        except:
            self.op_var.set("Error: Tool failed")
            pass

    def center_geometry(self):
        w = root.winfo_reqwidth()
        h = root.winfo_reqheight()+10
        x = (root.winfo_screenwidth() // 2) - (w // 2)
        y = (root.winfo_screenheight() // 2) - (h // 2)
        return f"{w}x{h}+{x}+{y}"

root = Tk()
MainWindow(root)
root.mainloop()