import yt_dlp
import threading
from tkinter import messagebox

is_downloading = False

# Function to download the video using yt-dlp
def download_video_worker(url, output_path, resolution, callback):
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
        callback()  # Call the callback to process the next item in the queue

def start_download(url, output_path, resolution, callback):
    global is_downloading
    
    if is_downloading:
        messagebox.showwarning("Warning", "A download is already in progress. Adding to queue.")
    else:
        is_downloading = True
        threading.Thread(target=download_video_worker, args=(url, output_path, resolution, callback)).start()
