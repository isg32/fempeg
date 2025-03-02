import os
import tkinter as tk
from tkinter import PhotoImage, filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText  # For scrollable log text
from PIL import Image, ImageTk  # For background image support
import ffmpeg
from tinytag import TinyTag

# Default path to ffmpeg.exe
FFMPEG_PATH = "./bin/ffmpeg.exe"
os.environ['PATH'] += os.pathsep + os.path.dirname(FFMPEG_PATH)

# Color scheme
BG_COLOR = "#f0f0f0"
BUTTON_COLOR = "#4CAF50"
TEXT_COLOR = "#333333"
ENTRY_COLOR = "#ffffff"

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

# def set_background():
#     image = Image.open("background.jpg")  # Change this to your image file
#     image = image.resize((900, 500), Image.LANCZOS)
#     bg_image = ImageTk.PhotoImage(image)
#     background_label.config(image=bg_image)
#     background_label.image = bg_image

# GUI Setup
root = tk.Tk()
root.title("FemPEG: FLAC to ALAC Converter")
root.geometry("900x500")
root.configure(bg=BG_COLOR)

# pfp
image = Image.open("fempfp.jpg") 
img = ImageTk.PhotoImage(image)
root.iconphoto(False, img)

# Menu Bar
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Select FLAC File", command=browse_file)
file_menu.add_command(label="Select FLAC Folder", command=browse_folder)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)
root.config(menu=menu_bar)

# Background Image Setup
background_label = tk.Label(root)
background_label.place(relwidth=1, relheight=1)
# set_background()

# Main Frame
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

# Input File Section
input_frame = ttk.Frame(main_frame)
input_frame.pack(fill=tk.X, pady=5)

ttk.Label(input_frame, text="Select a FLAC file:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
input_var = tk.StringVar()
input_entry = ttk.Entry(input_frame, textvariable=input_var, width=50)
input_entry.grid(row=0, column=1, padx=5, pady=5)
ttk.Button(input_frame, text="Browse", command=browse_file).grid(row=0, column=2, padx=5, pady=5)

# Output File Section
output_frame = ttk.Frame(main_frame)
output_frame.pack(fill=tk.X, pady=5)

ttk.Label(output_frame, text="Output File:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
output_var = tk.StringVar()
output_entry = ttk.Entry(output_frame, textvariable=output_var, width=50, state="readonly")
output_entry.grid(row=0, column=1, padx=5, pady=5)

# FFmpeg Path Section
ffmpeg_frame = ttk.Frame(main_frame)
ffmpeg_frame.pack(fill=tk.X, pady=5)

ttk.Label(ffmpeg_frame, text="FFmpeg Path:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
ffmpeg_path_var = tk.StringVar(value=FFMPEG_PATH)
ffmpeg_entry = ttk.Entry(ffmpeg_frame, textvariable=ffmpeg_path_var, width=50, state="readonly")
ffmpeg_entry.grid(row=0, column=1, padx=5, pady=5)
ttk.Button(ffmpeg_frame, text="Set Path", command=set_ffmpeg_path).grid(row=0, column=2, padx=5, pady=5)

# Progress Bar
progress_bar = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, mode="indeterminate")
progress_bar.pack(fill=tk.X, pady=10)

# Convert Button
convert_button = ttk.Button(main_frame, text="Convert", command=convert_to_mp3, style="Accent.TButton")
convert_button.pack(pady=10)

# Log Text Area
log_text = ScrolledText(main_frame, height=8, width=80, wrap=tk.WORD, bg=ENTRY_COLOR, fg=TEXT_COLOR)
log_text.pack(fill=tk.BOTH, expand=True, pady=10)

# Exit Button
exit_button = ttk.Button(main_frame, text="Exit", command=root.quit)
exit_button.pack(pady=10)

# Style Configuration
style = ttk.Style()
style.configure("Accent.TButton", background=BUTTON_COLOR, foreground=TEXT_COLOR, font=("Helvetica", 10, "bold"))

root.mainloop()