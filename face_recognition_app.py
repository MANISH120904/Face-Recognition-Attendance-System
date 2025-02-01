import cv2
import face_recognition
import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class FaceRecognitionApp:
    def __init__(self, root):
            self.root = root
            self.root.title("Face Recognition App")
            self.root.configure(bg="black")
            self.show_roll_no = True 

            # Ensure attendance file exists with headers
            if not os.path.exists("attendance.csv"):
                with open("attendance.csv", mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Timestamp", "Name", "Roll Number"]) 
            # Create a custom style for the label frame and buttons
            self.style = ttk.Style()
            self.style.configure("Main.TLabelframe", background="black", foreground="white")
            self.style.configure("Main.TButton", font=("Helvetica", 14), foreground="black", background="#4CAF50", width=20)

            # Make the main menu window bigger
            main_menu_frame = ttk.LabelFrame(root, text="Main Menu", padding=(50,50), relief="groove", borderwidth=3, style="Main.TLabelframe")
            main_menu_frame.grid(row=0, column=0, pady=100, padx=100)

            self.register_button = ttk.Button(main_menu_frame, text="Register", command=self.register_faces, style="Main.TButton")
            self.register_button.grid(row=0, column=0, pady=20)

            self.recognize_button = ttk.Button(main_menu_frame, text="Recognize", command=self.recognize_face, style="Main.TButton")
            self.recognize_button.grid(row=1, column=0, pady=20)

            self.delete_button = ttk.Button(main_menu_frame, text="Delete", command=self.delete_faces, style="Main.TButton")
            self.delete_button.grid(row=2, column=0, pady=20)

            self.view_attendance_button = ttk.Button(main_menu_frame, text="View Attendance", command=self.view_attendance, style="Main.TButton")
            self.view_attendance_button.grid(row=3, column=0, pady=20)

            self.exit_button = ttk.Button(main_menu_frame, text="Exit", command=root.destroy, style="Main.TButton")
            self.exit_button.grid(row=4, column=0, pady=20)

            self.settings_button = ttk.Button(main_menu_frame, text="Settings", command=self.show_settings,
                                            style="Main.TButton")
            self.settings_button.grid(row=5, column=0, pady=20)


    def record_attendance(self, name, roll_no, csv_filename="attendance.csv"):
        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([timestamp, name, roll_no])
            print(f"Attendance recorded for {name} ({roll_no}) at {timestamp}")

    def view_attendance(self):
            self.root.withdraw()
            attendance_window = tk.Toplevel(self.root)
            attendance_window.title("Attendance Records")
            attendance_window.configure(bg="black")

            attendance_frame = ttk.LabelFrame(attendance_window, text="Attendance Records", padding=(20, 20), relief="groove", borderwidth=3, style="Main.TLabelframe")
            attendance_frame.grid(row=0, column=0, padx=50, pady=50)

            text_area = tk.Text(attendance_frame, wrap=tk.WORD, width=60, height=20, font=("Helvetica", 12))
            text_area.grid(row=0, column=0, padx=10, pady=10)

            try:
                with open("attendance.csv", mode='r') as file:
                    reader = csv.reader(file)
                    attendance_data = "\n".join([", ".join(row) for row in reader])
                    text_area.insert(tk.END, attendance_data)
            except FileNotFoundError:
                text_area.insert(tk.END, "No attendance records found.")

            back_button = tk.Button(attendance_window, text="Back to Main Menu", command=lambda: [attendance_window.destroy(), self.root.deiconify()], font=("Helvetica", 14), bg="#4CAF50", fg="white")
            back_button.grid(row=1, column=0, pady=20)

    def capture_register(self):
        video_capture = cv2.VideoCapture(0)

        name = self.name_entry.get().strip()
        roll_no = self.roll_no_entry.get().strip()

        if not name or not roll_no:
            messagebox.showwarning("Warning", "Please enter both name and roll number before capturing.")
            return

        registered_faces = self.load_registered_faces_from_folder(folder_path="registered_faces")

        face_captured = False  # Track if a face has been successfully captured

        while True:
            ret, frame = video_capture.read()
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                face_captured = True  # Mark that a face has been captured

            cv2.imshow('Registration - Press "q" to save and exit', frame)

            if cv2.waitKey(1) & 0xFF == ord('q') and face_captured:
                registered_faces[name] = {'face_encoding': face_encoding, 'roll_no': roll_no}
                self.save_registered_faces(registered_faces, folder_path="registered_faces")
                messagebox.showinfo("Registration Completed", f"Face registered for {name} (Roll No: {roll_no})")
                break
            elif cv2.waitKey(1) & 0xFF == ord('q'):
                messagebox.showwarning("Warning", "No face detected! Try again.")

        video_capture.release()
        cv2.destroyAllWindows()
        self.back_to_main_menu()


    def register_faces(self):
        self.root.withdraw()  # Hide the main menu
        self.registration_window = tk.Toplevel(self.root)
        self.registration_window.title("Registration Mode")
        self.registration_window.configure(bg="black")

        registration_frame = ttk.LabelFrame(self.registration_window, text="Register Face", padding=(20, 20), relief="groove", borderwidth=3, style="Main.TLabelframe")
        registration_frame.grid(row=0, column=0, padx=50, pady=50)

        label = tk.Label(registration_frame, text="Capture your face and enter a label to register:", font=("Helvetica", 16), background="black", foreground="white")
        label.grid(row=0, column=0, columnspan=2, pady=20)

        name_label = tk.Label(registration_frame, text="Enter Name:", font=("Helvetica", 14), background="black", foreground="grey")
        name_label.grid(row=1, column=0, pady=10)

        self.name_entry = tk.Entry(registration_frame, font=("Helvetica", 14))
        self.name_entry.grid(row=1, column=1, pady=10)

        roll_no_label = tk.Label(registration_frame, text="Enter Roll No:", font=("Helvetica", 14), background="black", foreground="grey")
        roll_no_label.grid(row=2, column=0, pady=10)

        self.roll_no_entry = tk.Entry(registration_frame, font=("Helvetica", 14))
        self.roll_no_entry.grid(row=2, column=1, pady=10)

        # FIX: Pass self.capture_register() without unnecessary arguments
        register_button = tk.Button(registration_frame, text="Register", command=self.capture_register, font=("Helvetica", 14), bg="#4CAF50", fg="white")
        register_button.grid(row=3, column=0, columnspan=2, pady=20)

        back_button = tk.Button(registration_frame, text="Back to Main Menu", command=self.back_to_main_menu, font=("Helvetica", 14), bg="#f44336", fg="white")
        back_button.grid(row=4, column=0, columnspan=2, pady=20)

    def recognize_face(self):
        registered_faces = self.load_registered_faces_from_folder(folder_path="registered_faces")
        recorded_names = set()

        video_capture = cv2.VideoCapture(0)

        while True:
            ret, frame = video_capture.read()

            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                known_encodings = [data['face_encoding'] for data in registered_faces.values()]  # Extract only face encodings

                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                face_distances = face_recognition.face_distance(known_encodings, face_encoding)

                best_match_index = None
                if True in matches:
                    # Find the index with the smallest distance (best match)
                    best_match_index = min(range(len(matches)), key=lambda i: face_distances[i])

                if best_match_index is not None:
                    label = list(registered_faces.keys())[best_match_index]
                    roll_no = registered_faces[label]['roll_no']

                    if label not in recorded_names:
                        self.record_attendance(label, roll_no)
                        recorded_names.add(label)

                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    font = cv2.FONT_HERSHEY_DUPLEX

                    # Display the label and optionally the Roll No based on settings
                    if self.show_roll_no:
                        cv2.putText(frame, f"{label} - {roll_no}", (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
                    else:
                        cv2.putText(frame, label, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
                else:
                    # Display "Unknown Face" for unregistered faces
                    cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, "Unknown Face", (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

            cv2.imshow('Recognition', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()

        self.save_registered_faces(registered_faces, folder_path="registered_faces")
        messagebox.showinfo("Recognized succesfully", "Attendance recorded")
        self.back_to_main_menu()


    def delete_faces(self):
            self.root.withdraw()  # Hide the main menu
            self.delete_window = tk.Toplevel(self.root)
            self.delete_window.title("Delete Mode")
            self.delete_window.configure(bg="black")

            delete_frame = ttk.LabelFrame(self.delete_window, text="Delete Face", padding=(20, 20), relief="groove", borderwidth=3, style="Main.TLabelframe")
            delete_frame.grid(row=0, column=0, padx=50, pady=50)

            label = tk.Label(delete_frame, text="Select a face to delete:", font=("Helvetica", 16), background="black", foreground="white")
            label.grid(row=0, column=0, columnspan=2, pady=20)

            # Display the list of registered faces
            registered_faces = self.load_registered_faces_from_folder(folder_path="registered_faces")
            self.face_listbox = tk.Listbox(delete_frame, selectmode=tk.SINGLE, font=("Helvetica", 14))
            for label in registered_faces.keys():
                self.face_listbox.insert(tk.END, label)
            self.face_listbox.grid(row=1, column=0, columnspan=2, pady=20)

            delete_button = tk.Button(delete_frame, text="Delete Face", command=self.delete_selected_face, font=("Helvetica", 14), bg="#f44336", fg="white")
            delete_button.grid(row=2, column=0, pady=20)

            back_button = tk.Button(delete_frame, text="Back to Main Menu", command=self.back_to_main_menu_delete, font=("Helvetica", 14), bg="#4CAF50", fg="white")
            back_button.grid(row=3, column=0, pady=20)

    def delete_selected_face(self):
        selected_index = self.face_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Warning", "Please select a face to delete.")
            return

        selected_label = self.face_listbox.get(selected_index)
        registered_faces = self.load_registered_faces_from_folder(folder_path="registered_faces")

        if selected_label in registered_faces:
            del registered_faces[selected_label]

            file_path = os.path.join("registered_faces", f"{selected_label}.pkl")
            if os.path.exists(file_path):
                os.remove(file_path)

            self.save_registered_faces(registered_faces, folder_path="registered_faces")
            messagebox.showinfo("Success", f"Face '{selected_label}' deleted successfully.")
        else:
            messagebox.showwarning("Warning", f"Face '{selected_label}' not found.")

        self.face_listbox.delete(0, tk.END)
        for label in registered_faces.keys():
            self.face_listbox.insert(tk.END, label)

    def back_to_main_menu_delete(self):
        self.delete_window.destroy()
        self.root.deiconify()

    def back_to_main_menu(self):
        if hasattr(self, 'registration_window'):
            self.registration_window.destroy()
        elif hasattr(self, 'recognition_window'):
            self.recognition_window.destroy()
        elif hasattr(self, 'delete_window'):
            self.delete_window.destroy()

        self.root.deiconify()

    def load_registered_faces_from_folder(self, folder_path="registered_faces"):
        import pickle

        registered_faces = {}

        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                label = os.path.splitext(filename)[0]
                with open(os.path.join(folder_path, filename), 'rb') as file:
                    face_encoding = pickle.load(file)
                    registered_faces[label] = face_encoding

        return registered_faces

    def save_registered_faces(self, registered_faces, folder_path="registered_faces"):
        import pickle

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for label, face_encoding in registered_faces.items():
            filename = os.path.join(folder_path, f"{label}.pkl")
            with open(filename, 'wb') as file:
                pickle.dump(face_encoding, file)

    def record_attendance(self, name, roll_no, csv_filename="attendance.csv"):
            with open(csv_filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow([timestamp, name, roll_no])
                print(f"Attendance recorded for {name} ({roll_no}) at {timestamp}")
    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.configure(bg="black")

        view_roll_no_var = tk.IntVar(value=1)  # Default: Roll No is visible

        view_roll_no_checkbox = tk.Checkbutton(settings_window, text="View Roll No", variable=view_roll_no_var,
                                               font=("Helvetica", 14), background="black", foreground="white")
        view_roll_no_checkbox.grid(row=0, column=0, pady=20)

        save_button = tk.Button(settings_window, text="Save",
                                command=lambda: self.save_settings(settings_window, view_roll_no_var),
                                font=("Helvetica", 14), bg="#4CAF50", fg="white")
        save_button.grid(row=1, column=0, pady=20)

    def save_settings(self, settings_window, view_roll_no_var):
        self.show_roll_no = view_roll_no_var.get()
        settings_window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()

