import threading
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import json
import csv
import subprocess
import exifread
from PIL import Image
import pyexiv2
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
import platform
import urllib.request
import urllib.parse
import tempfile
import html
import webbrowser
import os
IS_WINDOWS = platform.system() == "Windows"

class MetadataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Metadata Viewer/Editor (EXIF • XMP • IPTC • Meta Data)")
        self.root.geometry("1200x650")

        self.style = tb.Style("flatly")

        # Top frame
        control_frame = tb.Frame(root, padding=10)
        control_frame.pack(fill=X)

        tb.Button(control_frame, text="Open File", bootstyle=PRIMARY, command=self.show_open_options).pack(side=LEFT, padx=5)

        tb.Button(control_frame, text="Save Metadata", bootstyle=SUCCESS, command=self.save_metadata).pack(side=LEFT, padx=5)
        
        tb.Button(control_frame, text="Export", bootstyle=SECONDARY, command=self.export_metadata).pack(side=LEFT, padx=5)

        tb.Button( control_frame, text="Generate Report", bootstyle=WARNING, command=self.generate_report ).pack(side=LEFT, padx=5)

        tb.Button(control_frame, text="About", bootstyle=INFO, command=self.show_about).pack(side=LEFT, padx=5)

        self.file_label = tb.Label(control_frame, text="No file selected", bootstyle=INFO)
        self.file_label.pack(side=LEFT, padx=10)

        # Table frame
        table_frame = tb.Frame(root, padding=10)
        table_frame.pack(fill=BOTH, expand=True)

        self.tree = tb.Treeview(table_frame, columns=("key", "value"), show="headings")
        self.tree.heading("key", text="Key")
        self.tree.heading("value", text="Value")

        self.tree.column("key", width=300)
        self.tree.column("value", width=600)

        self.tree.pack(fill=BOTH, expand=True)

        # Editable by double-click
        self.tree.bind("<Double-1>", self.edit_cell)

        # Right-click menu for delete
        self.tree.bind("<Button-3>", self.show_context_menu)

        self.edit_window = None
        self.edit_entry = None
        self.editing_item = None
        self.editing_column = None

        self.metadata_dict = {}
        self.current_file = None

    # -----------------------------
    # Context Menu
    # -----------------------------
    def show_context_menu(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            # Create the context menu (right-click menu)
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Context Menu")
            # Add "Delete Row" option to the context menu
            menu.add_command(label="Delete Row", command=lambda: self.confirm_delete(row_id))
            # Add "Add Row Below" option to the context menu
            menu.add_command(label="Add Row Below", command=lambda: self.show_add_row_popup(row_id))
            
            # Display the context menu at the position where the right-click happened
            menu.post(event.x_root, event.y_root)
            def close_menu(event):
                menu.unpost()

            # Bind the close_menu function to any click in the window (except on the context menu)
            self.root.bind("<Button-1>", close_menu, add='+')  # Left-click
            self.root.bind("<Button-3>", close_menu, add='+')  # Right-click
            
            # Unbind the close event when the menu is used
            def on_menu_click():
                self.root.unbind("<Button-1>", close_menu)
                self.root.unbind("<Button-3>", close_menu)

            # Bind on_menu_click when a command is clicked
            for menu_item in menu.winfo_children():
                menu_item.config(command=lambda item=menu_item: [item.invoke(), on_menu_click()])

    # -----------------------------
    # Confirm Deletion
    # -----------------------------
    def confirm_delete(self, row_id):
        # Ask the user for confirmation before deleting
        confirmation = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this row?")
        
        if confirmation:
            # If confirmed, proceed with deletion
            self.delete_row(row_id)
        else:
            # If not confirmed, do nothing
            print("Deletion canceled.")

    # -----------------------------
    # Delete Row
    # -----------------------------
    def delete_row(self, row_id):
        # Delete the row from the treeview and the metadata dictionary
        if row_id in self.metadata_dict:
            del self.metadata_dict[row_id]
        self.tree.delete(row_id)

    # -----------------------------
    # Add Row Below - Show Popup for Type Selection
    # -----------------------------
    def show_add_row_popup(self, row_id):
        # Pop-up to select EXIF, XMP, or IPTC
        popup = tk.Toplevel(self.root)
        popup.title("Select Metadata Type")
        popup.geometry("300x200")
        
        tb.Label(popup, text="Choose Metadata Type").pack(pady=10)
        
        def add_row(metadata_type):
            # Add the selected metadata type row
            self.add_row_below(row_id, metadata_type)
            popup.destroy()

        tb.Button(popup, text="EXIF", bootstyle=PRIMARY, command=lambda: add_row("EXIF")).pack(pady=5)
        tb.Button(popup, text="IPTC", bootstyle=PRIMARY, command=lambda: add_row("IPTC")).pack(pady=5)
        tb.Button(popup, text="XMP", bootstyle=PRIMARY, command=lambda: add_row("XMP")).pack(pady=5)

    # -----------------------------
    # Add Row Below Function
    # -----------------------------
    def add_row_below(self, row_id, metadata_type):
        # Add a new row below the selected row
        # For now, we will add a placeholder key-value pair based on metadata type
        if metadata_type == "EXIF":
            new_key = "Exif.Image.NewField"
            new_value = "New EXIF Data"
        elif metadata_type == "IPTC":
            new_key = "Iptc.Application2.NewField"
            new_value = "New IPTC Data"
        elif metadata_type == "XMP":
            new_key = "Xmp.::NewField"
            new_value = "New XMP Data"
        
        # Insert the new row into the Treeview
        self.metadata_dict[new_key] = new_value
        self.tree.insert("", "end", iid=new_key, values=(new_key, new_value))

    # -----------------------------
    # Open options: Local file or URL
    # -----------------------------
    def show_open_options(self):
        popup = tk.Toplevel(self.root)
        popup.title("Open")
        popup.geometry("320x180")
        popup.resizable(False, False)

        tb.Label(
            popup,
            text="Open metadata from:",
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        btn_frame = tb.Frame(popup)
        btn_frame.pack(pady=10)

        def open_local():
            popup.destroy()
            self.open_file()

        def open_url():
            popup.destroy()
            self.open_from_url()

        tb.Button(
            btn_frame,
            text="Local File",
            bootstyle=PRIMARY,
            command=open_local,
            width=14
        ).grid(row=0, column=0, padx=8)

        tb.Button(
            btn_frame,
            text="From URL",
            bootstyle=INFO,
            command=open_url,
            width=14
        ).grid(row=0, column=1, padx=8)

        tb.Button(
            popup,
            text="Cancel",
            bootstyle=SECONDARY,
            command=popup.destroy
        ).pack(pady=5)

    # -----------------------------
    # Open file from URL
    # -----------------------------
    def open_from_url(self):
        url_win = tk.Toplevel(self.root)
        url_win.title("Open from URL")
        url_win.geometry("450x180")
        url_win.resizable(False, False)

        tb.Label(
            url_win,
            text="Enter image/video URL:",
            font=("Arial", 11)
        ).pack(pady=10)

        url_var = tk.StringVar()
        entry = tb.Entry(url_win, textvariable=url_var)
        entry.pack(fill=X, padx=20)
        entry.focus_set()

        status_label = tb.Label(url_win, text="", bootstyle=INFO)
        status_label.pack(pady=5)

        def do_download_and_open():
            url = url_var.get().strip()
            if not url:
                messagebox.showerror("Error", "Please enter a URL.")
                return

            try:
                status_label.configure(text="Downloading...")
                url_win.update_idletasks()

                # Create temp dir
                tmp_dir = tempfile.mkdtemp(prefix="exifplus_")
                parsed = urllib.parse.urlparse(url)
                filename = os.path.basename(parsed.path) or "downloaded_file"
                local_path = os.path.join(tmp_dir, filename)

                # Browser-like headers
                headers = {
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    "Accept": "image/*,*/*;q=0.8"
                }

                def attempt_download(add_referer=False):
                    req = urllib.request.Request(url, headers=headers.copy())
                    if add_referer:
                        req.add_header("Referer", f"{parsed.scheme}://{parsed.netloc}")
                    try:
                        with urllib.request.urlopen(req, timeout=15) as resp:
                            data = resp.read()
                            with open(local_path, "wb") as f:
                                f.write(data)
                        return True
                    except Exception:
                        return False

                # Try 1: Normal browser headers
                ok = attempt_download(add_referer=False)

                # Try 2: Add Referer header (bypass hotlinking rules)
                if not ok:
                    ok = attempt_download(add_referer=True)

                # If still blocked → ask user to open in browser
                if not ok:
                    ask = messagebox.askyesno(
                        "Download Blocked",
                        "The server blocked downloading this image.\n"
                        "Do you want to open the URL in your browser to save it manually?"
                    )
                    if ask:
                        webbrowser.open(url)
                    return

                # SUCCESS → load file
                self.current_file = local_path
                self.file_label.config(text=local_path)

                for row in self.tree.get_children():
                    self.tree.delete(row)

                self.load_metadata()

                url_win.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"Error downloading file:\n{e}")

        btn_frame = tb.Frame(url_win)
        btn_frame.pack(pady=10)

        tb.Button(
            btn_frame,
            text="Download & Open",
            bootstyle=PRIMARY,
            command=do_download_and_open
        ).grid(row=0, column=0, padx=8)

        tb.Button(
            btn_frame,
            text="Cancel",
            bootstyle=SECONDARY,
            command=url_win.destroy
        ).grid(row=0, column=1, padx=8)

    # -----------------------------
    # Open File
    # -----------------------------
    def open_file(self):
        filename = filedialog.askopenfilename(filetypes=(
            ("Images & Video", "*.jpg *.jpeg *.png *.tiff *.mp4 *.mov *.mkv *.avi *.heic"),
            ("All files", "*.*")
        ))

        if filename:
            self.current_file = filename
            self.file_label.config(text=filename)

            for row in self.tree.get_children():
                self.tree.delete(row)

            threading.Thread(target=self.load_metadata, daemon=True).start()

    # -----------------------------
    # Load metadata
    # -----------------------------
    def load_metadata(self):
        self.metadata_dict = {}
        path = self.current_file

        try:
            # Read EXIF
            if path.lower().endswith((".jpg", ".jpeg", ".tiff", ".png", ".heic")):
                if IS_WINDOWS:
                    # ---- Windows: use exifread fallback (pyexiv2 is unstable/crashy here) ----
                    with open(path, "rb") as f:
                        tags = exifread.process_file(f, details=False)
                    for key, value in tags.items():
                        self.metadata_dict[str(key)] = str(value)
                else:
                    with open(path, 'rb') as f:
                        image_bytes = f.read()  # Read the image as bytes
                        with pyexiv2.ImageData(image_bytes) as img:  # Open image from bytes
                            # Read metadata
                            for key, value in img.read_exif().items():
                                self.metadata_dict[key] = str(value)

                            # Read IPTC metadata
                            for key, value in img.read_iptc().items():
                                self.metadata_dict[key] = str(value)

                            # Read XMP metadata
                            for key, value in img.read_xmp().items():
                                self.metadata_dict[key] = str(value)

            # Video metadata
            if path.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
                parser = createParser(path)
                metadata = extractMetadata(parser)
                if metadata:
                    for item in metadata.exportPlaintext():
                        key, val = item.split(":", 1)
                        self.metadata_dict[key.strip()] = val.strip()

        except Exception as e:
            messagebox.showerror("Error", f"Error loading metadata:\n{e}")
            return

        self.refresh_table()

    # -----------------------------
    # Refresh table
    # -----------------------------
    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for k, v in self.metadata_dict.items():
            self.tree.insert("", END, iid=k, values=(k, v))

    # -----------------------------
    # Edit table cell
    # -----------------------------
    def edit_cell(self, event):
        row_id = self.tree.focus()
        if not row_id:
            return

        col = self.tree.identify_column(event.x)
        col_index = int(col.replace("#", "")) - 1  # 0 = key, 1 = value

        self.editing_item = row_id
        self.editing_column = col_index

        old_value = self.tree.item(row_id)["values"][col_index]

        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Edit")
        self.edit_window.geometry("400x150")

        tb.Label(self.edit_window, text="Editing Cell").pack(pady=10)

        self.edit_entry = tb.Entry(self.edit_window)
        self.edit_entry.insert(0, old_value)
        self.edit_entry.pack(fill=X, padx=20)

        tb.Button(self.edit_window, text="Save", bootstyle=SUCCESS,
                  command=self.apply_edit).pack(pady=10)

    def apply_edit(self):
        new_value = self.edit_entry.get()

        old_key = self.editing_item

        # Editing KEY
        if self.editing_column == 0:
            new_key = new_value

            # Update dict
            if new_key in self.metadata_dict:
                messagebox.showerror("Error", "Key already exists!")
                return

            self.metadata_dict[new_key] = self.metadata_dict.pop(old_key)

            # Update table row
            self.tree.delete(old_key)
            self.tree.insert("", END, iid=new_key, values=(new_key, self.metadata_dict[new_key]))

        else:
            # Editing VALUE
            self.metadata_dict[old_key] = new_value
            self.tree.item(old_key, values=(old_key, new_value))

        self.edit_window.destroy()

    # -----------------------------
    # Save metadata to file
    # -----------------------------
    def save_metadata(self):
        if not self.current_file:
            messagebox.showerror("Error", "No file opened.")
            return
        
        if IS_WINDOWS:
            # On Windows, pyexiv2 is unstable for writing and may crash Python.
            messagebox.showinfo(
                "Not supported on Windows",
                "Saving metadata directly into image files is not supported on Windows in this version.\n\n"
                "You can still export metadata using the Export button (CSV or JSON)."
            )
            return

        threading.Thread(target=self._save_metadata_thread, daemon=True).start()

    def _save_metadata_thread(self):
        try:
            with open(self.current_file, 'rb+') as f:
                image_bytes = f.read()  # Read the image as bytes
                with pyexiv2.ImageData(image_bytes) as img:  # Open image from bytes
                    # Prepare the changes dictionary
                    changes = {}

                    # Modify EXIF
                    try:
                        exif_data = img.read_exif()
                        for key, val in self.metadata_dict.items():
                            if key in exif_data:  # Ensure the key exists in EXIF metadata
                                changes[key] = val
                        if changes:
                            img.modify_exif(changes)  # Modify EXIF metadata
                    except Exception as exif_error:
                        print(f"Error modifying EXIF: {exif_error}")

                    # Modify IPTC
                    try:
                        iptc_data = img.read_iptc()
                        for key, val in self.metadata_dict.items():
                            if key in iptc_data:  # Ensure the key exists in IPTC metadata
                                changes[key] = val
                        if changes:
                            img.modify_iptc(changes)  # Modify IPTC metadata
                    except Exception as iptc_error:
                        print(f"Error modifying IPTC: {iptc_error}")

                    # Modify XMP
                    try:
                        xmp_data = img.read_xmp()
                        for key, val in self.metadata_dict.items():
                            if key in xmp_data:  # Ensure the key exists in XMP metadata
                                changes[key] = val
                        if changes:
                            img.modify_xmp(changes)  # Modify XMP metadata
                    except Exception as xmp_error:
                        print(f"Error modifying XMP: {xmp_error}")

                    # Write the modified bytes back to the file
                    f.seek(0)
                    f.truncate()
                    f.write(img.get_bytes())  # Save the modified image bytes

                messagebox.showinfo("Success", "Metadata saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Error saving metadata:\n{e}")
    
    # -----------------------------
    # Export metadata (CSV / JSON)
    # -----------------------------
    def export_metadata(self):
        if not self.metadata_dict:
            messagebox.showerror("Error", "No metadata to export.")
            return

        popup = tk.Toplevel(self.root)
        popup.title("Export Metadata")
        popup.geometry("300x160")
        popup.resizable(False, False)

        tb.Label(
            popup,
            text="Export metadata as:",
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        btn_frame = tb.Frame(popup)
        btn_frame.pack(pady=10)

        def do_export_csv():
            self._export_as_csv()
            popup.destroy()

        def do_export_json():
            self._export_as_json()
            popup.destroy()

        tb.Button(
            btn_frame,
            text="CSV",
            bootstyle=PRIMARY,
            command=do_export_csv,
            width=10
        ).grid(row=0, column=0, padx=10)

        tb.Button(
            btn_frame,
            text="JSON",
            bootstyle=SUCCESS,
            command=do_export_json,
            width=10
        ).grid(row=0, column=1, padx=10)

        tb.Button(
            popup,
            text="Cancel",
            bootstyle=SECONDARY,
            command=popup.destroy
        ).pack(pady=5)

    def _export_as_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Key", "Value"])
                for k, v in self.metadata_dict.items():
                    writer.writerow([k, v])
            messagebox.showinfo("Export", f"Metadata exported as CSV:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting CSV:\n{e}")

    def _export_as_json(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.metadata_dict, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Export", f"Metadata exported as JSON:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting JSON:\n{e}")

    # -----------------------------
    # Generate HTML report (for bug bounty etc.)
    # -----------------------------
    def generate_report(self):
        if not self.current_file:
            messagebox.showerror("Error", "No file opened.")
            return

        if not self.metadata_dict:
            messagebox.showerror("Error", "No metadata loaded to include in report.")
            return

        report_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
            title="Save Metadata Report"
        )
        if not report_path:
            return

        try:
            esc = html.escape

            # Build table rows
            rows_html = "\n".join(
                f"<tr><td>{esc(str(k))}</td><td>{esc(str(v))}</td></tr>"
                for k, v in self.metadata_dict.items()
            )

            # Normalize path for file://
            img_path = os.path.abspath(self.current_file)
            img_uri = "file:///" + img_path.replace("\\", "/")

            html_content = f"""<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <title>ExifPlus Metadata Report</title> <style> body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f7f7f7; }} h1 {{ color: #333; }} .section {{ margin-bottom: 20px; padding: 15px; background: #ffffff; border-radius: 8px; box-shadow: 0 0 4px rgba(0,0,0,0.08); }} /* SIDE-BY-SIDE LAYOUT */ .content-flex {{ display: flex; gap: 20px; align-items: flex-start; }} .image-container {{ flex: 1; text-align: center; }} .image-container img {{ max-width: 100%; border-radius: 6px; border: 1px solid #ccc; }} .metadata-table {{ flex: 2; }} table {{ border-collapse: collapse; width: 100%; font-size: 13px; }} th, td {{ border: 1px solid #ddd; padding: 6px 8px; text-align: left; vertical-align: top; }} th {{ background-color: #f0f0f0; }} .footer {{ margin-top: 25px; font-size: 12px; color: #777; }} </style> </head> <body> <h1>Metadata Report</h1> <div class="section"> <strong>File:</strong> {esc(img_path)}<br> <p>This report was generated by <strong>ExifPlus</strong>.</p> </div> <!-- SIDE BY SIDE CONTENT --> <div class="section content-flex"> <!-- LEFT: IMAGE --> <div class="image-container"> <h2>Image Preview</h2> <img src='{img_uri}' alt="Image preview"> </div> <!-- RIGHT: METADATA TABLE --> <div class="metadata-table"> <h2>Metadata</h2> <table> <thead> <tr><th>Key</th><th>Value</th></tr> </thead> <tbody> {rows_html} </tbody> </table> </div> </div> <div class="footer"> Generated by ExifPlus — https://pypi.org/project/exifplus/ </div> </body> </html> """
            
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            messagebox.showinfo("Report Generated", f"Report saved to:\n{report_path}")

            # Open report in default browser
            webbrowser.open("file:///" + report_path.replace("\\", "/"))

        except Exception as e:
            messagebox.showerror("Error", f"Error generating report:\n{e}")

    # -----------------------------
    # About Window
    # -----------------------------
    def show_about(self):
        about = tk.Toplevel(self.root)
        about.title("About")
        about.geometry("400x450")

        tb.Label(about, text="Metadata Viewer & Editor", font=("Arial", 14, "bold")).pack(pady=10)
        tb.Label(about, text="Author: Mohammed Zahid Wadiwale").pack()
        tb.Label(about, text="Company: Webaon").pack()
        tb.Label(about, text="Website: webaon.com", bootstyle=INFO).pack(pady=5)
        # Author section
        tb.Label(
            about,
            text="Developed By:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        tb.Label(
            about,
            text="Mohammed Zahid Wadiwale",
            font=("Arial", 12)
        ).pack(pady=2)
        tb.Separator(about, orient="horizontal").pack(fill="x", pady=10)
        # Links section
        tb.Label(
            about,
            text="Official Links",
            font=("Arial", 14, "bold")
        ).pack(pady=5)
        link_style = {"font": ("Arial", 11), "foreground": "blue", "cursor": "hand2"}
        def make_link(label, url):
            widget = tb.Label(about, text=label, **link_style)
            widget.pack()
            widget.bind("<Button-1>", lambda e: subprocess.Popen(["xdg-open", url]))
        make_link("Website: www.webaon.com", "https://www.webaon.com/")
        make_link("GitHub: github.com/ZahidServers", "https://github.com/ZahidServers")
        make_link("Blog: blog.webaon.com", "https://blog.webaon.com/")
        make_link("Academy: academy.webaon.com", "https://academy.webaon.com/")
        tb.Separator(about, orient="horizontal").pack(fill="x", pady=10)

        tb.Button(about, text="OK", bootstyle=PRIMARY,
                  command=about.destroy).pack(pady=15)


def main():
    """Entry point to launch the GUI."""
    root = tb.Window(themename="flatly")
    app = MetadataApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
