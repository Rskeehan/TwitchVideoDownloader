import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def select_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
    )
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

def fix_video():
    input_file = file_entry.get()
    if not input_file:
        messagebox.showerror("Error", "Please select a video file.")
        return

    if not os.path.exists(input_file):
        messagebox.showerror("Error", "File does not exist.")
        return

    # Set output path with '_Fixed' suffix
    output_file = os.path.splitext(input_file)[0] + "_Fixed.mp4"

    # ffmpeg command to fix the video
    command = [
        "ffmpeg", "-i", input_file, "-c", "copy", "-bsf:a", "aac_adtstoasc", output_file
    ]

    try:
        subprocess.run(command, check=True)
        messagebox.showinfo("Success", f"Video fixed successfully.\nSaved to: {output_file}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to process video.\n{str(e)}")

# Create the main application window
root = tk.Tk()
root.title("Video Fixer")

# File selection field
file_entry = tk.Entry(root, width=50)
file_entry.grid(row=0, column=0, padx=10, pady=10)

# Browse button
browse_button = tk.Button(root, text="Browse", command=select_file)
browse_button.grid(row=0, column=1, padx=10, pady=10)

# Fix video button
fix_button = tk.Button(root, text="Fix Video", command=fix_video)
fix_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# Start the application
root.mainloop()
