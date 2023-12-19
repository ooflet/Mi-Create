# Updater
# tostr 2022

# Transferred from a previous project, so naming conventions are different
# Only difference is UI which is made to match other dialogs in Mi Create

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import urllib.request
import winsound
import tempfile
import subprocess
import os
import threading

class Updater:
    def start(self):
        def download_progress_hook(block_count, block_size, total_size):
            current_size = block_count * block_size
            progress = min(int((current_size / total_size) * 100), 100)
            status.config(text=f"Downloading... {round(current_size/1000000)} MB/{round(total_size/1000000)} MB")
            progressBar["value"] = progress
            window.update()

        def install_thread(temp_file):
            try:
                status.config(text="Installing...")
                progressBar["mode"] = "indeterminate"
                progressBar["value"] = 0
                progressBar.start()
                subprocess.run([temp_file, "/verysilent"])
                progressBar.stop()
                progressBar["mode"] = "determinate"
                progressBar["value"] = 100
                status.config(text="Installation complete")
                exit_flag.set()

            except Exception as e:
                error_message = f"An error occurred: {e}"
                messagebox.showerror("Error", error_message)
                exit_flag.set()

        def download_and_install():
            url = "https://github.com/ooflet/Mi-Face-Studio/releases/latest/download/setup.exe"
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
                error_message = f"An error occurred: {e}"
                messagebox.showerror("Error", error_message)
                exit_flag.set()

        def check_exit():
            if not exit_flag.is_set():
                window.after(1000, check_exit)
            else:
                window.quit()

        window = tk.Tk()
        window.title('Updater')

        def disable_event():
            message = messagebox.askokcancel("Exit updater?", "Exit the updater? This will only cancel the download, not the install.")
            if message:
                exit_flag.set()

        window.protocol("WM_DELETE_WINDOW", disable_event)

        window_width = 500
        window_height = 300
        display_width = window.winfo_screenwidth()
        display_height = window.winfo_screenheight()

        left = int(display_width/2 - window_width/2)
        top = int(display_height/2 - window_height/2 - 50)
        window.geometry(f'{window_width}x{window_height}+{left}+{top}')
        window.resizable(False, False)
        window.minsize(500, 300)
        window.maxsize(500, 300)

        title = ttk.Label(window, text="Updating...", font=("Segoe UI", 18))
        status = ttk.Label(window, text="Getting update package...")
        progressBar = ttk.Progressbar(window, orient="horizontal", mode="indeterminate", length=462, value=0)

        title.pack(fill="both", padx=18, pady=2)
        status.pack(fill="both", padx=18, pady=4)
        progressBar.pack()

        exit_flag = threading.Event()

        # Start the download and install process in a separate thread
        download_install_thread = threading.Thread(target=download_and_install)
        download_install_thread.start()

        window.after(1000, check_exit)
        window.mainloop()

if __name__ == "__main__":
    updater = Updater()
    updater.start()
