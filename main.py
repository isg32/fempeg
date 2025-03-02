import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText  # For scrollable log text
from PIL import Image, ImageTk  # For image support
import ffmpeg
from tinytag import TinyTag
from mutagen.flac import FLAC  # For extracting artwork from FLAC files
from mutagen.mp4 import MP4, MP4Cover  # For embedding artwork into M4A files

# Default path to ffmpeg.exe
FFMPEG_PATH = "./bin/ffmpeg.exe"
os.environ['PATH'] += os.pathsep + os.path.dirname(FFMPEG_PATH)

# Color scheme
BG_COLOR = "#f0f0f0"
BUTTON_COLOR = "#4CAF50"
TEXT_COLOR = "#333333"
ENTRY_COLOR = "#ffffff"

# Placeholder image path (use a default image if no artwork is found)
PLACEHOLDER_IMAGE = "fempfp.jpg"  # Replace with your placeholder image path

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

def convert_to_m4a():
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

        # Convert FLAC to M4A using ffmpeg
        (
            ffmpeg
            .input(input_file)
            .output(output_file, acodec="alac", map="0:a", f="mp4", ab=bitrate, map_metadata=0, vf="scale=300:-1")
            .run(overwrite_output=True)
        )

        # Embed artwork into the M4A file
        embed_artwork(input_file, output_file)

        log_text.insert(tk.END, "Conversion completed successfully!\n")
        messagebox.showinfo("Success", f"Conversion completed: {output_file}")
    except Exception as e:
        log_text.insert(tk.END, f"Error: {str(e)}\n")
        messagebox.showerror("Error", f"Conversion failed: {str(e)}")
    finally:
        # Stop progress bar
        progress_bar.stop()

def embed_artwork(input_file, output_file):
    try:
        # Extract artwork from FLAC file
        flac = FLAC(input_file)
        if flac.pictures:
            artwork_data = flac.pictures[0].data
            artwork_path = "temp_artwork.jpg"
            with open(artwork_path, "wb") as img_file:
                img_file.write(artwork_data)
        else:
            artwork_path = PLACEHOLDER_IMAGE

        # Load the artwork image
        with open(artwork_path, "rb") as img_file:
            artwork = img_file.read()

        # Embed artwork into the M4A file using mutagen.mp4
        m4a = MP4(output_file)
        m4a.tags["covr"] = [MP4Cover(artwork, MP4Cover.FORMAT_JPEG)]  # Use FORMAT_PNG for PNG images
        m4a.save()

        log_text.insert(tk.END, "Artwork embedded successfully!\n")
    except Exception as e:
        log_text.insert(tk.END, f"Error embedding artwork: {str(e)}\n")

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("FLAC files", "*.flac")])
    if file_path:
        input_var.set(file_path)
        display_artwork(file_path)
        update_music_title(file_path)

def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        flac_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".flac")]
        if flac_files:
            for file in flac_files:
                input_var.set(file)
                convert_to_m4a()
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

def update_music_title(file_path):
    try:
        flac = FLAC(file_path)
        title = flac.tags.get("title", [os.path.basename(file_path)])[0]
        music_title_var.set(title)
    except Exception as e:
        music_title_var.set("Unknown Title")

# GUI Setup
root = tk.Tk()
root.title("FemPEG: FLAC to ALAC Converter")
root.geometry("900x600")
root.configure(bg=BG_COLOR)

# Application icon
image = Image.open("fempfp.jpg") 
img = ImageTk.PhotoImage(image)
root.iconphoto(False, img)

# Main Frame
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

# Row A
row_a = ttk.Frame(main_frame)
row_a.pack(fill=tk.BOTH, expand=True)

# Row X
row_x = ttk.Frame(row_a)
row_x.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Column A (Input Fields)
column_a = ttk.Frame(row_x)
column_a.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Select a FLAC file
input_frame = ttk.Frame(column_a)
input_frame.pack(fill=tk.X, pady=5)

ttk.Label(input_frame, text="Select a FLAC file:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
input_var = tk.StringVar()
input_entry = ttk.Entry(input_frame, textvariable=input_var, width=40)
input_entry.grid(row=0, column=1, padx=5, pady=5)
ttk.Button(input_frame, text="Browse", command=browse_file).grid(row=0, column=2, padx=5, pady=5)

# Output file
output_frame = ttk.Frame(column_a)
output_frame.pack(fill=tk.X, pady=5)

ttk.Label(output_frame, text="Output File:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
output_var = tk.StringVar()
output_entry = ttk.Entry(output_frame, textvariable=output_var, width=40, state="readonly")
output_entry.grid(row=0, column=1, padx=5, pady=5)

# FFMPEG Path
ffmpeg_frame = ttk.Frame(column_a)
ffmpeg_frame.pack(fill=tk.X, pady=5)

ttk.Label(ffmpeg_frame, text="FFmpeg Path:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
ffmpeg_path_var = tk.StringVar(value=FFMPEG_PATH)
ffmpeg_entry = ttk.Entry(ffmpeg_frame, textvariable=ffmpeg_path_var, width=40, state="readonly")
ffmpeg_entry.grid(row=0, column=1, padx=5, pady=5)
ttk.Button(ffmpeg_frame, text="Set Path", command=set_ffmpeg_path).grid(row=0, column=2, padx=5, pady=5)

# Column B (Artwork and Music Title)
column_b = ttk.Frame(row_x)
column_b.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Artwork Display (Placeholder Image)
placeholder_image = Image.open(PLACEHOLDER_IMAGE)
placeholder_image = placeholder_image.resize((150, 150), Image.LANCZOS)
placeholder_img = ImageTk.PhotoImage(placeholder_image)
artwork_label = ttk.Label(column_b, image=placeholder_img)
artwork_label.image = placeholder_img  # Keep a reference to avoid garbage collection
artwork_label.pack(pady=10)

# Music Title
music_title_var = tk.StringVar(value="Music Title")
music_title_label = ttk.Label(column_b, textvariable=music_title_var, font=("Helvetica", 12, "bold"))
music_title_label.pack(pady=10)

# Row Y
row_y = ttk.Frame(main_frame)
row_y.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

# Progress Bar
progress_bar = ttk.Progressbar(row_a, orient=tk.HORIZONTAL, mode="indeterminate")
progress_bar.pack(fill=tk.X, pady=10)

# Convert Button
convert_button = ttk.Button(row_y, text="Convert", command=convert_to_m4a, style="Accent.TButton")
convert_button.pack(pady=10)

# Console (Log Text Area)
log_text = ScrolledText(row_y, height=8, width=80, wrap=tk.WORD, bg=ENTRY_COLOR, fg=TEXT_COLOR)
log_text.pack(fill=tk.BOTH, expand=True, pady=10)

# Exit Button
exit_button = ttk.Button(row_y, text="Exit", command=root.quit)
exit_button.pack(pady=10)

# Style Configuration
style = ttk.Style()
style.configure("Accent.TButton", background=BUTTON_COLOR, foreground=TEXT_COLOR, font=("Helvetica", 10, "bold"))

root.mainloop()