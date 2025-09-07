import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd

root = tk.Tk()
root.title("🎓 Students Grade Manager")
root.geometry("400x300")
root.resizable(False, False)

main_frame = ttk.Frame(root, padding=20)
main_frame.grid(row=0, column=0)

name_lable = ttk.Label(main_frame, text="Student Name:")
name_lable.grid(row=0, column=0, sticky="w", pady=5)

name_entry = ttk.Entry(main_frame, width=30)
name_entry.grid(row=0, column=1, pady=5)

grade_lable = ttk.Label(main_frame, text="Grade:")
grade_lable.grid(row=1, column=0, sticky="w", pady=5)

grade_entry = ttk.Entry(main_frame, width=30)
grade_entry.grid(column=1, row=1, pady=5)


def add_student():
    name = name_entry.get()
    grade = grade_entry.get()

    if not name or not grade:
        messagebox.showwarning("Missing info", "Please fill out all fields.")
        return

    try:
        grade = float(grade)
    except ValueError:
        messagebox.showerror("Invalid Grade", "Grade must be a number.")
        return

    conn = sqlite3.connect("init.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (name, grade) VALUES (?, ?)", (name, grade))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"✅ Added {name} successfully!")
    name_entry.delete(0, tk.END)
    grade_entry.delete(0, tk.END)


add_btn = ttk.Button(main_frame, text="Add Student", command=add_student).grid(
    row=2, column=0, columnspan=2, pady=10)


def show_students():
    conn = sqlite3.connect("init.db")
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()

# Create a new window to display the table
    window = tk.Toplevel(root)
    window.title("📋 All Students")
    window.geometry("400x300")

    tree = ttk.Treeview(window, columns=(
        "ID", "Name", "Grade"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Grade", text="Grade")


# Adjust columns
    tree.column("ID", width=50)
    tree.column("Name", width=150)
    tree.column("Grade", width=100)

# Data entry
    for index, row in df.iterrows():
        tree.insert("", tk.END, values=(row["id"], row["name"], row["grade"]))

    tree.pack(fill="both", expand=True)

    def calculate_average():
        conn = sqlite3.connect("init.db")
        cursor = conn.cursor()
        cursor.execute("SELECT AVG(grade) FROM students")
        avg = cursor.fetchone()[0]
        conn.close()

        if avg is None:
            messagebox.showinfo("📊 Average", "No data to calculate average.")
        else:
            messagebox.showinfo(
                "📊 Average", f"The average grade is: {avg:.2f}")

    avg_btn = ttk.Button(window, text="📊 Show Average",
                         command=calculate_average)
    avg_btn.pack(pady=5)

    def show_max_grade():
        conn = sqlite3.connect("init.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, grade FROM students ORDER BY grade DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()

        if result:
            name, grade = result
            messagebox.showinfo("🏆 Highest Grade",
                                f"{name} has the highest grade: {grade}")
        else:
            messagebox.showinfo("🏆 Highest Grade", "No students found.")

    max_btn = ttk.Button(window, text="🏆 Show Max Grade",
                         command=show_max_grade)
    max_btn.pack(pady=5)

    def show_min_grade():
        conn = sqlite3.connect("init.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, grade FROM students ORDER BY grade ASC LIMIT 1")
        result = cursor.fetchone()
        conn.close()

        if result:
            name, grade = result
            messagebox.showinfo(
                "📉 Lowest Grade", f"{name} has the lowest grade: {grade}")
        else:
            messagebox.showinfo("📉 Lowest Grade", "No students found.")

    min_btn = ttk.Button(window, text="📉 Show Min Grade",
                         command=show_min_grade)
    min_btn.pack(pady=5)

    def delete_student():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning(
                "⚠️ No Selection", "Please select a student to delete.")
            return

        values = tree.item(selected[0], "values")
        student_id = values[0]

        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm", f"Are you sure you want to delete student ID {student_id}?")
        if not confirm:
            return

        conn = sqlite3.connect("init.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        conn.close()

        # Delete from table
        tree.delete(selected[0])
        messagebox.showinfo(
            "Deleted", "Student has been deleted successfully.")

    delete_btn = ttk.Button(
        window, text="🗑️ Delete Selected", command=delete_student)
    delete_btn.pack(pady=10)

    def edit_student():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning(
                "⚠️ No Selection", "Please select a student to edit.")
            return

        values = tree.item(selected[0], "values")
        student_id = values[0]
        current_name = values[1]
        current_grade = values[2]

        # Edit window
        edit_win = tk.Toplevel(window)
        edit_win.title("✏️ Edit Student")
        edit_win.geometry("300x200")

        name_label = ttk.Label(edit_win, text="Student Name:")
        name_label.pack(pady=5)
        name_entry = ttk.Entry(edit_win)
        name_entry.insert(0, current_name)
        name_entry.pack(pady=5)

        grade_label = ttk.Label(edit_win, text="Grade:")
        grade_label.pack(pady=5)
        grade_entry = ttk.Entry(edit_win)
        grade_entry.insert(0, current_grade)
        grade_entry.pack(pady=5)

        def update_student():
            new_name = name_entry.get()
            new_grade = grade_entry.get()

            if not new_name or not new_grade:
                messagebox.showwarning(
                    "⚠️ Missing Info", "Please fill out all fields.")
                return

            try:
                new_grade = float(new_grade)
            except ValueError:
                messagebox.showerror(
                    "❌ Invalid Grade", "Grade must be a number.")
                return

            conn = sqlite3.connect("init.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE students SET name = ?, grade = ? WHERE id = ?",
                (new_name, new_grade, student_id)
            )
            conn.commit()
            conn.close()

            # Update in the table
            tree.item(selected[0], values=(student_id, new_name, new_grade))
            messagebox.showinfo("✅ Updated", "Student updated successfully.")
            edit_win.destroy()

        update_btn = ttk.Button(edit_win, text="Update",
                                command=update_student)
        update_btn.pack(pady=10)

   # update button
    edit_btn = ttk.Button(window, text="✏️ Edit Selected",
                          command=edit_student)
    edit_btn.pack(pady=5)


show_btn = ttk.Button(main_frame, text="Show Students", command=show_students)
show_btn.grid(row=3, column=0, columnspan=2, pady=10)


def search_student():
    search_win = tk.Toplevel(root)
    search_win.title("🔍 Search Student")
    search_win.geometry("300x150")

    ttk.Label(search_win, text="Enter student name:").pack(pady=5)
    search_entry = ttk.Entry(search_win, width=30)
    search_entry.pack(pady=5)

    def do_search():
        name = search_entry.get()
        if not name:
            messagebox.showwarning("Empty", "Please enter a name.")
            return

        conn = sqlite3.connect("init.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE name LIKE ?",
                       ('%' + name + '%',))
        results = cursor.fetchall()
        conn.close()

        if not results:
            messagebox.showinfo(
                "Not Found", "🚫 No student found with that name.")
            return

        # Show results in a new window
        result_win = tk.Toplevel(root)
        result_win.title("🔎 Search Results")
        result_win.geometry("400x200")

        tree = ttk.Treeview(result_win, columns=(
            "ID", "Name", "Grade"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Name", text="Name")
        tree.heading("Grade", text="Grade")

        for row in results:
            tree.insert("", tk.END, values=row)

        tree.pack(fill="both", expand=True)

    ttk.Button(search_win, text="Search", command=do_search).pack(pady=10)


search_btn = ttk.Button(
    main_frame, text="Search Student", command=search_student)
search_btn.grid(row=4, column=0, columnspan=2, pady=10)


root.mainloop()
