import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename
import pyperclip
import re

class FilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Filter Manager')
        
        self.areas_frame = tk.Frame(root)
        self.areas_frame.pack(fill=tk.BOTH, expand=True)

        self.footer_frame = tk.Frame(root)
        self.footer_frame.pack(fill=tk.X)

        self.add_area_button = tk.Button(self.footer_frame, text="Add Area", command=self.add_area)
        self.add_area_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(self.footer_frame, text="Save Filters", command=self.save_filters)
        self.save_button.pack(side=tk.LEFT)

        self.load_button = tk.Button(self.footer_frame, text="Load Filters", command=self.load_filters)
        self.load_button.pack(side=tk.LEFT)

        self.copy_area_button = tk.Button(self.footer_frame, text="Copy Areas", command=self.copy_areas)
        self.copy_area_button.pack(side=tk.LEFT)

        self.copy_sub_area_button = tk.Button(self.footer_frame, text="Copy Sub-areas", command=self.copy_sub_areas)
        self.copy_sub_area_button.pack(side=tk.LEFT)

        self.filters = {}

    def add_area(self):
        area_input = simpledialog.askstring("Input", "Enter Area (e.g., A1, B1-C3):")
        if area_input:
            areas = self.parse_area_input(area_input)
            for area in areas:
                self.add_area_internal(area)
        
    def parse_area_input(self, area_input):
        areas = []
        for part in area_input.split(','):
            part = part.strip()
            if '-' in part:  # Handle range
                start, end = part.split('-')
                if start.isdigit() and end.isdigit():
                    areas.extend(range(int(start), int(end) + 1))
                else:
                    start_prefix, start_number = re.match(r"([A-Za-z]*)([0-9]*)", start).groups()
                    end_prefix, end_number = re.match(r"([A-Za-z]*)([0-9]*)", end).groups()
                    if start_prefix == end_prefix:
                        areas.extend([f"{start_prefix}{i}" for i in range(int(start_number), int(end_number) + 1)])
                    else:
                        areas.append(part)
            else:  # Handle single area
                areas.append(part.strip())
        return areas

    def add_area_internal(self, area):
        area_frame = tk.Frame(self.areas_frame, bd=2, relief=tk.RAISED)
        area_frame.pack(fill=tk.X, padx=5, pady=5)
        
        area_label = tk.Label(area_frame, text="Area:")
        area_label.pack(side=tk.LEFT)
        
        area_entry = tk.Entry(area_frame)
        area_entry.insert(0, area)
        area_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        add_sub_area_button = tk.Button(area_frame, text="Add Sub-area", command=lambda: self.add_sub_area(area_frame))
        add_sub_area_button.pack(side=tk.RIGHT)

        sub_areas_frame = tk.Frame(area_frame)
        sub_areas_frame.pack(fill=tk.X)

        self.filters[area_frame] = {"area_entry": area_entry, "sub_areas": [], "sub_areas_frame": sub_areas_frame}

    def add_sub_area(self, area_frame):
        sub_area_frame = tk.Frame(self.filters[area_frame]["sub_areas_frame"])
        sub_area_frame.pack(fill=tk.X, padx=10, pady=2)

        sub_area_entry = tk.Entry(sub_area_frame)
        sub_area_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        remove_button = tk.Button(sub_area_frame, text="Remove", command=lambda: self.remove_sub_area(area_frame, sub_area_frame))
        remove_button.pack(side=tk.LEFT)

        self.filters[area_frame]["sub_areas"].append(sub_area_frame)

    def remove_sub_area(self, area_frame, sub_area_frame):
        sub_area_frame.destroy()
        self.filters[area_frame]["sub_areas"].remove(sub_area_frame)

    def save_filters(self):
        file_path = asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if not file_path:
            return 

        try:
            with open(file_path, 'w') as file:
                for area_frame, data in self.filters.items():
                    area = data["area_entry"].get().strip()
                    sub_areas = [self.format_sub_area(child.winfo_children()[0].get().strip()) for child in data["sub_areas"]]
                    if area and sub_areas:
                        file.write(f"{area}:{','.join(sub_areas)}\n")
            messagebox.showinfo("Save Successful", "Filters saved successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred: {e}")

    def format_sub_area(self, sub_area):
        if sub_area == '*':
            return '00-100'
        return sub_area

    def load_filters(self):
        file_path = askopenfilename(filetypes=[("Text files", "*.txt")])
        if not file_path:
            return

        try:
            with open(file_path, 'r') as file:
                for line in file:
                    area, sub_areas = line.strip().split(':')
                    area_frame = self.add_area_internal(area.strip())
                    for sub_area in sub_areas.split(','):
                        self.add_sub_area_internal(area_frame, sub_area.strip())
            messagebox.showinfo("Load Successful", "Filters loaded successfully.")
        except Exception as e:
            messagebox.showerror("Load Error", f"An error occurred: {e}")

    def add_sub_area_internal(self, area_frame, sub_area):
        sub_area_frame = tk.Frame(self.filters[area_frame]["sub_areas_frame"])
        sub_area_frame.pack(fill=tk.X, padx=10, pady=2)

        sub_area_entry = tk.Entry(sub_area_frame)
        sub_area_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        sub_area_entry.insert(0, sub_area)

        remove_button = tk.Button(sub_area_frame, text="Remove", command=lambda: self.remove_sub_area(area_frame, sub_area_frame))
        remove_button.pack(side=tk.LEFT)

        self.filters[area_frame]["sub_areas"].append(sub_area_frame)

    def copy_areas(self):
        areas = ",".join([data["area_entry"].get().strip() for data in self.filters.values()])
        pyperclip.copy(areas)
        messagebox.showinfo("Copy Successful", "Areas copied to clipboard.")

    def copy_sub_areas(self):
        sub_areas = []
        for data in self.filters.values():
            sub_areas.extend([self.format_sub_area(child.winfo_children()[0].get().strip()) for child in data["sub_areas"]])
        pyperclip.copy(",".join(sub_areas))
        messagebox.showinfo("Copy Successful", "Sub-areas copied to clipboard.")


if __name__ == "__main__":
    root = tk.Tk()
    app = FilterApp(root)
    root.mainloop()
