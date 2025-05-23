import customtkinter as ctk
import tkinter as ttk
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO
import os
import sys
from tkinter import messagebox
from Dashboard import InfoFrame
from Dashboard import TableHeader as OriginalTableHeader
import sqlite3

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.window_width = 1440
        self.window_height = 800
        self.configure(fg_color="#ffffff")

        self.title("Admin")
        self.iconbitmap("images/icon.ico")
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        self.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.after(100, lambda: self.state("zoomed"))
        self.bind("<Map>", self.on_restore)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.HeadFrame = HeadFrame(self)
        self.HeadFrame.grid(row=0, column=0, columnspan=2, sticky="nwe")

        self.MainView = MainView(self)
        self.MainView.grid(row=1, column=1, sticky="nwes")

        self.TabFrame = TabFrame(self, self.MainView)
        self.TabFrame.grid(row=1, column=0, sticky="nws")

    def on_restore(self, event=None):
        if self.state() == "normal":
            position_top = int((self.screen_height - self.window_height) / 2) - 30
            position_left = int((self.screen_width - self.window_width) / 2)
            self.geometry(f"{self.window_width}x{self.window_height}+{position_left}+{position_top}")


class HeadFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.configure(fg_color="#115272", corner_radius=0)

        self.Label1 = ctk.CTkLabel(self, text="Quezon City University - RFID Attendance System", text_color="white",
                                   font=("Arial", 25, "bold"))
        self.Label1.grid(row=0, column=1, sticky="nsew", pady=5)
        self.Label2 = ctk.CTkLabel(self, text="San Bartolome Campus", text_color="white", font=("Arial", 15))
        self.Label2.grid(row=1, column=1, sticky="nsew", pady=3)

        self.Qcuimg = ctk.CTkImage(light_image=Image.open("images/img_1.png"), size=(40, 40))
        self.ImageLabel1 = ctk.CTkLabel(self, image=self.Qcuimg, text="")
        self.ImageLabel1.grid(row=0, column=0, rowspan=2, pady=3)
        self.Qcimg = ctk.CTkImage(light_image=Image.open("images/img_2.png"), size=(53, 40))
        self.ImageLabel2 = ctk.CTkLabel(self, image=self.Qcimg, text="")
        self.ImageLabel2.grid(row=0, column=2, rowspan=2, pady=3)


class TabFrame(ctk.CTkFrame):
    def __init__(self, master, main_view):
        super().__init__(master)
        self.main_view = main_view

        self.configure(fg_color="#115272", corner_radius=0, width=275)
        self.grid_rowconfigure((0, 1, 2, 3), weight=0)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.MainView = main_view
        self.MenuLabel = ctk.CTkLabel(self, fg_color="#45b45d", width=260, height=50, font=("Arial", 20, "bold"),
                                      text_color="#ffffff", text="Menu")
        self.MenuLabel.grid(row=0, column=0, sticky="nwe", pady=15)

        self.RoomsButton = ctk.CTkButton(self, fg_color="#115272", height=50, font=("Arial", 17, "bold"),
                                         text_color="#ffffff", text="Rooms", hover_color="#1a6e98",
                                         command=self.RoomsTab)
        self.RoomsButton.grid(row=1, column=0, sticky="nwe", pady=5)
        self.RegisterButton = ctk.CTkButton(self, fg_color="#115272", height=50, font=("Arial", 17, "bold"),
                                            text_color="#ffffff", text="Student Register", hover_color="#1a6e98",
                                            command=self.StudentTab)
        self.RegisterButton.grid(row=2, column=0, sticky="nwe", pady=5)
        self.ScheduleButton = ctk.CTkButton(self, fg_color="#115272", height=50, font=("Arial", 17, "bold"),
                                            text_color="#ffffff", text="Schedule", hover_color="#1a6e98",
                                            command=self.ScheduleTab)
        self.ScheduleButton.grid(row=3, column=0, sticky="nwe", pady=5)

        self.LogoutButton = ctk.CTkButton(self, fg_color="#115272", height=50, font=("Arial", 15, "bold"),
                                          text_color="#ffffff", text="Logout", hover_color="#1a6e98",
                                          command=self.Logout)
        self.LogoutButton.grid(row=4, column=0, sticky="swe")

    def RoomsTab(self):
        self.main_view.set("Rooms")

    def StudentTab(self):
        self.main_view.set("Student Register")

    def ScheduleTab(self):
        self.main_view.set("Schedule")

    def Logout(self):
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?")
        if confirm:
            self.master.destroy()
            import AdminLogin
            AdminLogin.Login().mainloop()

class TableHeader(OriginalTableHeader):
    def __init__(self, master, table_frame):
        super().__init__(master)

        self.table_frame = table_frame

        self.ComboBox.destroy()
        self.ComboBox = ctk.CTkComboBox(self,
                                        values=["Dashboard", "View Room Schedule"],
                                        corner_radius=0,
                                        border_color="#115272",
                                        button_color="#28A745",
                                        button_hover_color="#208637",
                                        text_color="#ffffff",
                                        fg_color="#115272",
                                        justify="right",
                                        dropdown_font=("Arial", 13, "bold"),
                                        state="readonly",
                                        dropdown_fg_color="#ffffff",
                                        font=("Arial", 15, "bold"),
                                        command=self.on_table_select)
        self.ComboBox.grid(row=0, column=2, sticky="e", pady=5, padx=20)
        self.ComboBox.set("Dashboard")

    def on_table_select(self, choice):
        if choice == "Dashboard":
            self.Label2.configure(text="Students Time Table")
            self.table_frame.switch_to_student_view()
        elif choice == "View Room Schedule":
            self.Label2.configure(text="Room Schedule")
            self.table_frame.switch_to_schedule_view()

