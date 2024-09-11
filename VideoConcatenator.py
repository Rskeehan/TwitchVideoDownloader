import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def select_first_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
    )
    if file_path:
        file_entry1.delete(0, tk.END)
        file_entry1.insert(0, file_path)

def select_second_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
    )
    if file_path:
        file_entry2.delete(0, tk.END)
        file_entry2.insert(0, file_path)

def concatenate_videos():
    video1 = file_entry1.get()
    video2 = file_entry2.get()

    if not video1 or not video2:
        messagebox.showerror("Error", "Please select both video files.")
        return

    if not os.path.exists(video1) or not os.path.exists(video2):
        messagebox.showerror("Error", "One or both of the video files do not exist.")
        return

    # Create a text file for concatenation
    concat_file = "concat_list.txt"
    with open(concat_file, 'w') as f:
        f.write(f"file '{video1}'\n")
        f.write(f"file '{video2}'\n")

    # Output file path
    output_file = os.path.join(os.path.dirname(video1), "output.mp4")

    # ffmpeg command to concatenate without re-encoding
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
            os.remove(concat_file)  # Clean up the temporary concat file

# Create the main application window
root = tk.Tk()
root.title("MP4 Video Concatenator")

# File selection fields and buttons
file_entry1 = tk.Entry(root, width=50)
file_entry1.grid(row=0, column=0, padx=10, pady=10)

browse_button1 = tk.Button(root, text="Browse Video 1", command=select_first_file)
browse_button1.grid(row=0, column=1, padx=10, pady=10)

file_entry2 = tk.Entry(root, width=50)
file_entry2.grid(row=1, column=0, padx=10, pady=10)

browse_button2 = tk.Button(root, text="Browse Video 2", command=select_second_file)
browse_button2.grid(row=1, column=1, padx=10, pady=10)

# Concatenate button
concat_button = tk.Button(root, text="Concatenate", command=concatenate_videos)
concat_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Start the application
root.mainloop()
