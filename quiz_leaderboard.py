import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime

# File paths
QUIZ_FILE = "quiz_questions.json"
LEADERBOARD_FILE = "quiz_leaderboard.json"

class QuizApp:
    def __init__(self, master):
        self.master = master
        master.title("Quiz Application")
        master.geometry("500x300")
        master.resizable(False, False)

        # Get child's name
        self.user_name = simpledialog.askstring("Enter Name", "Who is taking the test?")

        if not self.user_name:
            messagebox.showerror("Error", "Name cannot be empty. Exiting!")
            master.destroy()
            return

        # Load questions from JSON file
        try:
            with open(QUIZ_FILE, "r") as f:
                self.questions = json.load(f)[:20]  # Take only first 20 questions
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load questions: {e}")
            master.destroy()
            return

        # Quiz state
        self.current_q = 0
        self.score = 0
        self.user_answers = []

        # UI Elements
        self.q_font = ("Arial", 14, "bold")
        self.opt_font = ("Arial", 12)
        self.question_label = tk.Label(master, text="", font=self.q_font, wraplength=450, justify="left")
        self.question_label.pack(pady=10)

        self.selected_option = tk.StringVar(value="")
        self.option_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(master, text="", font=self.opt_font,
                                variable=self.selected_option, value=chr(ord('a')+i),
                                anchor="w", justify="left", padx=20)
            rb.pack(anchor="w", pady=2)
            self.option_buttons.append(rb)

        self.next_button = tk.Button(master, text="Next", font=("Arial", 12), command=self.next_question)
        self.next_button.pack(pady=10)

        # Load first question
        self.show_question()

    def show_question(self):
        """Display the current question and its options."""
        q = self.questions[self.current_q]
        self.question_label.config(text=f"Question {self.current_q + 1}: {q['question']}")
        options = ['a', 'b', 'c', 'd']
        for i, opt in enumerate(options):
            option_text = q.get(opt, "")
            self.option_buttons[i].config(text=f"{opt.upper()}. {option_text}")
        self.selected_option.set("")

    def next_question(self):
        """Handle the Next button: record answer, update score, or show results if quiz ends."""
        selected = self.selected_option.get()
        if selected == "":
            messagebox.showwarning("No Selection", "Please select an answer before clicking Next.")
            return

        # Record answer and update score
        correct = self.questions[self.current_q]['correct_answer']
        self.user_answers.append(selected)
        if selected == correct:
            self.score += 1

        self.current_q += 1
        if self.current_q < len(self.questions):
            self.show_question()
        else:
            self.show_result()

    def show_result(self):
        """Display final score and update leaderboard."""
        # Hide question UI
        self.question_label.pack_forget()
        for rb in self.option_buttons:
            rb.pack_forget()
        self.next_button.pack_forget()

        # Store attempt in leaderboard
        self.save_score()

        # Display score
        result_text = f"Quiz Finished!\n{self.user_name} scored: {self.score} / {len(self.questions)}"
        result_label = tk.Label(self.master, text=result_text, font=("Arial", 14))
        result_label.pack(pady=20)

        # Show leaderboard button
        leaderboard_btn = tk.Button(self.master, text="View Leaderboard", font=("Arial", 12), command=self.view_leaderboard)
        leaderboard_btn.pack()

    def save_score(self):
        """Save quiz attempt in JSON leaderboard."""
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                leaderboard = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            leaderboard = []

        # Count past attempts for this user
        attempt_count = sum(1 for entry in leaderboard if entry["name"] == self.user_name) + 1

        leaderboard.append({
            "name": self.user_name,
            "score": self.score,
            "date": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
            "attempt": attempt_count
        })

        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(leaderboard, f, indent=4)

    def view_leaderboard(self):
        """Display leaderboard table with all attempts."""
        leaderboard_win = tk.Toplevel(self.master)
        leaderboard_win.title("Leaderboard")
        leaderboard_win.geometry("400x400")

        try:
            with open(LEADERBOARD_FILE, "r") as f:
                leaderboard = json.load(f)
        except:
            leaderboard = []

        if not leaderboard:
            tk.Label(leaderboard_win, text="No attempts recorded yet!", font=("Arial", 12)).pack(pady=10)
            return

        # Display leaderboard table
        leaderboard.sort(key=lambda x: (-x["score"], x["date"]))  # Sort by highest score, then date

        table_text = "Name       | Score | Date & Time | Attempt\n" + "="*40 + "\n"
        for entry in leaderboard:
            table_text += f"{entry['name']:10} | {entry['score']}/{len(self.questions)} | {entry['date']} | {entry['attempt']}\n"

        tk.Label(leaderboard_win, text=table_text, font=("Arial", 10), justify="left", anchor="w").pack(pady=10)

# Run the quiz application
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
