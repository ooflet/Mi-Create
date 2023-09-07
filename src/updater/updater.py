import tkinter as tk
from tkinter import ttk
import urllib.request
import winsound
import tempfile
import subprocess
import os
import threading

def download_progress_hook(block_count, block_size, total_size):
    current_size = block_count * block_size
    progress = min(int((current_size / total_size) * 100), 100)
    progressBar["value"] = progress
    window.update()

def install_thread(temp_file):
    try:
        status.config(text="Installing...")
        progressBar["mode"] = "indeterminate"
        progressBar["value"] = 0
        progressBar.start()
        subprocess.run([temp_file, "/verysilent"])
        window.quit()

    except Exception as e:
        winsound.PlaySound('SystemHand', winsound.SND_ALIAS | winsound.SND_ASYNC)
        error_message = f"An error occurred: {e}"
        status.config(text=error_message)

def download_and_install():
    url = "https://github.com/ooflet/Mi-Face-Studio/releases/latest/download/Mi.Face.Studio.Setup.exe"
    filename = os.path.basename(url)
    filename = filename.replace('?', '_')

    status.config(text="Downloading...")
    progressBar["mode"] = "determinate"

    try:
        temp_folder = tempfile.gettempdir()
        temp_file = os.path.join(temp_folder, filename)

        urllib.request.urlretrieve(url, temp_file, reporthook=download_progress_hook)

        install_thread_object = threading.Thread(target=install_thread, args=(temp_file,))
        install_thread_object.start()

    except Exception as e:
        winsound.PlaySound('SystemHand', winsound.SND_ALIAS | winsound.SND_ASYNC)
        error_message = f"An error occurred: {e}"
        status.config(text=error_message)

window = tk.Tk()
window.title('Updater')

window_width = 300
window_height = 55
display_width = window.winfo_screenwidth()
display_height = window.winfo_screenheight()

left = int(display_width/2 - window_width/2)
top = int(display_height/2 - window_height/2 - 50)
window.geometry(f'{window_width}x{window_height}+{left}+{top}')
window.minsize(300, 55)
window.maxsize(300, 55)

status = ttk.Label(window, text="Getting update package...")
progressBar = ttk.Progressbar(window, orient="horizontal", mode="indeterminate", length=285, value=0)

status.pack(fill="both", padx=7.5, pady=2)
progressBar.pack()

exit_flag = threading.Event()

download_and_install()

def check_exit():
    if not exit_flag.is_set():
        window.after(1000, check_exit)
    else:
        window.quit()

window.after(1000, check_exit)
window.mainloop()
