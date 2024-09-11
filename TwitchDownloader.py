import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import queue

# Global variable to keep track of whether a download is currently active
is_downloading = False
download_queue = queue.Queue()

# Function to get available formats from yt-dlp
def get_available_formats(url):
    try:
        # Initialize yt-dlp with format extraction options
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            return formats
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve formats: {str(e)}")
        return []

# Function to populate resolution radio buttons
def populate_resolutions(url):
    formats = get_available_formats(url)
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

# Function to download the video using yt-dlp
def download_video_worker(url, output_path, resolution):
    global is_downloading
    
    # Configure yt-dlp options
    ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'format': resolution  # Download the selected resolution
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Success", f"Download completed for: {url}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
    finally:
        is_downloading = False
        process_next_in_queue()

# Function to start a download in the background thread
def start_download(url, output_path, resolution):
    global is_downloading
    
    if is_downloading:
        messagebox.showwarning("Warning", "A download is already in progress. Adding to queue.")
        download_queue.put((url, output_path, resolution))
    else:
        is_downloading = True
        threading.Thread(target=download_video_worker, args=(url, output_path, resolution)).start()

# Function to process the next download in the queue
def process_next_in_queue():
    if not download_queue.empty():
        url, output_path, resolution = download_queue.get()
        start_download(url, output_path, resolution)

# Function to handle the download button click
def download_twitch_video():
    url = url_entry.get()
    output_path = output_dir_entry.get()
    resolution = resolution_var.get()
    
    if not url or not output_path:
        messagebox.showerror("Error", "Please provide both a Twitch URL and output directory.")
        return
    
    start_download(url, output_path, resolution)
    update_queue_listbox()

# Function to update the queue display
def update_queue_listbox():
    queue_listbox.delete(0, tk.END)
    for i, item in enumerate(list(download_queue.queue)):
        url, _, _ = item
        queue_listbox.insert(tk.END, f"{i+1}. {url}")

# Function to remove a download from the queue
def remove_from_queue():
    selected = queue_listbox.curselection()
    if not selected:
        messagebox.showwarning("Warning", "No item selected in the queue.")
        return
    
    index = selected[0]
    queue_list = list(download_queue.queue)
    del queue_list[index]
    download_queue.queue.clear()
    for item in queue_list:
        download_queue.put(item)
    update_queue_listbox()

# Function to move a download up in the queue
def move_up_in_queue():
    selected = queue_listbox.curselection()
    if not selected or selected[0] == 0:
        return
    
    index = selected[0]
    queue_list = list(download_queue.queue)
    queue_list[index], queue_list[index-1] = queue_list[index-1], queue_list[index]
    
    download_queue.queue.clear()
    for item in queue_list:
        download_queue.put(item)
    
    update_queue_listbox()
    queue_listbox.selection_set(index-1)

# Function to move a download down in the queue
def move_down_in_queue():
    selected = queue_listbox.curselection()
    if not selected or selected[0] == len(download_queue.queue) - 1:
        return
    
    index = selected[0]
    queue_list = list(download_queue.queue)
    queue_list[index], queue_list[index+1] = queue_list[index+1], queue_list[index]
    
    download_queue.queue.clear()
    for item in queue_list:
        download_queue.put(item)
    
    update_queue_listbox()
    queue_listbox.selection_set(index+1)

# Function to browse for the output directory
def browse_output_directory():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        output_dir_entry.delete(0, tk.END)
        output_dir_entry.insert(0, folder_selected)

# Function to fetch formats and dynamically update resolutions
def fetch_formats():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a Twitch video URL.")
        return
    populate_resolutions(url)

# GUI Setup
root = tk.Tk()
root.title("Twitch Video Downloader")

# URL input
tk.Label(root, text="Twitch Video URL:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)
fetch_button = tk.Button(root, text="Fetch Formats", command=fetch_formats)
fetch_button.grid(row=0, column=2, padx=10, pady=10)

# Output directory input
tk.Label(root, text="Output Directory:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
output_dir_entry = tk.Entry(root, width=50)
output_dir_entry.grid(row=1, column=1, padx=10, pady=10)
browse_button = tk.Button(root, text="Browse", command=browse_output_directory)
browse_button.grid(row=1, column=2, padx=10, pady=10)

# Resolution selection (will be dynamically populated)
tk.Label(root, text="Select Resolution:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
resolution_var = tk.StringVar(value="best")
resolutions_frame = tk.Frame(root)
resolutions_frame.grid(row=2, column=1, padx=10, pady=10, sticky="w")

# Download button
download_button = tk.Button(root, text="Download", command=download_twitch_video)
download_button.grid(row=3, column=1, padx=10, pady=10)

# Queue listbox
tk.Label(root, text="Download Queue:").grid(row=4, column=0, padx=10, pady=10, sticky="e")
queue_listbox = tk.Listbox(root, width=50, height=10)
queue_listbox.grid(row=4, column=1, padx=10, pady=10)

# Queue control buttons
control_frame = tk.Frame(root)
control_frame.grid(row=5, column=1, padx=10, pady=10)
remove_button = tk.Button(control_frame, text="Remove from Queue", command=remove_from_queue)
remove_button.grid(row=0, column=0, padx=5, pady=5)
move_up_button = tk.Button(control_frame, text="Move Up", command=move_up_in_queue)
move_up_button.grid(row=0, column=1, padx=5, pady=5)
move_down_button = tk.Button(control_frame, text="Move Down", command=move_down_in_queue)
move_down_button.grid(row=0, column=2, padx=5, pady=5)

# Start the Tkinter event loop
root.mainloop()
