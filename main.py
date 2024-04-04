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
from scrape import scrape


def career_compass() -> None:
    """
    Running the application
    """
    # NOTE: to test the scraper, you may uncomment the following line. However, do
    # note that the scraper can take upwards to 5-10 minutes, so be prepared lol. Also,
    # the scraper overwrites the current jobs.csv file, so create a copy if  you wish
    # to keep the preloaded dataset prior the running the scraper. Also, please do not
    # have jobs.csv open for at least 10 seconds after the scraper is intially run to
    # prevent any file locking issues (csv may not write to it otherwise).

    # scrape()
    gui()


if __name__ == "__main__":
    import python_ta

    career_compass()
    python_ta.check_all(
        config={
            "max-line-length": 120,
            "extra-imports": ["gui, scrape"],
        }
    )
