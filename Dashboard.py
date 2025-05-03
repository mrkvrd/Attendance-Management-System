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
from customtkinter import CTkImage
import smtplib
import random
import string
from email.message import EmailMessage
import ssl
import re
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import win32com.client as win32
import tempfile

EMAIL_SENDER = 'qcurfidams@gmail.com'
EMAIL_PASSWORD = 'qyvkmwwgwamcekna'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465

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

        self.setup_serial_connection()
        self.timeout_timer = None
        self.last_tap_time = None
        self.setup_timeout_check()

    def on_restore(self, event=None):
        if self.state() == "normal":
            position_top = int((self.screen_height - self.window_height) / 2) - 30
            position_left = int((self.screen_width - self.window_width) / 2)
            self.geometry(f"{self.window_width}x{self.window_height}+{position_left}+{position_top}")

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
                    if rfid_data and len(rfid_data.strip()) == 11 and rfid_data.count(' ') == 3:
                        self.process_rfid(rfid_data)
        except Exception as e:
            print(f"Error reading RFID: {e}")

        self.after(100, self.check_rfid)

    def start_countdown(self, seconds_left):
        if seconds_left > 0:
            self.CamFrame.countdown_label.configure(text=f"Capturing in: {seconds_left}")
            self.after(1000, lambda: self.start_countdown(seconds_left - 1))
        else:
            self.CamFrame.countdown_label.configure(text="")

    def process_rfid(self, rfid_data):
        if not rfid_data or len(rfid_data.strip()) == 0:
            return

        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT StudentNo, LastName, FirstName, MiddleName, Course, Department 
                FROM Students 
                WHERE StudentID = ?
            """, (rfid_data,))

            student_data = cursor.fetchone()

            if not student_data:
                messagebox.showwarning("Not Found", "Student with this RFID not found in database")
                conn.close()
                return

            student_no, last_name, first_name, middle_name, course, department = student_data

            if hasattr(self, 'latest_table_name') and self.latest_table_name:
                cursor.execute(f"""
                    SELECT COUNT(*) FROM [{self.latest_table_name}]
                    WHERE StudentNo = ?
                """, (student_no,))
                count = cursor.fetchone()[0]

                if count > 0:
                    messagebox.showwarning("Duplicate", "Attendance already recorded for this student")
                    conn.close()
                    return

            if hasattr(self, 'reset_timer'):
                self.after_cancel(self.reset_timer)
            self.reset_timer = self.after(300000, self.reset_info_frame)

            self.last_tap_time = datetime.datetime.now()

            self.start_countdown(3)

            self.after(3000, lambda: self.capture_and_save(
                rfid_data, student_no, last_name, first_name,
                middle_name, course, department
            ))

            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error looking up student: {e}")

    def capture_and_save(self, rfid_data, student_no, last_name, first_name, middle_name, course, department):
        if not hasattr(self.TableFrame, 'latest_table_name') or not self.TableFrame.latest_table_name:
            self.CamFrame.countdown_label.configure(text="")
            messagebox.showwarning("No Schedule", "No active schedule for this room")
            return

        try:
            table_name = self.TableFrame.latest_table_name

            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()

            cursor.execute(f"""
                SELECT COUNT(*) FROM [{table_name}]
                WHERE StudentNo = ?
            """, (student_no,))

            if cursor.fetchone()[0] > 0:
                self.CamFrame.countdown_label.configure(text="")
                messagebox.showwarning("Duplicate", "Attendance already recorded for this student")
                conn.close()
                return

            ret, frame = self.CamFrame.cap.read()
            if not ret:
                self.CamFrame.countdown_label.configure(text="")
                messagebox.showerror("Error", "Failed to capture photo")
                conn.close()
                return

            _, img_encoded = cv2.imencode('.jpg', frame)
            photo_blob = img_encoded.tobytes()

            current_time = datetime.datetime.now().strftime("%I:%M %p")
            status = self.determine_status(table_name)

            section = self.get_section_from_table_name(table_name)

            cursor.execute(f"""
                INSERT INTO [{table_name}] 
                (StudentNo, Name, Course, Department, Section, Time, Status, Photo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_no,
                f"{last_name}, {first_name} {middle_name}",
                course,
                department,
                section,
                current_time,
                status,
                photo_blob
            ))

            self.InfoFrame.update_student_info(
                f"{last_name}, {first_name} {middle_name}",
                student_no,
                department,
                course
            )
            self.InfoFrame.update_student_photo(photo_blob)

            conn.commit()
            conn.close()

            if self.TableFrame.current_view == "students":
                self.TableFrame.switch_to_student_view()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save attendance: {e}")
        finally:
            self.CamFrame.countdown_label.configure(text="")

    def determine_status(self, table_name):
        if "TimeOut" in table_name:
            return "Time Out"

        try:
            table_time_str = table_name.split('_')[-2]
            table_time = datetime.datetime.strptime(table_time_str, "%I%M%p")
            current_time = datetime.datetime.now()

            time_diff = (current_time - table_time).total_seconds() / 60
            return "Late" if time_diff > 20 else "Time In"
        except:
            return "Time In"

    def get_section_from_table_name(self, table_name):
        parts = table_name.split('_')
        return parts[3] if len(parts) > 3 else "N/A"

    def reset_info_frame(self):
        self.InfoFrame.update_student_info("Student Name", "00-0000", "_______", "_______")
        self.InfoFrame.update_student_photo(None)

    def setup_timeout_check(self):
        self.check_timeout_inactivity()
        self.after(60000, self.setup_timeout_check)

    def check_timeout_inactivity(self):
        if not hasattr(self.TableFrame, 'latest_table_name') or not self.TableFrame.latest_table_name:
            return

        if "TimeOut" in self.TableFrame.latest_table_name:
            if not self.last_tap_time:
                self.last_tap_time = datetime.datetime.now()
            else:
                time_since_last_tap = (datetime.datetime.now() - self.last_tap_time).total_seconds() / 60
                if time_since_last_tap >= 10:
                    self.handle_timeout_closure()

    def handle_timeout_closure(self):
        try:
            if not hasattr(self.TableFrame, 'latest_table_name') or not self.TableFrame.latest_table_name:
                return

            time_out_table = self.TableFrame.latest_table_name
            if not time_out_table:
                return

            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                AND name LIKE ?
                ORDER BY name DESC
            """, (f"%{self.room_code}%",))
            tables = cursor.fetchall()
            conn.close()
            print(f"Found tables for room {self.room_code}:")
            for table in tables:
                print(f"- {table[0]}")
            if len(tables) < 2:
                conn = sqlite3.connect("AMS.db")
                cursor = conn.cursor()
                parts = time_out_table.split('_')
                if len(parts) >= 4:
                    search_pattern = f"{parts[0]}_{parts[1]}_{parts[2]}_{parts[3]}%"
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' 
                        AND name LIKE ?
                        ORDER BY name DESC
                    """, (search_pattern,))
                    tables = cursor.fetchall()
                    conn.close()
                    print(f"Found related tables with pattern {search_pattern}:")
                    for table in tables:
                        print(f"- {table[0]}")
            if len(tables) < 2:
                messagebox.showerror("Error", f"Could not find two tables to export. Found {len(tables)} tables.")
                return
            table1 = tables[0][0]
            table2 = tables[1][0]
            print(f"Selected tables for export:")
            print(f"- First table: {table1}")
            print(f"- Second table: {table2}")
            excel_file = self.export_tables_to_excel(table1, table2)
            if not excel_file:
                return
            professor_email = self.get_professor_email_robust(table1)
            if professor_email:
                self.send_excel_via_email(professor_email, excel_file)
            else:
                messagebox.showwarning("Warning", "Could not find professor's email. Excel file was not sent.")
            self.TableFrame.latest_table_name = None
            self.TableHeader.Label1.configure(text="No Current Schedule")
            self.last_tap_time = None

            try:
                os.remove(f"latest_table_{self.room_code}.txt")
            except Exception:
                pass
            self.TableFrame.check_and_generate_table()
            self.TableFrame.switch_to_student_view()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to handle timeout closure: {str(e)}")
            print(f"Error details: {str(e)}")

    def export_tables_to_excel(self, table1, table2):
        try:
            conn = sqlite3.connect("AMS.db")
            temp_dir = tempfile.gettempdir()
            excel_file = os.path.join(temp_dir, f"attendance_{table1}.xlsx")
            writer = pd.ExcelWriter(excel_file, engine='openpyxl')

            df1 = pd.read_sql_query(f"SELECT * FROM [{table1}]", conn)
            if df1.empty:
                messagebox.showwarning("Warning", f"No data found in table {table1}")
                return None
            df1_no_photo = df1.drop(columns=['Photo']) if 'Photo' in df1.columns else df1
            short_name1 = table1[-31:] if len(table1) > 31 else table1
            df1_no_photo.to_excel(writer, sheet_name=short_name1, index=False)

            df2 = pd.read_sql_query(f"SELECT * FROM [{table2}]", conn)
            if df2.empty:
                messagebox.showwarning("Warning", f"No data found in table {table2}")
                return None
            df2_no_photo = df2.drop(columns=['Photo']) if 'Photo' in df2.columns else df2
            short_name2 = table2[-31:] if len(table2) > 31 else table2
            df2_no_photo.to_excel(writer, sheet_name=short_name2, index=False)

            writer.close()
            return excel_file
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export tables to Excel: {str(e)}")
            print(f"Export error details: {str(e)}")
            return None

    def get_professor_email_robust(self, table_name):
        try:
            parts = table_name.split('_')
            if len(parts) < 5:
                return None
            day = parts[0]
            subject = parts[1]
            professor = parts[2]
            section = parts[3]

            professor_spaced = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', professor)
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT ProfessorEmail 
                FROM Schedule 
                WHERE Room = ? AND LOWER(Professor) LIKE LOWER(?) AND Section = ? AND Day = ?
            """, (self.room_code, f"%{professor_spaced}%", section, day))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting professor email (robust): {e}")
            return None

    def send_excel_via_email(self, professor_email, excel_file):
        try:
            subject = f"Attendance Report - {self.room_code}"
            body = f"Please find attached the attendance report for your class in room {self.room_code}."

            em = EmailMessage()
            em['From'] = EMAIL_SENDER
            em['To'] = professor_email
            em['Subject'] = subject
            em.set_content(body)

            with open(excel_file, 'rb') as f:
                file_data = f.read()
                file_name = os.path.basename(excel_file)
                em.add_attachment(file_data, maintype='application', subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=file_name)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as smtp:
                smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                smtp.send_message(em)

            messagebox.showinfo("Email Sent", f"Attendance report has been sent to {professor_email}")

            os.remove(excel_file)

        except Exception as e:
            messagebox.showerror("Email Error", f"Failed to send email: {e}")

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

        self.StudentDeptLabel = ctk.CTkLabel(self, text="Department:", font=("Arial", 20))
        self.StudentDeptLabel.grid(row=2, column=1, sticky="nw")
        self.StudentDeptLabel = ctk.CTkLabel(self, text="_______", font=("Arial", 20, "bold"))
        self.StudentDeptLabel.grid(row=2, column=2, sticky="new")

        self.StudentProgramLabel = ctk.CTkLabel(self, text="Program:", font=("Arial", 20))
        self.StudentProgramLabel.grid(row=3, column=1, sticky="nw")
        self.StudentProgramLabel = ctk.CTkLabel(self, text="_______", font=("Arial", 20, "bold"))
        self.StudentProgramLabel.grid(row=3, column=2, sticky="new")

    def update_student_photo(self, photo_blob):
        if photo_blob:
            try:
                from io import BytesIO
                image = Image.open(BytesIO(photo_blob))
                image = image.resize((300, 250))
                photo = CTkImage(light_image=image, size=(300, 250))
                self.StudentImage = photo
                self.ImageLabel3.configure(image=self.StudentImage)
            except Exception as e:
                print(f"Failed to update student photo: {e}")
        else:
            default = Image.open("images/bg.png")
            photo = CTkImage(light_image=default, size=(300, 250))
            self.StudentImage = photo
            self.ImageLabel3.configure(image=self.StudentImage)

    def update_student_info(self, name, student_no, department, course):
        self.StudentName.configure(text=name)
        self.StudentNoEntry.configure(text=student_no)
        self.StudentDeptLabel.configure(text=department)
        self.StudentProgramLabel.configure(text=course)


class CamFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(corner_radius=0, fg_color="#ffffff")
        self.current_image = None

        self.countdown_label = ctk.CTkLabel(
            self, text="", font=("Arial", 24, "bold"),
            text_color="#115272", height=30
        )
        self.countdown_label.pack(pady=(10, 0))

        self.camera_label = ctk.CTkLabel(self, text="Initializing Camera...")
        self.camera_label.pack(expand=True, fill="both")

        self.cap = cv2.VideoCapture(0)
        self.update_camera()

    def update_camera(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img = img.resize((300, 250))
                self.current_image = ctk.CTkImage(light_image=img, size=(300, 250))
                self.camera_label.configure(image=self.current_image, text="")
        self.after(30, self.update_camera)

    def stop_camera(self):
        if hasattr(self, 'cap'):
            self.cap.release()
        if hasattr(self, 'camera_label'):
            self.camera_label.configure(image=None, text="Camera Off")
        if hasattr(self, 'current_image'):
            self.current_image = None

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
                if hasattr(self.master, 'CamFrame'):
                    self.master.CamFrame.stop_camera()
                self.master.destroy()
                import RoomLogin
                RoomLogin.Login().mainloop()
        elif choice == "Dashboard":
            print("Dashboard selected")
            self.Label2.configure(text="Students Time Table")
            self.master.TableFrame.switch_to_student_view()
        elif choice == "Early Out":
            self.handle_early_out()
        elif choice == "View Room Schedule":
            print("View Room Schedule selected")
            self.Label2.configure(text="Room Schedule")
            self.master.TableFrame.switch_to_schedule_view()

    def handle_early_out(self):
        if not hasattr(self.master.TableFrame, 'latest_table_name') or not self.master.TableFrame.latest_table_name:
            messagebox.showwarning("No Active Session", "There is no active class session to end early.")
            return

        latest_table = self.master.TableFrame.latest_table_name

        if "TimeOut" in latest_table:
            messagebox.showwarning("Already Timed Out", "This session has already been timed out.")
            return

        confirm = messagebox.askyesno("Confirm Early Out",
                                      "Are you sure you want to end this class session early?\n\n"
                                      "This will require verification from the professor.")
        if not confirm:
            return

        try:
            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()

            parts = latest_table.split('_')
            if len(parts) < 5:
                messagebox.showerror("Error", "Invalid table name format.")
                conn.close()
                return

            day = parts[0]

            section = parts[-3]

            time_index = -2
            section_index = -3

            professor = parts[section_index - 1]
            professor_spaced = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', professor)

            subject_parts = parts[1:section_index - 1]
            subject = '_'.join(subject_parts)

            cursor.execute("""
                SELECT DISTINCT ProfessorEmail 
                FROM Schedule 
                WHERE Room = ? AND LOWER(Professor) LIKE LOWER(?)
            """, (self.master.room_code, f"%{professor_spaced}%"))

            result = cursor.fetchone()

            conn.close()

            if not result or not result[0]:
                messagebox.showerror("Error",
                                     f"Could not find professor's email for verification.\nProfessor: {professor}, Section: {section}, Day: {day}")
                return

            professor_email = result[0]
            print(f"Found professor email: {professor_email} for professor: {professor}")

            def otp_callback(verified):
                if verified:
                    self.create_early_out_table(latest_table)
                else:
                    messagebox.showinfo("Cancelled", "Early out verification was cancelled.")

            OTPDialog(self.master, professor_email, otp_callback)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error retrieving professor information: {e}")

    def create_early_out_table(self, time_in_table):
        try:
            parts = time_in_table.split('_')
            if len(parts) < 5:
                messagebox.showerror("Error", "Invalid table name format.")
                return

            current_time = datetime.datetime.now().strftime("%I%M%p")
            parts[-2] = current_time
            parts[-1] = "TimeOut"
            time_out_table = '_'.join(parts)

            conn = sqlite3.connect("AMS.db")
            cursor = conn.cursor()

            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS [{time_out_table}] (
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

            conn.commit()
            conn.close()

            self.master.TableFrame.latest_table_name = time_out_table
            with open(f"latest_table_{self.master.room_code}.txt", "w") as f:
                f.write(time_out_table)

            self.master.TableHeader.Label1.configure(text=time_out_table)
            if self.master.TableFrame.current_view == "students":
                self.master.TableFrame.switch_to_student_view()

            self.master.last_tap_time = datetime.datetime.now()

            messagebox.showinfo("Success", "Class ended early. TimeOut attendance table created successfully.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error creating early out table: {e}")

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

                if 0 <= time_in_diff <= 30 and not self.is_timeout_created(current_day, subject, professor, section, time_out):
                    table_name = self.get_table_name(current_day, subject, professor, section, time_in, "TimeIn")
                    if not self.table_exists(table_name, cursor):
                        created_table_name = self.create_attendance_table(current_day, subject, professor, section,
                                                                          time_in, "TimeIn", cursor)
                        print(f"Created TimeIn table: {created_table_name}")

                elif 0 <= time_out_diff <= 30:
                    table_name = self.get_table_name(current_day, subject, professor, section, time_out, "TimeOut")
                    if not self.table_exists(table_name, cursor):
                        created_table_name = self.create_attendance_table(current_day, subject, professor, section,
                                                                          time_out, "TimeOut", cursor)
                        print(f"Created TimeOut table: {created_table_name}")

                        self.master.last_tap_time = datetime.datetime.now()

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


class OTPDialog(ctk.CTkToplevel):
    def __init__(self, parent, email, callback):
        super().__init__(parent)

        self.parent = parent
        self.email = email
        self.callback = callback
        self.result = False
        self.configure(fg_color="#ffffff")

        self.otp = self.generate_otp()

        self.send_otp()

        self.title("OTP Verification")
        self.geometry("430x250")
        self.resizable(False, False)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 430) // 2
        y = (screen_height - 250) // 2
        self.geometry(f"430x250+{x}+{y}")

        self.transient(parent)
        self.grab_set()

        self.create_widgets()

        parent.wait_window(self)

    def generate_otp(self, length=6):
        return ''.join(random.choices(string.digits, k=length))

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)

        info_frame = ctk.CTkFrame(self, fg_color="#ffffff")
        info_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        info_frame.grid_columnconfigure(0, weight=1)

        header_label = ctk.CTkLabel(
            info_frame,
            text="Verification Required",
            font=("Arial", 20, "bold"),
            text_color="#115272"
        )
        header_label.grid(row=0, column=0, sticky="ew")

        display_email = self.email
        if len(display_email) > 30:
            display_email = display_email[:15] + "..." + display_email[-12:]

        email_label = ctk.CTkLabel(
            info_frame,
            text=f"An OTP has been sent to:\n{display_email}",
            font=("Arial", 14)
        )
        email_label.grid(row=1, column=0, sticky="ew", pady=10)

        entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        entry_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        entry_frame.grid_columnconfigure(0, weight=1)

        self.otp_entry = ctk.CTkEntry(
            entry_frame,
            placeholder_text="Enter 6-digit OTP",
            font=("Arial", 16),
            width=200,
            justify="center",
            corner_radius=0,
            height=30
        )
        self.otp_entry.grid(row=0, column=0, sticky="ew")

        self.error_label = ctk.CTkLabel(
            entry_frame,
            text="",
            text_color="#FF0000",
            font=("Arial", 12)
        )
        self.error_label.grid(row=1, column=0, sticky="ew", pady=(5, 0))

        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        buttons_frame.grid_columnconfigure((0, 1), weight=1)

        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            font=("Arial", 14),
            fg_color="#6c757d",
            hover_color="#5a6268",
            command=self.on_cancel
        )
        cancel_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        verify_button = ctk.CTkButton(
            buttons_frame,
            text="Verify",
            font=("Arial", 14),
            fg_color="#28A745",
            hover_color="#208637",
            command=self.verify_otp
        )
        verify_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        self.bind("<Return>", lambda event: self.verify_otp())

        self.otp_entry.focus_set()

    def send_otp(self):
        try:
            subject = 'Early Out Verification OTP'
            body = f"""
            You are receiving this email because an early out request was made for your class.

            Your verification OTP is: {self.otp}

            This OTP is valid for 10 minutes. If you didn't request this, please ignore this email.
            """

            em = EmailMessage()
            em['From'] = EMAIL_SENDER
            em['To'] = self.email
            em['Subject'] = subject
            em.set_content(body)

            context = ssl.create_default_context()

            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as smtp:
                smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                smtp.sendmail(EMAIL_SENDER, self.email, em.as_string())

            return True
        except Exception as e:
            print(f"Error sending OTP: {e}")
            messagebox.showerror("Email Error",
                                 "Failed to send OTP email. Please check your internet connection "
                                 "and ensure the professor's email is correct.")
            return False

    def verify_otp(self):
        entered_otp = self.otp_entry.get().strip()

        if not entered_otp:
            self.error_label.configure(text="Please enter the OTP")
            return

        if entered_otp == self.otp:
            self.result = True
            self.callback(True)
            self.destroy()
        else:
            self.error_label.configure(text="Invalid OTP. Please try again.")
            self.otp_entry.delete(0, 'end')

    def on_cancel(self):
        self.result = False
        self.callback(False)
        self.destroy()

if __name__ == "__main__":
    Dashboard = Dashboard()
    Dashboard.mainloop()