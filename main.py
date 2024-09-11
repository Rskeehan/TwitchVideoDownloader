import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # For creating tabs
import subprocess
import os
from format_fetcher import fetch_formats  # Fetch formats using yt-dlp
import download_manager  # Download logic goes here
from queue_manager import add_to_queue, remove_from_queue, move_up_in_queue, move_down_in_queue, update_queue_listbox, process_next_in_queue

# Apply Dark Theme
def apply_dark_theme(root):
    root.configure(bg='#2e2e2e')  # Set background color for the root window

    style = ttk.Style()
    style.theme_use("clam")

    # Configure ttk styles for dark mode
    style.configure("TNotebook", background='#2e2e2e', foreground='#ffffff')
    style.configure("TNotebook.Tab", background='#3c3f41', foreground='#ffffff')
    style.map("TNotebook.Tab", background=[("selected", "#4c4f52")])

    style.configure("TFrame", background='#2e2e2e')
    style.configure("TLabel", background='#2e2e2e', foreground='#ffffff')
    style.configure("TButton", background='#3c3f41', foreground='#ffffff', borderwidth=1)
    style.map("TButton", background=[("active", "#4c4f52")])

    style.configure("TEntry", fieldbackground='#3c3f41', foreground='#ffffff')
    style.configure("TListbox", background='#3c3f41', foreground='#ffffff')
    style.configure("TRadiobutton", background='#2e2e2e', foreground='#ffffff')

# Function to fetch formats dynamically for a given Twitch URL and update GUI
def fetch_formats_for_gui(url_entry, formats_frame, resolution_var):
    url = url_entry.get()  # Get the URL from the entry field
    if not url:
        messagebox.showerror("Error", "Please enter a Twitch video URL.")
        return
    
    formats = fetch_formats(url)  # Fetch formats using the format_fetcher module
    if not formats:
        messagebox.showerror("Error", "No formats available or failed to retrieve formats.")
        return
    
    # Clear any existing radio buttons (previously fetched formats)
    for widget in formats_frame.winfo_children():
        widget.destroy()

    # Create radio buttons for each available format (resolution + framerate)
    for f in formats:
        format_label = f"{f['resolution']}p, {f['framerate']} FPS ({f['format_note']})"
        tk.Radiobutton(formats_frame, text=format_label, variable=resolution_var, value=f['format_id'], bg='#2e2e2e', fg='#ffffff', selectcolor='#4c4f52').pack(anchor="w")

# Function to open a directory browsing dialog for the output directory
def browse_output_directory(output_dir_entry):
    folder_selected = filedialog.askdirectory()  # Open a dialog to select a folder
    if folder_selected:
        output_dir_entry.delete(0, tk.END)  # Clear the current entry
        output_dir_entry.insert(0, folder_selected)  # Insert the selected folder path

# Function to start downloading the video using yt-dlp
def start_download_process(url_entry, output_dir_entry, resolution_var, queue_listbox):
    url = url_entry.get()  # Get the video URL from the entry field
    output_dir = output_dir_entry.get()  # Get the output directory from the entry field
    resolution = resolution_var.get()  # Get the selected resolution format ID
    
    if not url or not output_dir:
        messagebox.showerror("Error", "Please provide both a Twitch URL and output directory.")
        return
    
    if not resolution:
        messagebox.showerror("Error", "Please select a resolution to download.")
        return
    
    # Add the video to the queue
    add_to_queue(url, output_dir, resolution)
    update_queue_listbox(queue_listbox)  # Update the queue listbox display
    if not download_manager.is_downloading:  # Start downloading if not already in progress
        process_next_in_queue()

# Function to open the downloaded video fixer utility
def open_video_fixer():
    try:
        subprocess.Popen(['python', 'downloadedVideoFixer.py'])  # Launch the video fixer script
    except FileNotFoundError:
        messagebox.showerror("Error", "The video fixer utility could not be found.")

# Video Concatenator Functions
def select_first_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
    )
    if file_path:
        file_entry1.delete(0, tk.END)
        file_entry1.insert(0, file_path)  # Insert the selected file path into the first entry field

def select_second_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
    )
    if file_path:
        file_entry2.delete(0, tk.END)
        file_entry2.insert(0, file_path)  # Insert the selected file path into the second entry field

def concatenate_videos():
    video1 = file_entry1.get()  # Get the first video file path
    video2 = file_entry2.get()  # Get the second video file path

    if not video1 or not video2:
        messagebox.showerror("Error", "Please select both video files.")
        return

    if not os.path.exists(video1) or not os.path.exists(video2):
        messagebox.showerror("Error", "One or both of the video files do not exist.")
        return

    concat_file = "concat_list.txt"
    with open(concat_file, 'w') as f:
        f.write(f"file '{video1}'\n")
        f.write(f"file '{video2}'\n")

    output_file = os.path.join(os.path.dirname(video1), "output.mp4")

    command = [
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", output_file
    ]

    try:
        subprocess.run(command, check=True)
        messagebox.showinfo("Success", f"Videos concatenated successfully.\nSaved to: {output_file}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to concatenate videos.\n{str(e)}")
    finally:
        if os.path.exists(concat_file):
            os.remove(concat_file)

