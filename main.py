import json
import os
import threading

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk


def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2 + 50)
    window.geometry(f'{width}x{height}+{x}+{y}')


class ImageConverterApp:
    def __init__(self, _root):
        self.menu_bar      = None
        self.photo_image   = None
        self.image_label   = None
        self.progress      = None
        self.export_button = None
        self.size_label    = None
        self.format_option = None
        self.format_label  = None
        self.quality_scale = None
        self.format_var    = None
        self.remove_button = None
        self.add_button    = None
        self.file_listbox  = None
        self.files_label   = None
        self.paned_window  = None

        self.bg_color       = "#2e2e2e"
        self.fg_color       = "#ffffff"
        self.button_color   = "#444444"
        self.entry_bg_color = "#3e3e3e"

        self.root = _root

        self.lang_dir = os.path.join(os.path.dirname(__file__), 'lang')
        self.settings_file = os.path.join(os.path.dirname(__file__), 'settings.json')

        self.settings = self.load_settings()
        self.current_language = self.settings.get('language', 'eng')

        self.lang_data = self.load_language(self.current_language)

        self.root.title(self.lang_data.get("title", "WebPic - Image Converter"))
        self.files = []
        self.current_image = None

        self.root.minsize(1200, 800)

        self.create_widgets()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}

    def load_language(self, lang_code):
        lang_file = os.path.join(self.lang_dir, f"{lang_code}.json")
        if os.path.exists(lang_file):
            with open(lang_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            messagebox.showerror("Error", f"Language file {lang_file} not found.")
            return {}

    def create_widgets(self):
        self.paned_window = tk.PanedWindow(
            self.root,
            bg=self.bg_color,
            bd=0,
            sashwidth=5,
            sashrelief='raised'
        )
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(self.paned_window, bg=self.bg_color)
        self.paned_window.add(left_frame, minsize=500)

        right_frame = tk.Frame(self.paned_window, bg=self.bg_color)
        self.paned_window.add(right_frame, minsize=200)

        self.create_left_panel(left_frame)
        self.create_right_panel(right_frame)

        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.menu_bar.add_command(
            label=self.lang_data.get("settings", "Settings"),
            command=self.open_settings_window
        )
        self.create_menu()

    def create_left_panel(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)

        self.files_label = tk.Label(
            parent,
            text=self.lang_data.get("files_list", "Files List:"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.files_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        listbox_frame = tk.Frame(parent, bg=self.bg_color)
        listbox_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)

        self.file_listbox = tk.Listbox(
            listbox_frame,
            bg=self.entry_bg_color,
            fg=self.fg_color
        )
        self.file_listbox.grid(row=0, column=0, sticky="nsew")
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)

        v_scrollbar = tk.Scrollbar(
            listbox_frame,
            orient="vertical",
            command=self.file_listbox.yview
        )
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_listbox.config(yscrollcommand=v_scrollbar.set)

        h_scrollbar = tk.Scrollbar(
            listbox_frame,
            orient="horizontal",
            command=self.file_listbox.xview
        )
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.file_listbox.config(xscrollcommand=h_scrollbar.set)

        buttons_frame = tk.Frame(parent, bg=self.bg_color)
        buttons_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.add_button = tk.Button(
            buttons_frame,
            text=self.lang_data.get("add_button", "+"),
            command=self.add_files,
            bg=self.button_color,
            fg=self.fg_color,
            width=16
        )
        self.add_button.pack(side="left", padx=(0, 5))

        self.remove_button = tk.Button(
            buttons_frame,
            text=self.lang_data.get("remove_button", "X"),
            command=self.remove_file,
            bg=self.button_color,
            fg=self.fg_color,
            width=16
        )
        self.remove_button.pack(side="left")

        self.format_var = tk.StringVar(value="PNG")
        self.format_label = tk.Label(
            parent,
            text=self.lang_data.get("export_format", "Export Format:"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.format_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.format_option = ttk.Combobox(
            parent,
            textvariable=self.format_var,
            values=["PNG", "JPEG"],
            state="readonly"
        )
        self.format_option.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        self.format_option.bind("<<ComboboxSelected>>", self.toggle_quality_slider)

        self.quality_scale = tk.Scale(
            parent,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            label=self.lang_data.get("quality_jpeg", "JPEG Quality"),
            bg=self.bg_color,
            fg=self.fg_color,
            highlightbackground=self.bg_color,
            troughcolor=self.entry_bg_color
        )
        self.quality_scale.set(75)
        self.quality_scale.grid(row=5, column=0, padx=5, pady=5, sticky="ew")
        self.quality_scale.bind("<Motion>", self.update_estimated_size)
        self.quality_scale.grid_remove()

        self.size_label = tk.Label(parent, text="", bg=self.bg_color, fg=self.fg_color)
        self.size_label.grid(row=6, column=0, padx=5, pady=5, sticky="w")

        self.export_button = tk.Button(
            parent,
            text=self.lang_data.get("export_button", "Export"),
            command=self.start_export_thread,
            bg=self.button_color,
            fg=self.fg_color
        )
        self.export_button.grid(row=7, column=0, padx=5, pady=5, sticky="ew")

        self.progress = ttk.Progressbar(parent, orient="horizontal", mode="determinate")
        self.progress.grid(row=8, column=0, padx=5, pady=5, sticky="ew")

    def create_right_panel(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        self.image_label = tk.Label(parent, bg=self.bg_color)
        self.image_label.grid(row=0, column=0, sticky="nsew")

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("WebP Images", "*.webp")])
        if files:
            for file in files:
                if file not in self.files:
                    self.files.append(file)
                    self.file_listbox.insert(tk.END, file)

    def remove_file(self):
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            file_path = self.file_listbox.get(index)
            self.files.remove(file_path)
            self.file_listbox.delete(index)
            if self.current_image and getattr(self.current_image, 'filename', '') == file_path:
                self.current_image = None
                self.image_label.config(image='')
        else:
            messagebox.showwarning(
                self.lang_data.get("warning", "Warning"),
                self.lang_data.get("no_file_selected_to_remove", "No file selected to remove.")
            )

    def on_file_select(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            file_path = self.file_listbox.get(index)
            self.display_image(file_path)

    def display_image(self, file_path):
        try:
            img = Image.open(file_path)
            img.filename = file_path
            self.current_image = img
            self.update_image_preview()
        except Exception as e:
            messagebox.showerror(
                self.lang_data.get("error", "Error"),
                f"{self.lang_data.get('failed_to_load_image', 'Failed to load image')}: {e}"
            )

    def update_image_preview(self):
        if self.current_image:
            label_width = self.image_label.winfo_width()
            label_height = self.image_label.winfo_height()

            if label_width > 1 and label_height > 1:
                img = self.current_image.copy()
                if hasattr(Image, 'LANCZOS'):
                    resample_method = Image.Resampling.LANCZOS
                elif hasattr(Image, 'ANTIALIAS'):
                    resample_method = Image.ANTIALIAS
                elif hasattr(Image, 'BILINEAR'):
                    resample_method = Image.Resampling.BILINEAR
                else:
                    resample_method = Image.Resampling.NEAREST
                img.thumbnail((label_width, label_height), resample_method)
                self.photo_image = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.photo_image)
            else:
                self.root.after(100, self.update_image_preview)

    def on_resize(self, _event):
        self.update_image_preview()

    def toggle_quality_slider(self, _event):
        if self.format_var.get() == "JPEG":
            self.quality_scale.grid()
            self.size_label.config(text="")
        else:
            self.quality_scale.grid_remove()
            self.size_label.config(text="")

    def update_estimated_size(self, _event):
        quality = self.quality_scale.get()
        self.size_label.config(
            text=f"{self.lang_data.get('selected_quality', 'Selected quality')}: {quality}"
        )

    def start_export_thread(self):
        export_thread = threading.Thread(target=self.export_images)
        export_thread.start()

    def export_images(self):
        if not self.files:
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    self.lang_data.get("error", "Error"),
                    self.lang_data.get("no_files_selected", "No files selected for export.")
                )
            )
            return

        export_dir = filedialog.askdirectory(
            title=self.lang_data.get("select_export_dir", "Select export directory")
        )
        if not export_dir:
            return

        self.progress["maximum"] = len(self.files)
        self.progress["value"] = 0

        export_format = self.format_var.get().lower()
        quality = self.quality_scale.get() if export_format == "jpeg" else None

        try:
            for idx, file in enumerate(self.files):
                img = Image.open(file)
                filename = os.path.splitext(os.path.basename(file))[0] + f".{export_format}"
                save_path = os.path.join(export_dir, filename)
                save_kwargs = {}
                if export_format == "jpeg":
                    save_kwargs["quality"] = quality
                img.save(save_path, **save_kwargs)
                self.root.after(0, self.update_progress)
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    self.lang_data.get("success", "Success"),
                    self.lang_data.get("export_completed", "Export completed successfully!")
                )
            )
        except Exception as e:
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    self.lang_data.get("error", "Error"),
                    f"{self.lang_data.get('an_error_occurred', 'An error occurred')}: {e}"
                )
            )

    def update_progress(self):
        self.progress["value"] += 1

    def open_settings_window(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title(self.lang_data.get("settings", "Settings"))
        settings_window.transient(self.root)
        settings_window.grab_set()
        settings_window.resizable(False, False)

        settings_window.configure(bg=self.bg_color)

        center_window(settings_window)

        language_label = tk.Label(
            settings_window,
            text=self.lang_data.get("language", "Language:"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        language_label.pack(padx=10, pady=10)

        languages = []
        for filename in os.listdir(self.lang_dir):
            if filename.endswith(".json"):
                languages.append(filename[:-5])

        language_var = tk.StringVar(value=self.current_language)

        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            'Custom.TCombobox',
            fieldbackground=self.entry_bg_color,
            background=self.entry_bg_color,
            foreground=self.fg_color,
            arrowcolor=self.fg_color
        )
        style.map(
            'Custom.TCombobox',
            fieldbackground=[('readonly', self.entry_bg_color)],
            background=[('readonly', self.entry_bg_color)]
        )

        language_dropdown = ttk.Combobox(
            settings_window,
            textvariable=language_var,
            values=languages,
            state="readonly",
            style='Custom.TCombobox'
        )
        language_dropdown.pack(padx=10, pady=10)

        buttons_frame = tk.Frame(settings_window, bg=self.bg_color)
        buttons_frame.pack(pady=10)

        save_button = tk.Button(
            buttons_frame,
            text=self.lang_data.get("save", "Save"),
            command=lambda: self.save_settings(language_var.get(), settings_window),
            bg=self.button_color,
            fg=self.fg_color
        )
        save_button.pack(side="left", padx=5)

        cancel_button = tk.Button(
            buttons_frame,
            text=self.lang_data.get("cancel", "Cancel"),
            command=settings_window.destroy,
            bg=self.button_color,
            fg=self.fg_color
        )
        cancel_button.pack(side="left", padx=5)


    def save_settings(self, selected_language, settings_window):
        self.settings['language'] = selected_language
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f)

        self.current_language = selected_language
        self.lang_data = self.load_language(self.current_language)
        self.update_language()

        settings_window.destroy()

    def create_menu(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.menu_bar.add_command(
            label=self.lang_data.get("settings", "Settings"),
            command=self.open_settings_window
        )

    def update_language(self):
        self.root.title(self.lang_data.get("title", "Image Converter"))

        self.files_label.config(text=self.lang_data.get("files_list", "Files List:"))
        self.format_label.config(text=self.lang_data.get("export_format", "Export Format:"))
        self.quality_scale.config(label=self.lang_data.get("quality_jpeg", "JPEG Quality"))

        self.export_button.config(text=self.lang_data.get("export_button", "Export"))
        self.add_button.config(text=self.lang_data.get("add_button", "+"))
        self.remove_button.config(text=self.lang_data.get("remove_button", "X"))

        self.menu_bar.destroy()
        self.create_menu()

    def run(self):
        center_window(self.root)
        self.image_label.bind('<Configure>', self.on_resize)
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverterApp(root)
    app.run()
