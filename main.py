import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk  # For background image support
import ffmpeg
from tinytag import TinyTag 

# Default path to ffmpeg.exe
FFMPEG_PATH = "./bin/ffmpeg.exe"
os.environ['PATH'] += os.pathsep + os.path.dirname(FFMPEG_PATH)

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
        return str(round(bratefile.bitrate*1000))
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

def set_background():
    image = Image.open("background.jpg")  # Change this to your image file
    image = image.resize((800, 400), Image.LANCZOS)
    bg_image = ImageTk.PhotoImage(image)
    background_label.config(image=bg_image)
    background_label.image = bg_image

# GUI Setup
root = tk.Tk()
root.title("FLAC to MP3 Converter")
root.geometry("800x400")

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
set_background()

input_var = tk.StringVar()
output_var = tk.StringVar()
ffmpeg_path_var = tk.StringVar(value=FFMPEG_PATH)

frame = tk.Frame(root, bg='white', bd=2)
frame.pack(pady=10)

label = tk.Label(frame, text="Select a FLAC file:", bg='white')
label.grid(row=0, column=0, padx=5, pady=5)

entry = tk.Entry(frame, textvariable=input_var, width=40)
entry.grid(row=0, column=1, padx=5, pady=5)

browse_button = tk.Button(frame, text="Browse", command=browse_file)
browse_button.grid(row=0, column=2, padx=5, pady=5)

output_label = tk.Label(frame, text="Output File:", bg='white')
output_label.grid(row=1, column=0, padx=5, pady=5)

output_entry = tk.Entry(frame, textvariable=output_var, width=40, state='readonly')
output_entry.grid(row=1, column=1, padx=5, pady=5)

ffmpeg_label = tk.Label(frame, text="FFmpeg Path:", bg='white')
ffmpeg_label.grid(row=2, column=0, padx=5, pady=5)

ffmpeg_entry = tk.Entry(frame, textvariable=ffmpeg_path_var, width=40, state='readonly')
ffmpeg_entry.grid(row=2, column=1, padx=5, pady=5)

ffmpeg_button = tk.Button(frame, text="Set Path", command=set_ffmpeg_path)
ffmpeg_button.grid(row=2, column=2, padx=5, pady=5)

convert_button = tk.Button(root, text="Convert", command=convert_to_mp3)
convert_button.pack(pady=5)

log_text = tk.Text(root, height=8, width=50)
log_text.pack(pady=10)

exit_button = tk.Button(root, text="Exit", command=root.quit)
exit_button.pack(pady=5)

root.mainloop()