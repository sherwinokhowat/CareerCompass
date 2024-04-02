"""
CSC111 Winter 2024 Course Project 2: CareerCompass

This Python module is the GUI

This file is Copyright (c) 2024 Kush Gandhi
"""

from pathlib import Path
import tkinter as tk
import structures
from job import Job
from tkinter import ttk, messagebox
from PIL import ImageTk, Image

# Get File Directory
folder = Path(__file__).absolute().parent


##############################################
# CareerCompass
##############################################


class CareerCompass:
    """
    Class representing the CareerCompass application

    NOTE: Below are only the instance attributes EXCLUDING tkinter widgets.

    Instance Attributes:
    - user_name: the name of the user
    - preferences: a dictionary containing the preferences of the user
    - job_postings: a list containing the job postings

    Representation Invariants:
    - user_name.length() <= 9
    - preferences.keys() == {'country', 'remote', 'work_type', 'rating_score', 'python', 'java', 'c'}
    - preferences.values() == {'Yes', 'No', 'Don't Care'}
    - job_postings.length() <= 5

    """

    user_name: str | None
    preferences: dict[str, str]
    job_postings: list[Job]

    def __init__(self, root):
        """
        Initialize the CareerCompass application
        """

        # Creating container for the pages
        self.container = tk.Frame(root)
        self.container.pack(fill="both", expand=True)

        # Dictionary to store all the pages
        self.pages = {}

        # Load all the images
        self.images = {
            "line": ImageTk.PhotoImage(file=folder / "assets" / "Line.png"),
            "compass_emoji": ImageTk.PhotoImage(
                Image.open(folder / "assets" / "CompassEmoji.png")
            ),
            "hbutton": ImageTk.PhotoImage(
                Image.open(folder / "assets" / "HomeButton.png")
            ),
            "pbutton": ImageTk.PhotoImage(
                Image.open(folder / "assets" / "PreferencesButton.png")
            ),
            "cbutton": ImageTk.PhotoImage(
                Image.open(folder / "assets" / "ContactButton.png")
            ),
            "rs_image": ImageTk.PhotoImage(
                Image.open(folder / "assets" / "Rocket.png")
            ),
            "name_entry_image": ImageTk.PhotoImage(
                Image.open(folder / "assets" / "NameEntryBox.png")
            ),
            "start_button_image": ImageTk.PhotoImage(
                Image.open(folder / "assets" / "StartButton.png")
            ),
            "gradient_background": ImageTk.PhotoImage(
                Image.open(folder / "assets" / "FactBackground.png")
            ),
            "input_box": ImageTk.PhotoImage(
                file=folder / "assets" / "QuestionareEntryBox.png"
            ),
            "next_button_image": ImageTk.PhotoImage(
                Image.open(folder / "assets" / "NextButton.png")
            ),
            "job_posting_img": ImageTk.PhotoImage(
                Image.open(folder / "assets" / "JobPostingBackground.png")
            ),
            "star_img": ImageTk.PhotoImage(Image.open(folder / "assets" / "Star.png")),
            "start_over_button_image": ImageTk.PhotoImage(
                Image.open(folder / "assets" / "StartOverButton.png")
            ),
        }

        # Initializing the instance attributes
        self.user_name = ""
        self.preferences = {
            "country": "",
            "remote": "",
            "work_type": "",
            "rating_score": "",
            "python": "",
            "java": "",
            "c": "",
        }
        self.job_postings = []

        # Show the HomePage
        self.show_pages("HomePage")

    def show_pages(self, target_page):
        """
        Shows the target page and destroys the current page
        """

        # Destroying Current Page
        if self.pages:
            current_page = next(iter(self.pages.values()))
            current_page.destroy()
            self.pages.clear()

        # Create the new page and store it in the dictionary
        new_page = None
        if target_page == "HomePage":
            new_page = HomePage(self.container, self)
        elif target_page == "PreferencesPage":
            new_page = PreferencesPage(self.container, self)
        elif target_page == "JobsPage":
            new_page = JobsPage(self.container, self)

        self.pages[target_page] = new_page
        new_page.pack(fill="both", expand=True)

    def start_over(self):
        """
        # TODO Function to start over the application
        """

        # Clear the user name, preferences, and job postings
        self.user_name = None
        self.preferences.clear()
        self.job_postings.clear()


##############################################
# Home Page
##############################################


