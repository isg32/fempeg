import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText  # For scrollable log text
from PIL import Image, ImageTk  # For image support
import ffmpeg
from tinytag import TinyTag
from mutagen.flac import FLAC  # For extracting artwork from FLAC files

# Default path to ffmpeg.exe
FFMPEG_PATH = "./bin/ffmpeg.exe"
os.environ['PATH'] += os.pathsep + os.path.dirname(FFMPEG_PATH)

# Color scheme
BG_COLOR = "#f0f0f0"
BUTTON_COLOR = "#4CAF50"
TEXT_COLOR = "#333333"
ENTRY_COLOR = "#ffffff"

# Placeholder image path (use a default image if no artwork is found)
PLACEHOLDER_IMAGE = "placeholder.jpg"

def set_ffmpeg_path():
    global FFMPEG_PATH
    file_path = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe")])
    if file_path:
        FFMPEG_PATH = file_path
        os.environ['PATH'] += os.pathsep + os.path.dirname(FFMPEG_PATH)
        ffmpeg_path_var.set(FFMPEG_PATH)

def get_audio_bitrate(input_file):
    try:
        bratefile = TinyTag.get(input_file)
        return str(round(bratefile.bitrate * 1000))
    except Exception as e:
        messagebox.showerror("Error", f"Could not retrieve bitrate: {str(e)}")
        return "320000"

def convert_to_mp3():
    input_file = input_var.get()
    if not input_file:
        messagebox.showerror("Error", "Please select a FLAC file.")
        return
    try:
        bitrate = get_audio_bitrate(input_file)
        output_file = os.path.splitext(input_file)[0] + ".m4a"
        output_var.set(output_file)
        log_text.insert(tk.END, f"Converting: {input_file} -> {output_file} at {bitrate} bps\n")
        root.update()

        # Start progress bar
        progress_bar.start()

        (
            ffmpeg
            .input(input_file)
            .output(output_file, acodec="alac", map="0:a", f="mp4", ab=bitrate, map_metadata=0, vf="scale=300:-1")
            .run(overwrite_output=True)
        )

        log_text.insert(tk.END, "Conversion completed successfully!\n")
        messagebox.showinfo("Success", f"Conversion completed: {output_file}")
    except Exception as e:
        log_text.insert(tk.END, f"Error: {str(e)}\n")
        messagebox.showerror("Error", f"Conversion failed: {str(e)}")
    finally:
        # Stop progress bar
        progress_bar.stop()

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("FLAC files", "*.flac")])
    if file_path:
        input_var.set(file_path)
        display_artwork(file_path)

def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        flac_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".flac")]
        if flac_files:
            for file in flac_files:
                input_var.set(file)
                convert_to_mp3()
        else:
            messagebox.showerror("Error", "No FLAC files found in the selected folder.")

def display_artwork(file_path):
    try:
        # Extract artwork from FLAC file
        flac = FLAC(file_path)
        if flac.pictures:
            artwork_data = flac.pictures[0].data
            with open("temp_artwork.jpg", "wb") as img_file:
                img_file.write(artwork_data)
            artwork_path = "temp_artwork.jpg"
        else:
            artwork_path = PLACEHOLDER_IMAGE

        # Load and display the image
        image = Image.open(artwork_path)
        image = image.resize((150, 150), Image.LANCZOS)
        img = ImageTk.PhotoImage(image)
        artwork_label.config(image=img)
        artwork_label.image = img  # Keep a reference to avoid garbage collection
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load artwork: {str(e)}")

# GUI Setup
root = tk.Tk()
root.title("FemPEG: FLAC to ALAC Converter")
root.geometry("900x500")
root.configure(bg=BG_COLOR)

# Application icon
image = Image.open("fempfp.jpg") 
img = ImageTk.PhotoImage(image)
root.iconphoto(False, img)

# Menu Bar
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Select FLAC Folder", command=browse_folder)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="Bulk Convert", menu=file_menu)
root.config(menu=menu_bar)

# Main Frame
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

# Left Frame (Input Fields)
left_frame = ttk.Frame(main_frame)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Input File Section
input_frame = ttk.Frame(left_frame)
input_frame.pack(fill=tk.X, pady=5)

ttk.Label(input_frame, text="Select a FLAC file:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
input_var = tk.StringVar()
input_entry = ttk.Entry(input_frame, textvariable=input_var, width=40)
input_entry.grid(row=0, column=1, padx=5, pady=5)
ttk.Button(input_frame, text="Browse", command=browse_file).grid(row=0, column=2, padx=5, pady=5)

# Output File Section
output_frame = ttk.Frame(left_frame)
output_frame.pack(fill=tk.X, pady=5)

ttk.Label(output_frame, text="Output File:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
output_var = tk.StringVar()
output_entry = ttk.Entry(output_frame, textvariable=output_var, width=40, state="readonly")
output_entry.grid(row=0, column=1, padx=5, pady=5)

# FFmpeg Path Section
ffmpeg_frame = ttk.Frame(left_frame)
ffmpeg_frame.pack(fill=tk.X, pady=5)

ttk.Label(ffmpeg_frame, text="FFmpeg Path:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
ffmpeg_path_var = tk.StringVar(value=FFMPEG_PATH)
ffmpeg_entry = ttk.Entry(ffmpeg_frame, textvariable=ffmpeg_path_var, width=40, state="readonly")
ffmpeg_entry.grid(row=0, column=1, padx=5, pady=5)
ttk.Button(ffmpeg_frame, text="Set Path", command=set_ffmpeg_path).grid(row=0, column=2, padx=5, pady=5)

# Progress Bar
progress_bar = ttk.Progressbar(left_frame, orient=tk.HORIZONTAL, mode="indeterminate")
progress_bar.pack(fill=tk.X, pady=10)

# Convert Button
convert_button = ttk.Button(left_frame, text="Convert", command=convert_to_mp3, style="Accent.TButton")
convert_button.pack(pady=10)

# Log Text Area
log_text = ScrolledText(left_frame, height=8, width=50, wrap=tk.WORD, bg=ENTRY_COLOR, fg=TEXT_COLOR)
log_text.pack(fill=tk.BOTH, expand=True, pady=10)

# Exit Button
exit_button = ttk.Button(left_frame, text="Exit", command=root.quit)
exit_button.pack(pady=10)

# Right Frame (Image Display)
right_frame = ttk.Frame(main_frame)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Artwork Display
artwork_label = ttk.Label(right_frame)
artwork_label.pack(pady=10)

# Style Configuration
style = ttk.Style()
style.configure("Accent.TButton", background=BUTTON_COLOR, foreground=TEXT_COLOR, font=("Helvetica", 10, "bold"))

root.mainloop()