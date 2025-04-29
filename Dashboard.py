import customtkinter as ctk
from tkinter import ttk
import os
import sys
import datetime
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
        self.current_view = "students"
        self.latest_table_name = None

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

        self.schedule_check_loop()

    def setup_student_columns(self):
        columns = ("Student No.", "Name", "Course", "Department", "Section", "Time", "Status")
        self.tree.config(columns=columns)

        column_widths = {
            "Student No.": 120,
            "Name": 200,
            "Course": 120,
            "Department": 150,
            "Section": 100,
            "Time": 100,
            "Status": 100
        }

        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, anchor="center", width=column_widths.get(col, 100))

        self.tree.heading("#0", text="Photo", anchor="center")
        self.tree.column("#0", width=120, minwidth=110, anchor="center")

    def setup_schedule_columns(self):
        columns = ("Subject", "Section", "Professor", "Email", "Day", "Time In", "Time Out")
        self.tree.config(columns=columns)

        column_widths = {
            "Subject": 180,
            "Section": 100,
            "Professor": 140,
            "Email": 200,
            "Day": 100,
            "Time In": 100,
            "Time Out": 100
        }

        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, anchor="center", width=column_widths.get(col, 100))

        self.tree.heading("#0", text="", anchor="center")
        self.tree.column("#0", width=0, minwidth=0)

    def load_schedule_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()

            room_code = self.master.room_code

            cursor.execute("""
                SELECT Subject, Section, Professor, ProfessorEmail, Day, TimeIn, TimeOut 
                FROM Schedule 
                WHERE Room = ?
            """, (room_code,))
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
        self.tree.delete(*self.tree.get_children())
        self.setup_student_columns()

        if not self.latest_table_name:
            return

        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()

            cursor.execute(f"SELECT * FROM [{self.latest_table_name}]")
            rows = cursor.fetchall()

            for index, row in enumerate(rows):
                tag = "evenrow" if index % 2 == 0 else "oddrow"
                photo_data = row[7]

                photo = self.convert_blob_to_image(photo_data) if photo_data else None
                self.tree.insert("", "end", values=row[:7], tags=(tag,))

                if photo:
                    self.image_refs.append(photo)
                    self.tree.item(self.tree.get_children()[-1], image=photo)

            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading latest table: {e}")

    def convert_blob_to_image(self, blob_data):
        from io import BytesIO
        from PIL import Image, ImageTk

        try:
            image = Image.open(BytesIO(blob_data))
            image = image.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)

            self.image_refs.append(photo)
            return photo
        except Exception as e:
            print(f"Error converting BLOB to image: {e}")
            return None

    def schedule_check_loop(self):
        self.check_and_generate_table()
        self.after(5000, self.schedule_check_loop)

    def check_and_generate_table(self):
        now = datetime.datetime.now()
        current_day = now.strftime("%A")
        current_time = now.strftime("%I:%M %p")

        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT Subject, Section, Professor, TimeIn, TimeOut
                FROM Schedule
                WHERE Room = ? AND Day = ?
            """, (self.master.room_code, current_day))

            rows = cursor.fetchall()
            created_table_name = None

            for subject, section, professor, time_in, time_out in rows:
                current_dt = datetime.datetime.strptime(current_time, "%I:%M %p")

                time_in_dt = datetime.datetime.strptime(time_in, "%I:%M %p")
                time_out_dt = datetime.datetime.strptime(time_out, "%I:%M %p")

                time_in_diff = (current_dt - time_in_dt).total_seconds() / 60
                time_out_diff = (current_dt - time_out_dt).total_seconds() / 60

                if 0 <= time_in_diff <= 1 and not self.is_timeout_created(current_day, subject, professor, section, time_out):
                    table_name = self.get_table_name(current_day, subject, professor, section, time_in, "TimeIn")
                    if not self.table_exists(table_name, cursor):
                        created_table_name = self.create_attendance_table(current_day, subject, professor, section,
                                                                          time_in, "TimeIn", cursor)
                        print(f"Created TimeIn table: {created_table_name}")

                elif 0 <= time_out_diff <= 1:
                    table_name = self.get_table_name(current_day, subject, professor, section, time_out, "TimeOut")
                    if not self.table_exists(table_name, cursor):
                        created_table_name = self.create_attendance_table(current_day, subject, professor, section,
                                                                          time_out, "TimeOut", cursor)
                        print(f"Created TimeOut table: {created_table_name}")

            if created_table_name:
                self.latest_table_name = created_table_name
                with open(f"latest_table_{self.master.room_code}.txt", "w") as f:
                    f.write(created_table_name)
                self.master.TableHeader.Label1.configure(text=created_table_name)
                if self.current_view != "schedule":
                    self.switch_to_student_view()
            else:
                try:
                    with open(f"latest_table_{self.master.room_code}.txt", "r") as f:
                        last_known_table = f.read().strip()
                        if self.table_exists(last_known_table, cursor):
                            self.latest_table_name = last_known_table
                            self.master.TableHeader.Label1.configure(text=last_known_table)
                            if self.current_view != "schedule":
                                self.switch_to_student_view()
                        else:
                            self.master.TableHeader.Label1.configure(text="No Current Schedule")
                except FileNotFoundError:
                    self.master.TableHeader.Label1.configure(text="No Current Schedule")

            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error checking schedule: {e}")

    def get_table_name(self, day, subject, professor, section, time_str, tag):
        def sanitize(text):
            return text.replace(":", "").replace(" ", "").replace("-", "").replace("@", "").replace(".", "")

        clean_time = datetime.datetime.strptime(time_str.strip(), "%I:%M %p").strftime("%I:%M%p")
        table_name = f"{day}_{subject}_{professor}_{section}_{clean_time}_{tag}"
        return sanitize(table_name)

    def table_exists(self, table_name, cursor):
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return cursor.fetchone() is not None

    def is_timeout_created(self, day, subject, professor, section, time_str):
        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()
            table_name = self.get_table_name(day, subject, professor, section, time_str, "TimeOut")
            result = self.table_exists(table_name, cursor)
            conn.close()
            return result
        except sqlite3.Error:
            return False

    def create_attendance_table(self, day, subject, professor, section, time_str, tag, cursor):
        table_name = self.get_table_name(day, subject, professor, section, time_str, tag)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS [{table_name}] (
                StudentNo TEXT,
                Name TEXT,
                Course TEXT,
                Department TEXT,
                Section TEXT,
                Time TEXT,
                Status TEXT,
                Photo BLOB
            )
        """)

        return table_name

if __name__ == "__main__":
    Dashboard = Dashboard()
    Dashboard.mainloop()