class HomePage(ttk.Frame):
    """
    Class for the Home Page
    # TODO
    """

    def __init__(self, container_home, app):
        super().__init__(container_home)

        self.app = app

        # Background
        canvas_home = tk.Canvas(
            self,
            bg="#0E355D",
            height=750,
            width=1000,
            bd=0,
            highlightthickness=0,
            relief="ridge",
        )
        canvas_home.create_rectangle(0, 0, 270.0, 750, fill="#0084FF", outline="")
        canvas_home.create_image(133.9, 153.5, image=self.app.images["line"])

        # Title
        canvas_home.create_text(
            7.0,
            4.0,
            anchor="nw",
            text="Career",
            fill="#0E355D",
            font=("Karma Bold", 64 * -1),
        )
        canvas_home.create_image(63.0, 107, image=self.app.images["compass_emoji"])
        canvas_home.create_text(
            7.0,
            58.0,
            anchor="nw",
            text="C  mpass",
            fill="#0E355D",
            font=("Karma Bold", 64 * -1),
        )

        # Home Button
        self.home_button = tk.Button(
            self,
            image=self.app.images["hbutton"],
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
        )
        self.home_button.place(x=87.0, y=194.0, width=95, height=40.0)

        # Preferences Button
        self.preferences_button = tk.Button(
            self,
            image=self.app.images["pbutton"],
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.start_button_command(),
            relief="flat",
        )
        self.preferences_button.place(x=46.0, y=268.0, width=180, height=40.0)

        # Contact Button
        self.contact_button = tk.Button(
            self,
            image=self.app.images["cbutton"],
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("Contact Button Click"),
            relief="flat",
        )
        self.contact_button.place(x=69.0, y=344.0, width=128, height=40.0)

        # Rocket Ship
        canvas_home.create_image(150.0, 565.0, image=self.app.images["rs_image"])

        # Title
        canvas_home.create_text(
            625.0,
            75.0,
            anchor="center",
            text="Launch Your Career",
            fill="#D6F4FF",
            font=("Karma Bold", 64 * -1),
        )

        # Input Name
        canvas_home.create_text(
            383.0,
            155.0,
            anchor="nw",
            text="What's your name?",
            fill="#FFFFFF",
            font=("Karma Medium", 20 * -1),
        )
        canvas_home.create_image(
            635.0, 215.0, image=self.app.images["name_entry_image"]
        )
        self.name_entry = tk.Entry(
            self, bg="#0084FF", fg="#FFFFFF", font=("Karma Medium", 16), bd=0
        )
        self.name_entry.place(x=395.0, y=200, width=481.0, height=35.0)

        # Filling in the name if it exists
        if self.app.user_name:
            self.name_entry.insert(0, self.app.user_name)

        # Start Button
        start_button = tk.Button(
            self,
            image=self.app.images["start_button_image"],
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.start_button_command(),
            relief="flat",
        )
        start_button.place(x=562.0, y=254.0, width=147.0, height=42.0)

        # Jobs Available Fact
        canvas_home.create_image(
            465.0, 500.0, image=self.app.images["gradient_background"]
        )
        canvas_home.create_text(
            465.0,
            530.0,
            anchor="center",
            text="Jobs Available!",
            fill="#0E355D",
            font=("Karma Medium", 36 * -1),
        )
        canvas_home.create_text(
            465.0,
            470.0,
            anchor="center",
            text="999,999",
            fill="#FFFFFF",
            font=("Karma Bold", 64 * -1),
        )

        # Average Pay Fact
        canvas_home.create_image(
            800.0, 500.0, image=self.app.images["gradient_background"]
        )
        canvas_home.create_text(
            800.0,
            530.0,
            anchor="center",
            text="Average Pay",
            fill="#0E355D",
            font=("Karma Medium", 36 * -1),
        )
        canvas_home.create_text(
            800.0,
            470.0,
            anchor="center",
            text="$99,999",
            fill="#FFFFFF",
            font=("Karma Bold", 64 * -1),
        )

        # Packing the canvas
        canvas_home.pack(fill="both", expand=True)

    def start_button_command(self):
        """
        # TODO Function to check if the name is entered and then move to the next page
        """

        # Update the name
        self.update_name()

        # Proceed to the next page once the name is entered
        if self.app.user_name is not None:
            self.app.show_pages("PreferencesPage")

    def update_name(self):
        """
        # TODO Function to update the name
        """

        # Get the name from the entry box
        username = self.name_entry.get()

        # Check if the name is empty
        if username.strip() == "":
            messagebox.showerror("Error", "Please enter your name.")
            return

        # Update the name
        self.app.user_name = username[:9]