class MainView(ctk.CTkTabview):
    def __init__(self, master):
        super().__init__(master)

        self.add("Rooms")
        self.add("Student Register")
        self.add("Schedule")

        self.configure(fg_color="#ffffff", corner_radius=0)
        self._segmented_button.grid_forget()

        self.setup_rooms_tab()

        self.setup_student_register_tab()

        self.setup_schedule_tab()

    def setup_rooms_tab(self):
        self.room_tab = self.tab("Rooms")
        self.room_tab.grid_columnconfigure((0, 1), weight=1)
        self.room_tab.grid_rowconfigure(0, weight=0)
        self.room_tab.grid_rowconfigure(1, weight=0)
        self.room_tab.grid_rowconfigure(2, weight=3)

        self.dropdown_frame = ctk.CTkFrame(self.room_tab, fg_color="transparent")
        self.dropdown_frame.grid(row=0, column=1, sticky="news")
        self.dropdown_frame.grid_columnconfigure(0, weight=1)
        self.dropdown_frame.grid_rowconfigure((0, 1), weight=1)

        self.room_label = ctk.CTkLabel(
            self.dropdown_frame,
            text="Select Room:",
            font=("Arial", 18, "bold"),
            text_color="#115272"
        )
        self.room_label.grid(row=0, column=0, sticky="s", pady=(0, 5))

        self.dropdown = ctk.CTkComboBox(
            self.dropdown_frame,
            button_color="#28A745",
            button_hover_color="#208637",
            justify="center",
            state="readonly",
            dropdown_fg_color="#ffffff",
            font=("Arial", 18, "bold"),
            text_color="#115272",
            dropdown_font=("Arial", 15, "bold"),
            corner_radius=0,
            width=300,
            height=35,
            border_color="#115272",
            command=self.on_room_selected
        )
        self.dropdown.grid(row=1, column=0, sticky="n", pady=(5, 0))

        self.info_frame = InfoFrame(self.room_tab)
        self.info_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.table_frame = RoomTableFrame(self.room_tab, table_header=None)
        self.table_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.table_header = TableHeader(self.room_tab, self.table_frame)
        self.table_header.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10)
        self.table_frame.table_header = self.table_header

        self.load_room_ids()

    def on_room_selected(self, room_code):
        self.table_frame.current_room_code = room_code
        self.table_frame.load_latest_table_name()
        self.table_frame.switch_to_student_view()
        self.table_frame.reload_data()

        latest_table = self.table_frame.latest_table_name
        if latest_table:
            try:
                conn = sqlite3.connect("AMS.db")
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT Name, StudentNo, Department, Course, Photo 
                    FROM [{latest_table}] 
                    ORDER BY ROWID DESC LIMIT 1
                """)
                latest = cursor.fetchone()
                conn.close()

                if latest:
                    name, student_no, department, course, photo = latest
                    self.info_frame.update_student_info(name, student_no, department, course)
                    self.info_frame.update_student_photo(photo)
                else:
                    self.info_frame.update_student_info("Student Name", "00-0000", "_______", "_______")
                    self.info_frame.update_student_photo(None)
            except sqlite3.Error as e:
                print(f"Failed to load latest student info: {e}")
        else:
            self.info_frame.update_student_info("Student Name", "00-0000", "_______", "_______")
            self.info_frame.update_student_photo(None)

    def setup_student_register_tab(self):
        self.Reg_tab = self.tab("Student Register")
        self.Reg_tab.grid_columnconfigure(0, weight=1)
        self.Reg_tab.grid_rowconfigure(0, weight=0)
        self.Reg_tab.grid_rowconfigure(1, weight=1)

        self.AddStudentFrame = AddStudentFrame(self.Reg_tab)
        self.AddStudentFrame.grid(row=0, column=0, sticky="nsew")

        self.StudentTableFrame = StudentTableFrame(self.Reg_tab)
        self.StudentTableFrame.grid(row=1, column=0, sticky="nsew")

    def setup_schedule_tab(self):
        self.Sched_tab = self.tab("Schedule")
        self.Sched_tab.grid_columnconfigure(0, weight=1)
        self.Sched_tab.grid_rowconfigure(0, weight=0)
        self.Sched_tab.grid_rowconfigure(1, weight=1)

        self.SchedTableFrame = SchedTableFrame(self.Sched_tab)
        self.SchedTableFrame.grid(row=1, column=0, sticky="nsew")

        self.AddSchedFrame = AddScheduleFrame(self.Sched_tab, self.SchedTableFrame)
        self.AddSchedFrame.grid(row=0, column=0, sticky="nsew")

        self.SchedTableFrame.grid_columnconfigure(0, weight=1)
        self.SchedTableFrame.grid_rowconfigure(0, weight=1)

    def load_room_ids(self):
        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()
            cursor.execute("SELECT RoomCode FROM Rooms")
            room_ids = [str(row[0]) for row in cursor.fetchall()]
            self.dropdown.configure(values=room_ids)
            if room_ids:
                self.dropdown.set(room_ids[0])
                self.on_room_selected(room_ids[0])
            conn.close()
        except sqlite3.Error as e:
            print("Database error:", e)


class RoomTableFrame(ctk.CTkFrame):
    def __init__(self, master, table_header=None):
        super().__init__(master)

        self.table_header = table_header

        self.configure(corner_radius=10, fg_color="#f5f5f5")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.current_room_code = None
        self.current_view = "students"

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="black",
                        rowheight=100,
                        fieldbackground="#f8f8f8",
                        font=("Arial", 12, "bold"))
        style.configure("Treeview.Heading",
                        font=("Arial", 14, "bold"),
                        background="#115272",
                        foreground="white")
        style.map("Treeview.Heading",
                  background=[("active", "#115272"), ("pressed", "#115272")],
                  foreground=[("active", "white"), ("pressed", "white")])

        self.tree = ttk.Treeview(self, show="headings", height=15)

        self.setup_student_columns()

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=10)

        self.tree.tag_configure("evenrow", background="#f0f0f0")
        self.tree.tag_configure("oddrow", background="#ffffff")

        self.photo_refs = []

        self.latest_table_name = None
        self.schedule_check_loop()

    def setup_student_columns(self):
        columns = ("Student No.", "Name", "Course", "Department", "Section", "Time", "Status")
        self.tree.config(columns=columns, show="headings tree")

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
            self.tree.column(col, anchor="center", width=column_widths.get(col, 100), stretch=True)

        self.tree.heading("#0", text="Photo", anchor="center")
        self.tree.column("#0", width=120, minwidth=110, anchor="center")

    def setup_schedule_columns(self):
        columns = ("Subject", "Section", "Professor", "Email", "Day", "Time In", "Time Out")
        self.tree.config(columns=columns, show="headings")

        column_widths = {
            "Subject": 200,
            "Section": 120,
            "Professor": 150,
            "Email": 180,
            "Day": 100,
            "Time In": 100,
            "Time Out": 100
        }

        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, anchor="center", width=column_widths.get(col, 100), stretch=True)

    def load_latest_table_name(self):
        if not self.current_room_code:
            return

        try:
            with open(f"latest_table_{self.current_room_code}.txt", "r") as f:
                self.latest_table_name = f.read().strip()
        except FileNotFoundError:
            self.latest_table_name = None
            print(f"No latest table found for room {self.current_room_code}")

    def switch_to_student_view(self):
        self.current_view = "students"
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tree.configure(show="headings tree")
        self.setup_student_columns()
        self.reload_data()

    def switch_to_schedule_view(self):
        self.current_view = "schedule"
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.setup_schedule_columns()
        self.reload_data()

    def reload_data(self):
        if not self.current_room_code:
            return

        if self.current_view == "students":
            self.load_student_data()
        else:
            self.load_schedule_data()

    def schedule_check_loop(self):
        self.check_and_generate_table()
        self.after(5000, self.schedule_check_loop)

    def check_and_generate_table(self):
        if not self.current_room_code:
            return

        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()

            try:
                with open(f"latest_table_{self.current_room_code}.txt", "r") as f:
                    last_known_table = f.read().strip()
                    if self.table_exists(last_known_table, cursor):
                        self.latest_table_name = last_known_table
                        if self.table_header:
                            self.table_header.Label1.configure(text=self.latest_table_name)
                        if self.current_view == "students":
                            self.load_student_data()
                    else:
                        self.latest_table_name = None
                        if self.table_header:
                            self.table_header.Label1.configure(text="No Current Schedule")
            except FileNotFoundError:
                self.latest_table_name = None
                if self.table_header:
                    self.table_header.Label1.configure(text="No Current Schedule")

            conn.close()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def table_exists(self, table_name, cursor):
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return cursor.fetchone() is not None

    def load_student_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.latest_table_name:
            print("No latest table name available")
            return

        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.latest_table_name,))
            if not cursor.fetchone():
                print(f"Table {self.latest_table_name} doesn't exist")
                return

            cursor.execute(f"""
                SELECT StudentNo, Name, Course, Department, Section, Time, Status, Photo 
                FROM [{self.latest_table_name}]
                ORDER BY Time DESC
            """)

            rows = cursor.fetchall()

            for index, row in enumerate(rows):
                tag = "evenrow" if index % 2 == 0 else "oddrow"
                photo_blob = row[7]

                if photo_blob:
                    try:
                        image = Image.open(BytesIO(photo_blob))
                        image = image.resize((100, 100), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(image)
                        self.photo_refs.append(photo)
                        self.tree.insert("", "end", image=photo, values=row[:7], tags=(tag,))
                    except Exception as e:
                        print(f"Error loading photo: {e}")
                        self.tree.insert("", "end", values=row[:7], tags=(tag,))
                else:
                    self.tree.insert("", "end", values=row[:7], tags=(tag,))

            conn.close()

        except sqlite3.Error as e:
            print(f"Database error in load_student_data: {e}")

    def load_schedule_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT Subject, Section, Professor, ProfessorEmail, Day, TimeIn, TimeOut 
                FROM Schedule 
                WHERE Room = ?
            """, (self.current_room_code,))

            rows = cursor.fetchall()

            for index, row in enumerate(rows):
                tag = "evenrow" if index % 2 == 0 else "oddrow"
                self.tree.insert("", "end", values=row, tags=(tag,))

            conn.close()

        except sqlite3.Error as e:
            print(f"Database error: {e}")


class AddStudentFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.conn = sqlite3.connect('AMS.db')
        self.cursor = self.conn.cursor()

        self.create_table_if_not_exists()

        self.configure(fg_color="#ffffff", height=300)
        self.grid_propagate(False)
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        self.StudNo_label = ctk.CTkLabel(self, text="Student No.", font=("Arial", 15, "bold"), text_color="#545454")
        self.StudNo_label.grid(row=1, column=0, padx=40, sticky="sw")
        self.StudNo_entry = ctk.CTkEntry(self, width=300, height=40, corner_radius=0,
                                         placeholder_text="Enter Student Number", font=("Arial", 15, "bold"))
        self.StudNo_entry.grid(row=2, column=0, padx=40, sticky="nw")

        self.Course_label = ctk.CTkLabel(self, text="Course", font=("Arial", 15, "bold"), text_color="#545454")
        self.Course_label.grid(row=1, column=1, padx=40, sticky="sw")
        self.Course_dropdown = ctk.CTkComboBox(self, width=300, height=40, corner_radius=0, font=("Arial", 15, "bold"),
                                               justify="center",
                                               dropdown_fg_color="#ffffff", dropdown_font=("Arial", 15, "bold"),
                                               state="readonly",
                                               values=["BSIT", "BSIS", "BSCS", "BSMA", "BSA", "BSENT", "BSIE", "BSCpE",
                                                       "BSEcE", "BSED"])
        self.Course_dropdown.set("Select Course")
        self.Course_dropdown.grid(row=2, column=1, padx=40, sticky="nw")

        self.Dept_label = ctk.CTkLabel(self, text="Department", font=("Arial", 15, "bold"), text_color="#545454")
        self.Dept_label.grid(row=1, column=2, padx=40, sticky="sw")
        self.Dept_dropdown = ctk.CTkComboBox(self, width=300, height=40, corner_radius=0, font=("Arial", 15, "bold"),
                                             justify="center",
                                             dropdown_fg_color="#ffffff", dropdown_font=("Arial", 15, "bold"),
                                             state="readonly",
                                             values=["CCS", "CBAA", "COE", "CE"])
        self.Dept_dropdown.set("Select Department")
        self.Dept_dropdown.grid(row=2, column=2, padx=40, sticky="nw")

        self.StudentName_label = ctk.CTkLabel(self, text="Student Name (LN,FN,MN)",
                                              font=("Arial", 15, "bold"), text_color="#545454")
        self.StudentName_label.grid(row=3, column=0, padx=40, sticky="sw")
        self.LName_entry = ctk.CTkEntry(self, width=300, height=40, corner_radius=0, placeholder_text="Enter Last Name",
                                        font=("Arial", 15, "bold"))
        self.LName_entry.grid(row=4, column=0, padx=40, sticky="nw")

        self.FName_entry = ctk.CTkEntry(self, width=300, height=40, corner_radius=0,
                                        placeholder_text="Enter First Name", font=("Arial", 15, "bold"))
        self.FName_entry.grid(row=4, column=1, padx=40, sticky="nw")

        self.MName_entry = ctk.CTkEntry(self, width=300, height=40, corner_radius=0,
                                        placeholder_text="Enter Middle Name", font=("Arial", 15, "bold"))
        self.MName_entry.grid(row=4, column=2, padx=40, sticky="nw")

        self.rfid_label = ctk.CTkLabel(self, text="Student RFID", font=("Arial", 15, "bold"), text_color="#545454")
        self.rfid_label.grid(row=5, column=0, padx=40, sticky="sw")
        self.rfid_entry = ctk.CTkEntry(self, width=300, font=("Arial", 15, "bold"), state="readonly", height=40,
                                       corner_radius=0, )
        self.rfid_entry.grid(row=6, column=0, padx=40, sticky="nw")

        self.Save_student = ctk.CTkButton(self, width=300, height=50, font=("Arial", 15, "bold"), text_color="#ffffff",
                                          fg_color="#45b45d", hover_color="#308042", corner_radius=0,
                                          text="Save Student",
                                          command=self.save_student_to_db)
        self.Save_student.grid(row=6, column=1, padx=40, sticky="nw")

        self.create_regform_widgets()
        self.setup_serial_connection()

    def create_table_if_not_exists(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Students (
                StudentID TEXT PRIMARY KEY,
                StudentNo TEXT UNIQUE NOT NULL,
                LastName TEXT NOT NULL,
                FirstName TEXT NOT NULL,
                MiddleName TEXT,
                Course TEXT NOT NULL,
                Department TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def create_regform_widgets(self):
        self.Sched_tab_Head = ctk.CTkLabel(self,
                                           text="REGISTER A STUDENT",
                                           font=("Arial", 25, "bold", "underline"),
                                           text_color="#545454")
        self.Sched_tab_Head.grid(row=0, column=0, columnspan=2, padx=30, sticky="nw")

    def save_student_to_db(self):
        student_id = self.rfid_entry.get()
        student_no = self.StudNo_entry.get()
        last_name = self.LName_entry.get()
        first_name = self.FName_entry.get()
        middle_name = self.MName_entry.get()
        course = self.Course_dropdown.get()
        department = self.Dept_dropdown.get()

        if not all([student_id, student_no, last_name, first_name, course != "Select Course",
                    department != "Select Department"]):
            messagebox.showwarning("Warning", "Please fill in all required fields before saving.")
            return

        try:
            self.cursor.execute('''
                INSERT INTO Students (StudentID, StudentNo, LastName, FirstName, MiddleName, Course, Department)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (student_id, student_no, last_name, first_name, middle_name, course, department))
            self.conn.commit()
            messagebox.showinfo("Success", "Student saved successfully!")
            self.clear_entries()

            for widget in self.master.winfo_children():
                if isinstance(widget, StudentTableFrame):
                    widget.load_data()
                    break

        except sqlite3.IntegrityError as e:
            if "StudentID" in str(e):
                messagebox.showerror("Error", "Student ID (RFID) already exists!")
            elif "StudentNo" in str(e):
                messagebox.showerror("Error", "Student Number already exists!")
            else:
                messagebox.showerror("Error", f"Database integrity error: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def clear_entries(self):
        self.StudNo_entry.delete(0, "end")
        self.LName_entry.delete(0, "end")
        self.FName_entry.delete(0, "end")
        self.MName_entry.delete(0, "end")
        self.rfid_entry.configure(state="normal")
        self.rfid_entry.delete(0, "end")
        self.rfid_entry.configure(state="readonly")
        self.Course_dropdown.set("Select Course")
        self.Dept_dropdown.set("Select Department")

    def setup_serial_connection(self):
        try:
            import serial
            self.arduino = serial.Serial('COM3', 9600, timeout=0.1)
            self.check_rfid()
        except Exception as e:
            print(f"Error connecting to Arduino: {e}")
            messagebox.showerror("Connection Error", f"Could not connect to Arduino on COM3: {e}")

    def check_rfid(self):
        try:
            if hasattr(self, 'arduino') and self.arduino.isOpen():
                if self.arduino.in_waiting:
                    rfid_data = self.arduino.readline().decode('utf-8').strip()
                    if rfid_data:
                        self.rfid_entry.configure(state="normal")
                        self.rfid_entry.delete(0, "end")
                        self.rfid_entry.insert(0, rfid_data)
                        self.rfid_entry.configure(state="readonly")
        except Exception as e:
            print(f"Error reading RFID: {e}")

        self.after(100, self.check_rfid)


class StudentTableFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(fg_color="#ffffff")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="black",
                        rowheight=100,
                        fieldbackground="#f8f8f8",
                        font=("Arial", 12, "bold"))
        style.configure("Treeview.Heading",
                        font=("Arial", 14, "bold"),
                        background="#115272",
                        foreground="white")
        style.map("Treeview.Heading",
                  background=[("active", "#115272"), ("pressed", "#115272")],
                  foreground=[("active", "white"), ("pressed", "white")])

        columns = ("Student ID", "Student No.", "Last Name", "First Name", "Middle Name", "Course", "Department", "Action")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)

        # Enable column header sorting for student table
        for col in columns:
            if col != "Action":
                self.tree.heading(col, text=col, anchor="center", command=lambda _col=col: self.sort_treeview_by_column(_col))
            else:
                self.tree.heading(col, text=col, anchor="center")

        self.tree.bind("<Button-1>", self.on_treeview_click)

        col_widths = {
            "Student ID": 150,
            "Student No.": 120,
            "Last Name": 150,
            "First Name": 150,
            "Middle Name": 120,
            "Course": 100,
            "Department": 120,
            "Action": 150
        }

        for col in columns:
            self.tree.column(col, width=col_widths[col], anchor="center")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.search_frame = ctk.CTkFrame(self, fg_color="#f5f5f5")
        self.search_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.search_label = ctk.CTkLabel(self.search_frame, text="Search:", font=("Arial", 12, "bold"))
        self.search_label.grid(row=0, column=0, padx=5, pady=5)

        self.search_entry = ctk.CTkEntry(self.search_frame, width=200, font=("Arial", 12), corner_radius=5)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)

        self.search_button = ctk.CTkButton(self.search_frame, text="Search",
                                           font=("Arial", 12, "bold"),
                                           fg_color="#115272", hover_color="#1a6e98",
                                           corner_radius=5, height=30,
                                           command=self.search_students)
        self.search_button.grid(row=0, column=2, padx=5, pady=5)

        self.refresh_button = ctk.CTkButton(self.search_frame, text="Refresh",
                                            font=("Arial", 12, "bold"),
                                            fg_color="#28A745", hover_color="#208637",
                                            corner_radius=5, height=30,
                                            command=self.load_data)
        self.refresh_button.grid(row=0, column=3, padx=5, pady=5)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=10)

        self.tree.tag_configure("evenrow", background="#f0f0f0")
        self.tree.tag_configure("oddrow", background="#ffffff")

        self.load_data()

    def auto_refresh(self):

        self.load_data()

        self.after(5000, self.auto_refresh)

    def load_data(self):
        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT StudentID, StudentNo, LastName, FirstName, MiddleName, Course, Department FROM Students
            """)
            rows = cursor.fetchall()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for index, row in enumerate(rows):
                tag = "evenrow" if index % 2 == 0 else "oddrow"

                values = list(row) + ["Edit | Delete"]
                self.tree.insert("", "end", values=values, tags=(tag,))

            conn.close()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def on_treeview_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)

            if column == "#8":
                x, y, width, height = self.tree.bbox(item, column)
                if event.x > x + width / 2:
                    self.delete_student(item)
                else:
                    self.edit_student(item)

    def edit_student(self, item):
        values = self.tree.item(item, "values")
        student_id = values[0]

        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Edit Student")
        edit_window.geometry("250x530")
        edit_window.grab_set()
        edit_window.configure(fg_color="#ffffff")

        ctk.CTkLabel(edit_window, text="Edit Student Information", font=("Arial", 16, "bold")).pack(pady=10)

        ctk.CTkLabel(edit_window, text="Student No:").pack()
        stud_no_entry = ctk.CTkEntry(edit_window)
        stud_no_entry.insert(0, values[1])
        stud_no_entry.pack(pady=5)

        ctk.CTkLabel(edit_window, text="Last Name:").pack()
        lname_entry = ctk.CTkEntry(edit_window)
        lname_entry.insert(0, values[2])
        lname_entry.pack(pady=5)

        ctk.CTkLabel(edit_window, text="First Name:").pack()
        fname_entry = ctk.CTkEntry(edit_window)
        fname_entry.insert(0, values[3])
        fname_entry.pack(pady=5)

        ctk.CTkLabel(edit_window, text="Middle Name:").pack()
        mname_entry = ctk.CTkEntry(edit_window)
        mname_entry.insert(0, values[4] if values[4] else "")
        mname_entry.pack(pady=5)

        ctk.CTkLabel(edit_window, text="Course:").pack()
        course_dropdown = ctk.CTkComboBox(edit_window,
                                          values=["BSIT", "BSIS", "BSCS", "BSMA", "BSA", "BSENT", "BSIE", "BSCpE",
                                                  "BSEcE", "BSED"])
        course_dropdown.set(values[5])
        course_dropdown.pack(pady=5)

        ctk.CTkLabel(edit_window, text="Department:").pack()
        dept_dropdown = ctk.CTkComboBox(edit_window,
                                        values=["CCS", "CBAA", "COE", "CE"])
        dept_dropdown.set(values[6])
        dept_dropdown.pack(pady=5)

        def save_changes():
            try:
                conn = sqlite3.connect("AMS.db")
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE Students SET 
                    StudentNo = ?,
                    LastName = ?,
                    FirstName = ?,
                    MiddleName = ?,
                    Course = ?,
                    Department = ?
                    WHERE StudentID = ?
                """, (
                    stud_no_entry.get(),
                    lname_entry.get(),
                    fname_entry.get(),
                    mname_entry.get(),
                    course_dropdown.get(),
                    dept_dropdown.get(),
                    student_id
                ))
                conn.commit()
                conn.close()

                messagebox.showinfo("Success", "Student updated successfully!")
                edit_window.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update student: {e}")

        ctk.CTkButton(edit_window, text="Save Changes", command=save_changes, fg_color="#45b45d", hover_color="#308042", corner_radius=0).pack(pady=20)

    def sort_treeview_by_column(self, column):
        if column == "Action":
            return  # Don't sort the Action column

        # Toggle sort order if the same column is clicked again
        if getattr(self, "_last_sort_col", None) == column:
            self._last_sort_reverse = not getattr(self, "_last_sort_reverse", False)
        else:
            self._last_sort_reverse = False
        self._last_sort_col = column

        column_index = self.tree["columns"].index(column)
        items = []
        for item in self.tree.get_children(""):
            values = self.tree.item(item, "values")
            value = values[column_index]

            # Numeric sort for Student ID and Student No.
            if column in ("Student ID", "Student No."):
                try:
                    sort_value = int(value)
                except Exception:
                    sort_value = value
            else:
                sort_value = value.lower() if isinstance(value, str) else value

            items.append((sort_value, item, values))

        items.sort(reverse=self._last_sort_reverse)

        for item in self.tree.get_children(""):
            self.tree.delete(item)

        for index, (_, item, values) in enumerate(items):
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=values, tags=(tag,))

    def search_students(self):
        search_term = self.search_entry.get().strip().lower()
        if not search_term:
            messagebox.showinfo("Search", "Please enter a search term")
            return

        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT StudentID, StudentNo, LastName, FirstName, MiddleName, Course, Department
                FROM Students
                WHERE LOWER(StudentID) LIKE ? OR LOWER(StudentNo) LIKE ? OR 
                LOWER(LastName) LIKE ? OR LOWER(FirstName) LIKE ? OR
                LOWER(Course) LIKE ? OR LOWER(Department) LIKE ?
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%",
                  f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))

            rows = cursor.fetchall()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for index, row in enumerate(rows):
                tag = "evenrow" if index % 2 == 0 else "oddrow"

                values = list(row) + ["Archive | Delete"]
                self.tree.insert("", "end", values=values, tags=(tag,))

            conn.close()

            if not rows:
                messagebox.showinfo("Search Results", "No matching students found")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            messagebox.showerror("Database Error", f"An error occurred during search: {e}")

    def delete_student(self, item):
        values = self.tree.item(item, "values")
        student_id = values[0]
        student_name = values[2]

        confirm = messagebox.askyesno("Confirm Delete",
                                      f"Are you sure you want to delete this student?\n\nID: {student_id}\nName: {student_name}")
        if confirm:
            try:
                conn = sqlite3.connect("AMS.db")
                cursor = conn.cursor()

                cursor.execute("DELETE FROM Students WHERE StudentID = ?", (student_id,))
                conn.commit()
                conn.close()

                self.tree.delete(item)
                messagebox.showinfo("Success", "Student deleted successfully!")

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred while deleting: {e}")
        else:
            print("Delete operation cancelled")


class AddScheduleFrame(ctk.CTkFrame):
    def __init__(self, master, table_frame):
        super().__init__(master)

        self.table_frame = table_frame
        self.configure(fg_color="#ffffff", height=300)
        self.grid_propagate(False)
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self.create_widgets()
        self.load_room_ids()

    def create_widgets(self):
        self.Sched_tab_Head = ctk.CTkLabel(self,
                                           text="ADD CLASS SCHEDULE",
                                           font=("Arial", 25, "bold", "underline"),
                                           text_color="#545454")
        self.Sched_tab_Head.grid(row=0, column=0, columnspan=2, sticky="nw", padx=30)

        self.Subject_Entry = self.create_entry("Enter Subject Code", 1, 0)
        self.Section_Entry = self.create_entry("Enter Section", 1, 1)
        self.Professor_Entry = self.create_entry("Enter Subject Professor", 1, 2)

        self.Email_Entry = self.create_entry("Enter Professor's Email", 3, 1, sticky="nw")

        self.Day_Dropdown = self.create_day_dropdown(2, 0)

        times = [f"{hour % 12 or 12}:00 {'AM' if hour < 12 else 'PM'}" for hour in range(7, 22)]
        self.Time_in = self.create_time_dropdown("Time In", times, 2, 1)
        self.Time_out = self.create_time_dropdown("Time Out", times, 2, 2)

        self.Room_Dropdown = self.create_room_dropdown(3, 0)
        self.SaveSched_Button = self.create_save_button(3, 2)

    def create_entry(self, placeholder, row, column, sticky="nw", pady=0):
        entry = ctk.CTkEntry(self,
                             width=300,
                             height=40,
                             corner_radius=0,
                             placeholder_text=placeholder,
                             font=("Arial", 15, "bold"))
        entry.grid(row=row, column=column, sticky=sticky, padx=40, pady=pady)
        return entry

    def create_day_dropdown(self, row, column):
        dropdown = ctk.CTkComboBox(self,
                                   width=300,
                                   height=40,
                                   corner_radius=0,
                                   font=("Arial", 15, "bold"),
                                   justify="center",
                                   dropdown_fg_color="#ffffff",
                                   dropdown_font=("Arial", 15, "bold"),
                                   state="readonly",
                                   values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
        dropdown.set("Day")
        dropdown.grid(row=row, column=column, sticky="nw", padx=40)
        return dropdown

    def create_time_dropdown(self, default_text, values, row, column):
        dropdown = ctk.CTkComboBox(self,
                                   width=300,
                                   height=40,
                                   corner_radius=0,
                                   font=("Arial", 15, "bold"),
                                   justify="center",
                                   dropdown_fg_color="#ffffff",
                                   dropdown_font=("Arial", 15, "bold"),
                                   state="readonly",
                                   values=values)
        dropdown.set(default_text)
        dropdown.grid(row=row, column=column, sticky="nw", padx=40)
        return dropdown

    def create_room_dropdown(self, row, column):
        dropdown = ctk.CTkComboBox(self,
                                   width=300,
                                   height=40,
                                   corner_radius=0,
                                   font=("Arial", 15, "bold"),
                                   justify="center",
                                   dropdown_fg_color="#ffffff",
                                   dropdown_font=("Arial", 15, "bold"),
                                   state="readonly")
        dropdown.set("Room")
        dropdown.grid(row=row, column=column, sticky="nw", padx=40)
        return dropdown

    def create_save_button(self, row, column):
        button = ctk.CTkButton(self,
                               width=300,
                               height=50,
                               font=("Arial", 15, "bold"),
                               text_color="#ffffff",
                               fg_color="#45b45d",
                               hover_color="#308042",
                               corner_radius=0,
                               text="Save Schedule",
                               command=self.save_schedule)
        button.grid(row=row, column=column, sticky="nw", padx=40)
        return button

    def load_room_ids(self):
        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()
            cursor.execute("SELECT RoomCode FROM Rooms")
            room_ids = [str(row[0]) for row in cursor.fetchall()]
            self.Room_Dropdown.configure(values=room_ids)
            conn.close()
        except sqlite3.Error as e:
            print("Database error:", e)

    def save_schedule(self):
        subject = self.Subject_Entry.get()
        section = self.Section_Entry.get()
        professor = self.Professor_Entry.get()
        professor_email = self.Email_Entry.get()
        day = self.Day_Dropdown.get()
        time_in = self.Time_in.get()
        time_out = self.Time_out.get()
        room = self.Room_Dropdown.get()

        if not all([subject, section, professor,
                    professor_email]) or day == "Day" or time_in == "Time In" or time_out == "Time Out" or room == "Room":
            messagebox.showwarning("Warning", "Please fill in all fields before saving.")
            return

        if "@" not in professor_email or "." not in professor_email:
            messagebox.showwarning("Warning", "Please enter a valid email address.")
            return

        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()

            cursor.execute("PRAGMA table_info(Schedule)")
            columns = [column[1] for column in cursor.fetchall()]

            if not columns:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Schedule (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Subject TEXT,
                        Section TEXT,
                        Professor TEXT,
                        ProfessorEmail TEXT,
                        Day TEXT,
                        TimeIn TEXT,
                        TimeOut TEXT,
                        Room TEXT
                    )
                """)
            elif "id" not in columns:
                cursor.execute("ALTER TABLE Schedule ADD COLUMN id INTEGER PRIMARY KEY AUTOINCREMENT")

            if "ProfessorEmail" not in columns:
                cursor.execute("ALTER TABLE Schedule ADD COLUMN ProfessorEmail TEXT")

            cursor.execute("""
                INSERT INTO Schedule (Subject, Section, Professor, ProfessorEmail, Day, TimeIn, TimeOut, Room)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (subject, section, professor, professor_email, day, time_in, time_out, room))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Schedule saved successfully!")
            self.clear_form()
            self.table_frame.load_data()

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Selected Room does not exist in Rooms table.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def clear_form(self):
        self.Subject_Entry.delete(0, "end")
        self.Section_Entry.delete(0, "end")
        self.Professor_Entry.delete(0, "end")
        self.Email_Entry.delete(0, "end")
        self.Day_Dropdown.set("Day")
        self.Time_in.set("Time In")
        self.Time_out.set("Time Out")
        self.Room_Dropdown.set("Room")


class SchedTableFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(corner_radius=10, fg_color="#f5f5f5")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="black",
                        rowheight=100,
                        fieldbackground="#f8f8f8",
                        font=("Arial", 12, "bold"))
        style.configure("Treeview.Heading",
                        font=("Arial", 14, "bold"),
                        background="#115272",
                        foreground="white")
        style.map("Treeview.Heading",
                  background=[("active", "#115272"), ("pressed", "#115272")],
                  foreground=[("active", "white"), ("pressed", "white")])

        self.columns = ("id", "Subject", "Section", "Professor", "Email", "Day", "Time In", "Time Out", "Room", "Action")
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings", height=15)
        self.tree.column("id", width=0, stretch=False)

        self.tree.bind("<Button-1>", self.on_treeview_click)

        visible_columns = ("Subject", "Section", "Professor", "Email", "Day", "Time In", "Time Out", "Room", "Action")

        col_widths = {
            "Subject": 120, "Section": 80, "Professor": 120, "Email": 180,
            "Day": 80, "Time In": 80, "Time Out": 80,
            "Room": 80, "Action": 120
        }

        for col in visible_columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=col_widths.get(col, 100), anchor="center")

            if col != "Action":
                self.tree.heading(col, command=lambda _col=col: self.sort_treeview_by_column(_col))

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=10)

        self.tree.tag_configure("evenrow", background="#f0f0f0")
        self.tree.tag_configure("oddrow", background="#ffffff")

        self.day_order = {
            "Monday": 1,
            "Tuesday": 2,
            "Wednesday": 3,
            "Thursday": 4,
            "Friday": 5,
            "Saturday": 6,
        }

        self._last_sort_col = None
        self._last_sort_reverse = False

        self.load_data()

    def load_data(self):
        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, Subject, Section, Professor, ProfessorEmail, Day, TimeIn, TimeOut, Room FROM Schedule")
            rows = cursor.fetchall()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for index, row in enumerate(rows):
                tag = "evenrow" if index % 2 == 0 else "oddrow"
                values = row + ("Edit | Delete",)
                self.tree.insert("", "end", values=values, tags=(tag,))

            conn.close()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def on_treeview_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)

            if column == "#10":
                x, y, width, height = self.tree.bbox(item, column)
                if event.x > x + width / 2:
                    self.delete_schedule(item)
                else:
                    self.edit_schedule(item)

    def edit_schedule(self, item):
        values = self.tree.item(item, "values")
        schedule_id = values[0]

        if not schedule_id:
            print("Error: Schedule ID is not available!")
            return

        edit_window = ctk.CTkToplevel(self)
        edit_window.title("Edit Schedule")
        edit_window.geometry("250x650")
        edit_window.grab_set()
        edit_window.configure(fg_color="#ffffff")

        ctk.CTkLabel(edit_window, text="Edit Schedule Information", font=("Arial", 16, "bold")).pack(pady=10)

        ctk.CTkLabel(edit_window, text="Subject:").pack()
        subject_entry = ctk.CTkEntry(edit_window)
        subject_entry.insert(0, values[1])
        subject_entry.pack(pady=5)

        ctk.CTkLabel(edit_window, text="Section:").pack()
        section_entry = ctk.CTkEntry(edit_window)
        section_entry.insert(0, values[2])
        section_entry.pack(pady=5)

        ctk.CTkLabel(edit_window, text="Professor:").pack()
        professor_entry = ctk.CTkEntry(edit_window)
        professor_entry.insert(0, values[3])
        professor_entry.pack(pady=5)

        ctk.CTkLabel(edit_window, text="Email:").pack()
        email_entry = ctk.CTkEntry(edit_window)
        email_entry.insert(0, values[4])
        email_entry.pack(pady=5)

        ctk.CTkLabel(edit_window, text="Day:").pack()
        day_dropdown = ctk.CTkComboBox(edit_window,
                                       values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])
        day_dropdown.set(values[5])
        day_dropdown.pack(pady=5)

        ctk.CTkLabel(edit_window, text="Time In:").pack()
        time_in_dropdown = ctk.CTkComboBox(edit_window,
                                           values=[f"{hour % 12 or 12}:00 {'AM' if hour < 12 else 'PM'}" for hour in
                                                   range(7, 22)])
        time_in_dropdown.set(values[6])
        time_in_dropdown.pack(pady=5)

        ctk.CTkLabel(edit_window, text="Time Out:").pack()
        time_out_dropdown = ctk.CTkComboBox(edit_window,
                                            values=[f"{hour % 12 or 12}:00 {'AM' if hour < 12 else 'PM'}" for hour in
                                                    range(7, 22)])
        time_out_dropdown.set(values[7])
        time_out_dropdown.pack(pady=5)

        ctk.CTkLabel(edit_window, text="Room:").pack()
        room_dropdown = ctk.CTkComboBox(edit_window)
        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()
            cursor.execute("SELECT RoomCode FROM Rooms")
            room_ids = [str(row[0]) for row in cursor.fetchall()]
            room_dropdown.configure(values=room_ids)
            room_dropdown.set(values[8])
            conn.close()
        except sqlite3.Error as e:
            print("Database error:", e)
        room_dropdown.pack(pady=5)

        def save_changes():
            try:
                conn = sqlite3.connect("AMS.db")
                cursor = conn.cursor()

                cursor.execute("""
                        UPDATE Schedule SET 
                        Subject = ?,
                        Section = ?,
                        Professor = ?,
                        ProfessorEmail = ?,
                        Day = ?,
                        TimeIn = ?,
                        TimeOut = ?,
                        Room = ?
                        WHERE id = ?
                    """, (
                    subject_entry.get(),
                    section_entry.get(),
                    professor_entry.get(),
                    email_entry.get(),
                    day_dropdown.get(),
                    time_in_dropdown.get(),
                    time_out_dropdown.get(),
                    room_dropdown.get(),
                    schedule_id
                ))

                conn.commit()
                conn.close()

                messagebox.showinfo("Success", "Schedule updated successfully!")
                edit_window.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update schedule: {e}")

        ctk.CTkButton(edit_window, text="Save Changes", command=save_changes,
                      fg_color="#45b45d", hover_color="#308042").pack(pady=20)

    def delete_schedule(self, item):
        values = self.tree.item(item, "values")
        schedule_id = values[0]

        confirm = messagebox.askyesno("Confirm Delete",
                                      f"Are you sure you want to delete this schedule?\n\n"
                                      f"Subject: {values[1]}\n"
                                      f"Section: {values[2]}\n"
                                      f"Professor: {values[3]}\n"
                                      f"Email: {values[4]}\n"
                                      f"Day: {values[5]}\n"
                                      f"Time: {values[6]} - {values[7]}\n"
                                      f"Room: {values[8]}")

        if confirm:
            try:
                conn = sqlite3.connect("AMS.db")
                cursor = conn.cursor()

                cursor.execute("DELETE FROM Schedule WHERE id = ?", (schedule_id,))

                conn.commit()
                conn.close()

                self.tree.delete(item)
                messagebox.showinfo("Success", "Schedule deleted successfully!")

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"An error occurred while deleting: {e}")

    def sort_treeview_by_column(self, column):
        if column == "Action":
            return

        if getattr(self, "_last_sort_col", None) == column:
            self._last_sort_reverse = not getattr(self, "_last_sort_reverse", False)
        else:
            self._last_sort_reverse = False
        self._last_sort_col = column

        column_index = self.tree["columns"].index(column)
        items = []
        for item in self.tree.get_children(""):
            values = self.tree.item(item, "values")
            value = values[column_index]

            if column in ("Student ID", "Student No."):
                try:
                    sort_value = int(value)
                except Exception:
                    sort_value = value
            else:
                sort_value = value.lower() if isinstance(value, str) else value

            items.append((sort_value, item, values))

        items.sort(reverse=self._last_sort_reverse)

        for item in self.tree.get_children(""):
            self.tree.delete(item)

        for index, (_, item, values) in enumerate(items):
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=values, tags=(tag,))

if __name__ == "__main__":
    Dashboard = Dashboard()
    Dashboard.mainloop()