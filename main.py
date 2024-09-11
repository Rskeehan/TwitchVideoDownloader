import tkinter as tk
from tkinter import filedialog, messagebox
from format_fetcher import fetch_formats
import download_manager  # Import download_manager module
from queue_manager import add_to_queue, remove_from_queue, move_up_in_queue, move_down_in_queue, update_queue_listbox, process_next_in_queue

# GUI Setup
root = tk.Tk()
root.title("Twitch Video Downloader")

# Function to browse for the output directory
def browse_output_directory():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        output_dir_entry.delete(0, tk.END)
        output_dir_entry.insert(0, folder_selected)

# Function to fetch formats and dynamically update resolutions
def fetch_formats_for_gui():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a Twitch video URL.")
        return
    formats = fetch_formats(url)
    populate_resolutions(formats)

# Function to populate resolution radio buttons
def populate_resolutions(formats):
    if formats:
        for widget in resolutions_frame.winfo_children():
            widget.destroy()  # Clear previous radio buttons

        # Create radio buttons for each available format
        for f in formats:
            resolution = f"{f.get('format_note', 'Unknown')} - {f['ext']} ({f.get('height', 'Unknown')}p)"
            framerate = f.get('fps', 'Unknown FPS')
            format_code = f['format_id']
            label = f"{resolution}, {framerate} FPS"
            tk.Radiobutton(resolutions_frame, text=label, variable=resolution_var, value=format_code).pack(anchor="w")

# Function to start the next download in the queue
def start_next_in_queue():
    next_download = process_next_in_queue()
    if next_download:
        url, output_path, resolution = next_download
        download_manager.start_download(url, output_path, resolution, start_next_in_queue)  # Use download_manager here

# Function to handle the download button click
def start_download_process():
    url = url_entry.get()
    output_path = output_dir_entry.get()
    resolution = resolution_var.get()
    
    if not url or not output_path:
        messagebox.showerror("Error", "Please provide both a Twitch URL and output directory.")
        return

    add_to_queue(url, output_path, resolution)
    update_queue_listbox(queue_listbox)

    # Start the first download if it's not already in progress
    if not download_manager.is_downloading:  # Check the download status using download_manager
        start_next_in_queue()

# URL input
tk.Label(root, text="Twitch Video URL:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)
fetch_button = tk.Button(root, text="Fetch Formats", command=fetch_formats_for_gui)
fetch_button.grid(row=0, column=2, padx=10, pady=10)

# Output directory input
tk.Label(root, text="Output Directory:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
output_dir_entry = tk.Entry(root, width=50)
output_dir_entry.grid(row=1, column=1, padx=10, pady=10)
browse_button = tk.Button(root, text="Browse", command=browse_output_directory)
browse_button.grid(row=1, column=2, padx=10, pady=10)

# Resolution selection
tk.Label(root, text="Select Resolution:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
resolution_var = tk.StringVar(value="best")
resolutions_frame = tk.Frame(root)
resolutions_frame.grid(row=2, column=1, padx=10, pady=10, sticky="w")

# Download button
download_button = tk.Button(root, text="Download", command=start_download_process)
download_button.grid(row=3, column=1, padx=10, pady=10)

# Queue listbox
tk.Label(root, text="Download Queue:").grid(row=4, column=0, padx=10, pady=10, sticky="e")
queue_listbox = tk.Listbox(root, width=50, height=10)
queue_listbox.grid(row=4, column=1, padx=10, pady=10)

# Queue control buttons
control_frame = tk.Frame(root)
control_frame.grid(row=5, column=1, padx=10, pady=10)
remove_button = tk.Button(control_frame, text="Remove from Queue", command=lambda: remove_from_queue(queue_listbox))
remove_button.grid(row=0, column=0, padx=5, pady=5)
move_up_button = tk.Button(control_frame, text="Move Up", command=lambda: move_up_in_queue(queue_listbox))
move_up_button.grid(row=0, column=1, padx=5, pady=5)
move_down_button = tk.Button(control_frame, text="Move Down", command=lambda: move_down_in_queue(queue_listbox))
move_down_button.grid(row=0, column=2, padx=5, pady=5)

# Start the Tkinter event loop
root.mainloop()