##############################################
# Preferences Page
##############################################
class PreferencesPage(ttk.Frame):
    """
    Class for the Preferences Page
    # TODO
    """

    def __init__(self, container_preferences, app):
        super().__init__(container_preferences)

        self.app = app

        # Background
        canvas_preferences = tk.Canvas(
            self,
            bg="#0E355D",
            height=750,
            width=1000,
            bd=0,
            highlightthickness=0,
            relief="ridge",
        )
        canvas_preferences.create_rectangle(
            0, 0, 270.0, 750, fill="#0084FF", outline=""
        )
        canvas_preferences.create_image(133.9, 153.5, image=self.app.images["line"])

        # Title
        canvas_preferences.create_text(
            7.0,
            4.0,
            anchor="nw",
            text="Career",
            fill="#0E355D",
            font=("Karma Bold", 64 * -1),
        )
        canvas_preferences.create_image(
            63.0, 107, image=self.app.images["compass_emoji"]
        )
        canvas_preferences.create_text(
            7.0,
            58.0,
            anchor="nw",
            text="C  mpass",
            fill="#0E355D",
            font=("Karma Bold", 64 * -1),
        )

        # Home Button
        self.home_button = tk.Button(
            self,
            image=self.app.images["hbutton"],
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.app.show_pages("HomePage"),
            relief="flat",
        )
        self.home_button.place(x=87.0, y=194.0, width=95, height=40.0)

        # Preferences Button
        self.preferences_button = tk.Button(
            self,
            image=self.app.images["pbutton"],
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
        )
        self.preferences_button.place(x=46.0, y=268.0, width=180, height=40.0)

        # Contact Button
        contact_button = tk.Button(
            self,
            image=self.app.images["cbutton"],
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("Contact Button Click"),
            relief="flat",
        )
        contact_button.place(x=69.0, y=344.0, width=128, height=40.0)

        # Rocket Ship
        canvas_preferences.create_image(150.0, 565.0, image=self.app.images["rs_image"])

        # Page Title
        canvas_preferences.create_text(
            625.0,
            70.0,
            anchor="center",
            text=f"{self.app.user_name}, " f"let's see what you prefer.",
            fill="#D6F4FF",
            font=("Karma Bold", 40 * -1),
        )

        # Input Boxes
        self.input_boxes = []
        self.input_box = ImageTk.PhotoImage(
            file=folder / "assets" / "QuestionareEntryBox.png"
        )

        # Inputs
        initial_y = 159
        questions = [
            "Jobs in Canada? (Yes/No/Don't Care)",
            "Remote jobs? (Yes/No/Don't Care)",
            "Frontend jobs? (Yes/No/Don't Care)",
            "Do you prefer a rating score above 3? (Yes/No/Don't Care)",
            "Are you skilled at Python? (Yes/No/Don't Care)",
            "Are you skilled at Java? (Yes/No/Don't Care)",
            "Are you skilled at C/C++? (Yes/No/Don't Care)",
        ]
        for i in range(7):
            canvas_preferences.create_text(
                385.0,
                initial_y - 34,
                anchor="nw",
                text=questions[i],
                fill="#FFFFFF",
                font=("Karma Medium", 18 * -1),
            )
            canvas_preferences.create_image(636.5, initial_y + 15, image=self.input_box)
            input_box = tk.Entry(
                self, bg="#0084FF", fg="#FFFFFF", font=("Karma Medium", 14), bd=0
            )
            input_box.place(x=395.0, y=initial_y, width=481.0, height=35.0)
            self.input_boxes.append(input_box)
            initial_y += 78

        # Filling in the preferences if they exist
        if self.app.preferences:
            for i in range(7):
                key = list(self.app.preferences.keys())[i]
                self.input_boxes[i].insert(0, self.app.preferences[key])

        # Next Button
        next_button = tk.Button(
            self,
            image=self.app.images["next_button_image"],
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.next_button_command(),
            relief="flat",
        )
        next_button.place(x=572.0, y=685.0, width=128.0, height=60.0)

        # Packing the canvas
        canvas_preferences.pack(fill="both", expand=True)

    def next_button_command(self):
        """
        # TODO Function to create the Jobs Page
        """

        # Update the preferences
        if self.update_preferences():

            # Converting the preferences to the correct format
            for key in self.app.preferences:
                if self.app.preferences[key] == "yes":
                    self.app.preferences[key] = 0
                elif self.app.preferences[key] == "no":
                    self.app.preferences[key] = 1
                else:
                    self.app.preferences[key] = 2

            # Generating Decision Tree and Graph
            graph, tree = structures.load_graph_and_tree()

            # Getting the job postings
            self.app.job_postings = tree._traverse_path(
                list(self.app.preferences.items())
            )[:5]

            self.app.show_pages("JobsPage")

    def update_preferences(self) -> bool:
        """
        # TODO Function to check if all the input boxes are filled
        """

        valid_answers = ["yes", "no", "don't care", "dont care"]

        for i in range(7):
            key = list(self.app.preferences.keys())[i]
            preference = self.input_boxes[i].get().lower().strip()

            if preference not in valid_answers:
                messagebox.showerror("Error", "Please enter a valid answer.")
                return False

            self.app.preferences[key] = preference

        return True


