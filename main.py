"""
CSC111 Winter 2024 Course Project 2: CareerCompass

This Python module contains the main function to
run our application.

Copyright and Usage Information
===============================
This file is provided solely for the personal and private use of the instructors
and teaching assistants of CSC111 at the University of Toronto St. George campus.
All forms of distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright of these files,
please contact us through Github using the "contact" button within our application.

This file is Copyright (c) 2024 Kush Gandhi, Sherwin Okhowat, David Cen, Tony Qi.
"""

from gui import gui


def career_compass() -> None:
    """
    Running the application
    """

    gui()


if __name__ == '__main__':

    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ["gui"],
    })