# Main application window setup
root = tk.Tk()
root.title("Twitch Video Downloader with Utilities (Dark Theme)")

# Apply the dark theme to the window
apply_dark_theme(root)

# Creating the tabbed interface using ttk.Notebook
notebook = ttk.Notebook(root)
notebook.pack(padx=10, pady=10, expand=True)

# ================= First Tab (Twitch Video Downloader) =======================
downloader_frame = ttk.Frame(notebook)
notebook.add(downloader_frame, text="Twitch Video Downloader")

# URL input for downloader tab
tk.Label(downloader_frame, text="Twitch Video URL:", bg='#2e2e2e', fg='#ffffff').grid(row=0, column=0, padx=10, pady=10, sticky="e")
url_entry = tk.Entry(downloader_frame, width=50, bg='#3c3f41', fg='#ffffff')
url_entry.grid(row=0, column=1, padx=10, pady=10)
formats_frame = tk.Frame(downloader_frame, bg='#2e2e2e')  # Frame to hold dynamically generated format radio buttons
formats_frame.grid(row=2, column=1, padx=10, pady=10)
resolution_var = tk.StringVar()  # Variable to hold the selected format ID

fetch_button = tk.Button(downloader_frame, text="Fetch Formats", command=lambda: fetch_formats_for_gui(url_entry, formats_frame, resolution_var), bg='#3c3f41', fg='#ffffff')
fetch_button.grid(row=0, column=2, padx=10, pady=10)

# Output directory input for downloader tab
tk.Label(downloader_frame, text="Output Directory:", bg='#2e2e2e', fg='#ffffff').grid(row=1, column=0, padx=10, pady=10, sticky="e")
output_dir_entry = tk.Entry(downloader_frame, width=50, bg='#3c3f41', fg='#ffffff')
output_dir_entry.grid(row=1, column=1, padx=10, pady=10)
browse_button = tk.Button(downloader_frame, text="Browse", command=lambda: browse_output_directory(output_dir_entry), bg='#3c3f41', fg='#ffffff')
browse_button.grid(row=1, column=2, padx=10, pady=10)

# Queue listbox to display the download queue
queue_listbox = tk.Listbox(downloader_frame, width=50, height=10, bg='#3c3f41', fg='#ffffff')
queue_listbox.grid(row=3, column=1, padx=10, pady=10)

# Download button to start the video download process
download_button = tk.Button(downloader_frame, text="Download", command=lambda: start_download_process(url_entry, output_dir_entry, resolution_var, queue_listbox), bg='#3c3f41', fg='#ffffff')
download_button.grid(row=4, column=1, padx=10, pady=10)

# ==================== Second Tab (Video Utilities) ============================
utilities_frame = ttk.Frame(notebook)
notebook.add(utilities_frame, text="Video Utilities")

# --------------- Section for Video Fixer ---------------
video_fixer_label = tk.Label(utilities_frame, text="Fix Downloaded Video:", bg='#2e2e2e', fg='#ffffff')
video_fixer_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

fixer_button = tk.Button(utilities_frame, text="Open Video Fixer", command=open_video_fixer, bg='#3c3f41', fg='#ffffff')
fixer_button.grid(row=0, column=1, padx=10, pady=10)

# --------------- Section for Video Concatenator ---------------
concatenator_label = tk.Label(utilities_frame, text="Concatenate Videos:", bg='#2e2e2e', fg='#ffffff')
concatenator_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

# File selection fields and buttons for concatenator
file_entry1 = tk.Entry(utilities_frame, width=40, bg='#3c3f41', fg='#ffffff')  # Entry for the first video file path
file_entry1.grid(row=2, column=0, padx=10, pady=10)

browse_button1 = tk.Button(utilities_frame, text="Browse Video 1", command=select_first_file, bg='#3c3f41', fg='#ffffff')
browse_button1.grid(row=2, column=1, padx=10, pady=10)

file_entry2 = tk.Entry(utilities_frame, width=40, bg='#3c3f41', fg='#ffffff')  # Entry for the second video file path
file_entry2.grid(row=3, column=0, padx=10, pady=10)

browse_button2 = tk.Button(utilities_frame, text="Browse Video 2", command=select_second_file, bg='#3c3f41', fg='#ffffff')
browse_button2.grid(row=3, column=1, padx=10, pady=10)

# Concatenate button to start the video concatenation process
concat_button = tk.Button(utilities_frame, text="Concatenate Videos", command=concatenate_videos, bg='#3c3f41', fg='#ffffff')
concat_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Start the main event loop
root.mainloop()
