# Super duper barebones colorScheme.json editor

import tkinter as tk
from tkinter import ttk, filedialog, colorchooser
import json

class ColorEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Color Editor")
        
        # Create GUI elements
        self.file_label = ttk.Label(self.master, text="Select JSON file:")
        self.file_label.grid(row=0, column=0, padx=10 ,sticky="w")
        
        self.file_entry = ttk.Entry(self.master, width=30)
        self.file_entry.grid(row=0, column=1, padx=10, sticky="w")
        
        self.browse_button = ttk.Button(self.master, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        self.scheme_label = ttk.Label(self.master, text="Scheme:")
        self.scheme_label.grid(row=1, column=0, padx=10, sticky="w")
        
        self.scheme_var = tk.StringVar()
        self.scheme_dropdown = ttk.OptionMenu(self.master, self.scheme_var, "", "")
        self.scheme_dropdown.grid(row=1, column=1, padx=10, sticky="w")
        
        self.color_frame = ttk.Frame(self.master)
        self.color_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.color_items = {
            "Base": {},
            "Disabled": {}
        }
        
    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)
            self.load_json(filename)
        
    def load_json(self, filename):
        def updateScheme(s):
            self.scheme_var.set(s)
            self.load_colors(s)

        # Clear previous color labels
        for colorGroup in self.color_items.values():
            for role in colorGroup.values():
                for widget in role:
                    widget.destroy()
        
        self.color_items = {
            "Base": {},
            "Disabled": {}
        }
        
        self.filename = filename

        # Load JSON data
        with open(filename, "r") as f:
            self.data = json.load(f)
        
        # Update scheme dropdown options
        schemes = list(self.data.keys())
        menu = self.scheme_dropdown["menu"]
        menu.delete(0, tk.END)
        for scheme in schemes:
            menu.add_command(label=scheme, command=lambda s=scheme: updateScheme(s))

        self.scheme_var.set(schemes[0])  # Default scheme
        
        # Load colors for default scheme
        self.load_colors(self.scheme_var.get())

    def rgb_to_hex(self, color):
        return f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}"
        
    def load_colors(self, scheme):
        # Clear previous color labels
        for colorGroup in self.color_items.values():
            for role in colorGroup.values():
                for widget in role:
                    widget.destroy()
        
        self.color_items = {
            "Base": {},
            "Disabled": {}
        }
        
        # Load colors for selected scheme
        base_colors = self.data[scheme]["Base"]
        disabled_colors = self.data[scheme]["Disabled"]
        
        row = 0
        for role, color in base_colors.items():
            label = ttk.Label(self.color_frame, text=role, width=15)
            label.grid(row=row, column=0, padx=5, pady=5)
            
            color_str = self.rgb_to_hex(color)
            color_entry = ttk.Entry(self.color_frame, width=10)
            color_entry.insert(0, color_str)
            color_entry.grid(row=row, column=1, padx=5, pady=5)

            color_display = tk.Label(self.color_frame, bg=color_str, width=5)
            color_display.grid(row=row, column=2, padx=5, pady=5)
            
            color_picker_button = ttk.Button(self.color_frame, text="Pick Color", command=lambda role=role, color=self.rgb_to_hex(base_colors[role]), colorScheme=scheme, colorGroup="Base": self.pick_color(role, color, colorScheme, colorGroup))
            color_picker_button.grid(row=row, column=3, padx=5, pady=5)
            
            self.color_items["Base"][role] = [label, color_entry, color_display, color_picker_button]

            row += 1
        
        for role, color in disabled_colors.items():
            label = ttk.Label(self.color_frame, text=f"{role} (Disabled)", width=15)
            label.grid(row=row, column=0, padx=5, pady=5)
            
            color_str = self.rgb_to_hex(color)
            color_entry = ttk.Entry(self.color_frame, width=10)
            color_entry.insert(0, color_str)
            color_entry.grid(row=row, column=1, padx=5, pady=5)
            
            color_display = tk.Label(self.color_frame, bg=color_str, width=5)
            color_display.grid(row=row, column=2, padx=5, pady=5)

            color_role = role
            color_picker_button = ttk.Button(self.color_frame, text="Pick Color", command=lambda role=color_role, color=self.rgb_to_hex(base_colors[role]), colorScheme=scheme, colorGroup="Disabled": self.pick_color(role, color, colorScheme, colorGroup))
            color_picker_button.grid(row=row, column=3, padx=5, pady=5)

            self.color_items["Disabled"][role] = [label, color_entry, color_display, color_picker_button]
            
            row += 1

    def pick_color(self, role, init_color, scheme, color_group):
        color = colorchooser.askcolor(initialcolor=init_color)[0]  # Returns color as (R, G, B) tuple
        if color:
            color_str = self.rgb_to_hex(color)
            self.color_items[color_group][role][2].config(bg=color_str)
            self.data[scheme][color_group][role] = color
            with open(self.filename, "w") as f:
                f.write(json.dumps(self.data, indent=4))

def main():
    root = tk.Tk()
    app = ColorEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