##############################################
# Jobs Pages
##############################################


class JobsPage(ttk.Frame):
    """
    Class for the Jobs Page
    # TODO
    """

    def __init__(self, container_jobs, app):
        super().__init__(container_jobs)

        self.app = app

        # Background
        canvas_jobs = tk.Canvas(
            self,
            bg="#0E355D",
            height=750,
            width=1000,
            bd=0,
            highlightthickness=0,
            relief="ridge",
        )
        canvas_jobs.create_rectangle(0, 0, 270.0, 750, fill="#0084FF", outline="")
        canvas_jobs.create_image(133.9, 153.5, image=self.app.images["line"])

        # Title
        canvas_jobs.create_text(
            7.0,
            4.0,
            anchor="nw",
            text="Career",
            fill="#0E355D",
            font=("Karma Bold", 64 * -1),
        )
        canvas_jobs.create_image(63.0, 107, image=self.app.images["compass_emoji"])
        canvas_jobs.create_text(
            7.0,
            58.0,
            anchor="nw",
            text="C  mpass",
            fill="#0E355D",
            font=("Karma Bold", 64 * -1),
        )

        # Home Button
        home_button = tk.Button(
            self,
            image=self.app.images["hbutton"],
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.app.show_pages("HomePage"),
            relief="flat",
        )
        home_button.place(x=87.0, y=194.0, width=95, height=40.0)

        # Preferences Button
        preferences_button = tk.Button(
            self,
            image=self.app.images["pbutton"],
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.app.show_pages("PreferencesPage"),
            relief="flat",
        )
        preferences_button.place(x=46.0, y=268.0, width=180, height=40.0)

        # Contact Button
        contact_button = tk.Button(
            self,
            image=self.app.images["cbutton"],
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("Contact Button Click"),
            relief="flat",
        )
        contact_button.place(x=69.0, y=344.0, width=128, height=40.0)

        # Rocket Ship
        canvas_jobs.create_image(150.0, 565.0, image=self.app.images["rs_image"])

        # Page Text
        canvas_jobs.create_text(
            625.0,
            70.0,
            anchor="center",
            text=f"{self.app.user_name}, find your job!",
            fill="#D6F4FF",
            font=("Karma Bold", 40 * -1),
        )
        canvas_jobs.create_text(
            414.0,
            98.0,
            anchor="nw",
            text="Click one of the stars to find similar jobs!",
            fill="#FFFFFF",
            font=("Karma SemiBold", 20 * -1),
        )

        # Load Job Postings
        initial_y = 175
        for i in range(5):
            # Job Postings
            star = tk.Button(
                self,
                image=self.app.images["star_img"],
                borderwidth=0,
                highlightthickness=0,
                relief="flat",
            )
            star.place(x=322.0, y=initial_y, width=44.0, height=44.0)
            canvas_jobs.create_image(
                635.0, initial_y + 19, image=self.app.images["job_posting_img"]
            )
            canvas_jobs.create_text(
                376.0,
                initial_y - 31,
                anchor="nw",
                text=f"{self.app.job_postings[i].job_details['job_title']}",
                fill="#FFFFFF",
                font=("Karma Bold", 20 * -1),
            )
            canvas_jobs.create_text(
                376.0,
                initial_y - 9,
                anchor="nw",
                text=f" ",
                fill="#0E355D",
                font=("Karma Bold", 16 * -1),
            )
            canvas_jobs.create_text(
                663.0,
                initial_y - 21,
                anchor="nw",
                text=f"Orlando, FL, United States",
                fill="#0E355D",
                font=("Karma Semibold", 13 * -1),
            )
            canvas_jobs.create_text(
                376.0,
                initial_y + 12,
                anchor="nw",
                text=f"Lorem ipsum dolor sit amet, consecrate",
                fill="#FFFFFF",
                font=("Karma Light", 14 * -1),
            )

            initial_y += 106

        # Start Over Button
        start_over_button = tk.Button(
            self,
            image=self.app.images["start_over_button_image"],
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.start_over_button_command(),
            relief="flat",
        )
        start_over_button.place(x=515.0, y=676.0, width=241.0, height=65.0)

        # Packing the canvas
        canvas_jobs.pack(fill="both", expand=True)

    def start_over_button_command(self):
        """
        # TODO Function to start over the application
        """

        self.app.start_over()
        self.app.show_pages("HomePage")


def main():
    # Create the main window
    root = tk.Tk()
    root.title("CareerCompass")
    root.geometry("1000x750")
    root.resizable(False, False)

    # Create the CareerCompass object
    CareerCompass(root)

    # Run the main loop
    root.mainloop()


# Run the main function
if __name__ == "__main__":
    main()
