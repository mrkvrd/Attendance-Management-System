import customtkinter as ctk
from tkinter import ttk
import os
import sys
from PIL import Image, ImageTk
import cv2
from tkinter import messagebox
import sqlite3
from sqlite3 import Error

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


class Dashboard(ctk.CTk):
    def __init__(self, room_code):
        super().__init__()

        self.room_code = room_code

        self.window_width = 1080
        self.window_height = 720

        title_text = "Room Login"
        if room_code:
            title_text = f"Room {room_code} - Dashboard"

        self.title(title_text)
        self.iconbitmap("images/icon.ico")
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        self.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.after(100, lambda: self.state("zoomed"))
        self.bind("<Map>", self.on_restore)

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=4)

        self.HeadFrame = HeadFrame(self)
        self.HeadFrame.grid(row=0, column=0, columnspan=2, sticky="nwe")

        self.InfoFrame = InfoFrame(self)
        self.InfoFrame.grid(row=1, column=0, sticky="nswe")

        self.CamFrame = CamFrame(self)
        self.CamFrame.grid(row=1, column=1, sticky="nswe")

        self.TableHeader = TableHeader(self)
        self.TableHeader.grid(row=2, column=0, columnspan=2, sticky="nswe")

        self.TableFrame = TableFrame(self)
        self.TableFrame.grid(row=3, column=0, columnspan=2, sticky="nswe")

    def on_restore(self, event=None):
        if self.state() == "normal":
            position_top = int((self.screen_height - self.window_height) / 2) - 30
            position_left = int((self.screen_width - self.window_width) / 2)
            self.geometry(f"{self.window_width}x{self.window_height}+{position_left}+{position_top}")

class HeadFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure((0,1),weight=1)
        self.grid_columnconfigure((0,1,2),weight=1)
        self.configure(fg_color="#115272", corner_radius=0)

        self.Label1 = ctk.CTkLabel(self, text="Quezon City University - RFID Attendance System", text_color="white", font=("Arial", 25, "bold"))
        self.Label1.grid(row=0, column=1, sticky="nsew",pady=5)
        self.Label2 = ctk.CTkLabel(self, text="San Bartolome Campus", text_color="white", font=("Arial", 15))
        self.Label2.grid(row=1, column=1, sticky="nsew",pady=3)

        self.Qcuimg = ctk.CTkImage(light_image=Image.open("images/img_1.png"), size=(40, 40))
        self.ImageLabel1 = ctk.CTkLabel(self, image=self.Qcuimg, text="")
        self.ImageLabel1.grid(row=0, column=0, rowspan=2, pady=3)
        self.Qcimg = ctk.CTkImage(light_image=Image.open("images/img_2.png"), size=(53, 40))
        self.ImageLabel2 = ctk.CTkLabel(self, image=self.Qcimg, text="")
        self.ImageLabel2.grid(row=0, column=2, rowspan=2, pady=3)

class InfoFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure((0,1,2,4), weight=1)
        self.grid_rowconfigure((0,1,2,3), weight=1)

        self.configure(corner_radius=0, fg_color="#ffffff")

        self.StudentImage = ctk.CTkImage(light_image=Image.open("images/bg.png"), size=(300, 250))
        self.ImageLabel3 = ctk.CTkLabel(self, text="", image=self.StudentImage)
        self.ImageLabel3.grid(row=0, column=0, rowspan=4, sticky="nswe", pady=20)

        self.StudentName = ctk.CTkLabel(self, text="Student Name", font=("Arial", 25, "bold"), pady=20)
        self.StudentName.grid(row=0, column=1, columnspan=2, sticky="nsw")

        self.StudentNoLabel = ctk.CTkLabel(self, text="Student No.:", font=("Arial", 20))
        self.StudentNoLabel.grid(row=1, column=1, sticky="nw")
        self.StudentNoEntry = ctk.CTkLabel(self, text="00-0000", font=("Arial", 20, "bold"), width=300)
        self.StudentNoEntry.grid(row=1, column=2, sticky="new")

        self.StudentProgramLabel = ctk.CTkLabel(self, text="Department:", font=("Arial", 20))
        self.StudentProgramLabel.grid(row=2, column=1, sticky="nw")
        self.StudentProgramEntry = ctk.CTkLabel(self, text="_______", font=("Arial", 20, "bold"))
        self.StudentProgramEntry.grid(row=2, column=2, sticky="new")

        self.StudentSectionLabel = ctk.CTkLabel(self, text="Program:", font=("Arial", 20))
        self.StudentSectionLabel.grid(row=3, column=1, sticky="nw")
        self.StudentSectionEntry = ctk.CTkLabel(self, text="_______", font=("Arial", 20, "bold"))
        self.StudentSectionEntry.grid(row=3, column=2, sticky="new")

class CamFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(corner_radius=0, fg_color="#ffffff")

        self.cap = cv2.VideoCapture(0)

        self.camera_label = ctk.CTkLabel(self, text="Initializing Camera...")
        self.camera_label.pack(expand=True, fill="both")

        self.update_camera()

    def update_camera(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)

            img = img.resize((300, 250))

            self.live_image = ctk.CTkImage(light_image=img, size=(300, 250))

            self.camera_label.configure(image=self.live_image, text="")

        self.after(30, self.update_camera)

    def stop_camera(self):
        self.cap.release()

class TableHeader(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0,1,2), weight=1)
        self.configure(height=60, fg_color="#115272", corner_radius=0)

        self.Label1 = ctk.CTkLabel(self, text_color="#ffffff", text="No Current Schedule", font=("Arial", 15, "bold"))
        self.Label1.grid(row=0, column=0, sticky="w", pady=5, padx=20)

        self.Label2 = ctk.CTkLabel(self, text_color="#ffffff", text="Students Time Table", font=("Arial", 25, "bold"))
        self.Label2.grid(row=0, column=1, sticky="nswe", pady=5)

        self.ComboBox = ctk.CTkComboBox(self, values=["Dashboard", "Early Out", "View Room Schedule", "Logout"], corner_radius=0, border_color="#115272",
                                        button_color="#28A745", button_hover_color="#208637", text_color="#ffffff", fg_color="#115272", justify="right",
                                        dropdown_font=("Arial", 13, "bold"), state="readonly", dropdown_fg_color="#ffffff", font=("Arial", 15, "bold"),
                                        command=self.on_select)
        self.ComboBox.grid(row=0, column=2, sticky="e", pady=5, padx=20)

    def on_select(self, choice):
        if choice == "Logout":
            confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?")
            if confirm:
                self.master.destroy()
                python = sys.executable
                os.execv(python, [python, "RoomLogin.py"])
        elif choice == "Dashboard":
            print("Dashboard selected")
            self.Label2.configure(text="Students Time Table")
            self.master.TableFrame.switch_to_student_view()
        elif choice == "Early Out":
            print("Early Out selected")
        elif choice == "View Room Schedule":
            print("View Room Schedule selected")
            self.Label2.configure(text="Room Schedule")
            self.master.TableFrame.switch_to_schedule_view()

class TableFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.current_view = "students"  # default view

        self.configure(corner_radius=10, fg_color="#f5f5f5")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Treeview",
                        background="#ffffff",
                        foreground="black",
                        rowheight=110,
                        fieldbackground="#f8f8f8",
                        font=("Arial", 14, "bold"))

        style.configure("Treeview.Heading",
                        font=("Arial", 16, "bold"),
                        background="#115272",
                        foreground="white")

        style.map("Treeview.Heading",
                  background=[("active", "#115272"), ("pressed", "#115272")],
                  foreground=[("active", "white"), ("pressed", "white")])

        self.tree = ttk.Treeview(self, show="headings tree", height=8)
        self.setup_student_columns()

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=10)

        self.images = {}
        self.image_refs = []

        self.tree.tag_configure("evenrow", background="#f0f0f0")
        self.tree.tag_configure("oddrow", background="#ffffff")

    def setup_student_columns(self):
        columns = ("Student No.", "Name", "Course", "Department", "Section", "Status")
        self.tree.config(columns=columns)

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, anchor="center")

        self.tree.heading("#0", text="Photo", anchor="center")
        self.tree.column("#0", width=120, minwidth=110, anchor="center")

    def setup_schedule_columns(self):
        columns = ("Subject", "Section", "Professor", "Day", "Time In", "Time Out")
        self.tree.config(columns=columns)

        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, anchor="center")

        self.tree.heading("#0", text="", anchor="center")
        self.tree.column("#0", width=0, minwidth=0)

    def load_schedule_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()

            room_code = self.master.room_code

            cursor.execute("SELECT Subject, Section, Professor, Day, TimeIn, TimeOut FROM Schedule WHERE Room = ?", (room_code,))
            rows = cursor.fetchall()

            for index, row in enumerate(rows):
                tag = "evenrow" if index % 2 == 0 else "oddrow"
                self.tree.insert("", "end", values=row, tags=(tag,))

            conn.close()
        except Error as e:
            messagebox.showerror("Database Error", f"Error connecting to database: {e}")

    def switch_to_schedule_view(self):
        self.current_view = "schedule"

        for row in self.tree.get_children():
            self.tree.delete(row)

        self.setup_schedule_columns()
        self.load_schedule_data()

    def switch_to_student_view(self):
        self.current_view = "students"

        for row in self.tree.get_children():
            self.tree.delete(row)

        self.setup_student_columns()

if __name__ == "__main__":
    Dashboard = Dashboard()
    Dashboard.mainloop()