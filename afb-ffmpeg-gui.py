"""
    AFB FFmpeg GUI
    A simple interface made using Python & Tkinter to speed up FFmpeg video to image sequence conversions. 
    (First draft just basic structure, no functionality, no error checking)
"""

from tkinter import *
from tkinter import ttk
from tkinter import font

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

        # Image format radiobutton
        self.format_var = StringVar()
        format1 = ttk.Radiobutton(main_frame, text='png', variable=self.format_var, value='png').grid(column=1, row=10, sticky=(W, N))
        format2 = ttk.Radiobutton(main_frame, text='jpg', variable=self.format_var, value='jpg').grid(column=1, row=11, sticky=(W, N))
        self.format_var.set("png")
        
        # FPS Label
        ttk.Label(main_frame, text="FPS", font=font_italic).grid(column=2, row=9, sticky=W)
        
        # FPS radiobutton
        self.fps_var = StringVar()
        fps1 = ttk.Radiobutton(main_frame, text='24', variable=self.fps_var, value=24).grid(column=2, row=10, sticky=(W, N))
        fps2 = ttk.Radiobutton(main_frame, text='29.976', variable=self.fps_var, value=29.976).grid(column=2, row=11, sticky=(W, N))
        self.fps_var.set("24")
        
        # FFmpeg command button
        cmd_button = ttk.Button(main_frame, text="Make FFmpeg command", command=self.make_command, padding=(5, 2, 5, 2)).grid(column=1, columnspan=2, row=12, sticky="W, E")

        ttk.Label(main_frame, text="Make FFmpeg command first", font=font_italic).grid(column=3, row=12, sticky="W, E")

        ttk.Separator(main_frame, orient=HORIZONTAL).grid(column=1, columnspan=4, row=13, sticky="W, E")

        # FFmpeg command Label
        self.cmd_var = StringVar(value="The FFmpeg command will show here.")
        cmd_label = ttk.Label(main_frame, textvariable=self.cmd_var, font="TkFixedFont", justify="center", wraplength=500)
        cmd_label.grid(column=1, columnspan=4, row=14, sticky=(W,E,N,S))

        ttk.Separator(main_frame, orient=HORIZONTAL).grid(column=1, columnspan=4, row=15, sticky="W, E")

        # Run FFmpeg tool button
        exe_button = ttk.Button(main_frame, text="Run FFmpeg", command=self.run_tool, padding=(5, 2, 5, 2)).grid(column=1, columnspan=2, row=16, sticky="W, E")

        # FFmpeg tool operation report
        self.op_var = StringVar(value="")
        op_label = ttk.Label(main_frame, textvariable=self.op_var, font=font_italic, justify="left", wraplength=450)
        op_label.grid(column=3, columnspan=2, row=16, sticky="W, E, N, S")

        # Styling, resizing rules, padding, etc.
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0, minsize=50)
        main_frame.columnconfigure(2, weight=0, minsize=50)
        main_frame.columnconfigure(3, weight=1)
        main_frame.columnconfigure(4, weight=1)
        for child in main_frame.winfo_children(): 
            child.grid_configure(padx=3, pady=3)

        # Give first entry field focus
        in_entry.focus()
        root.bind("<Return>", self.choose_input)

    # Input button action
    def choose_input(self, *args):
        try:
            orig_in = "Input file path"
            orig_out = "Output folder path"
            file = str(self.in_var.get())
            if file == orig_in:
                self.in_var.set(orig_out)
            else:
                self.in_var.set(orig_in)
        except:
            pass
    
    # Output button action
    def choose_output(self, *args):
        try:
            orig_in = "Input file path"
            orig_out = "Output folder path"
            folder = str(self.out_var.get())
            if folder == orig_out:
                self.out_var.set(orig_in)
            else:
                self.out_var.set(orig_out)
        except:
            pass
    
    # Get info and make FFmpeg command
    def make_command(self, *args):
        try:
            # Gather variables
            input_file = self.in_var.get().replace(' ', '/')
            output_folder = self.out_var.get().replace(' ', '/')
            output_file = self.out_file_var.get().replace(' ', '_')
            ext = self.format_var.get()
            fps = self.fps_var.get()

            # Make command
            self.cmd_var.set("ffmpeg -i {0} -vf fps={1} {2}/{3}_%04d.{4}".format(input_file, fps, output_folder, output_file, ext))
        except:
            pass
    
    # Run FFmpeg
    def run_tool(self, *args):
        try:
            # Check for errors
            if self.cmd_var.get().startswith("ffmpeg"):
                # Run FFmpeg
                self.op_var.set("The FFmpeg tool was run.")
            else:
                self.op_var.set("Error: no FFmpeg command to run.")
        except:
            pass


root = Tk()
MainWindow(root)
root.mainloop()