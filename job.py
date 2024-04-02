from typing import Any
from random import randint


class Job:
    """
    Class representing a job posting instance.

    Instance Attributes:
    - job_details: a dictionary representing this Job instance's details.

    Representation Invariants:
    - 'job_title' in self.job_details
    - 'employer_name' in self.job_details
    - 'rating' in self.job_details
    - 'link' in self.job_details
    - 'fragmented_desc' in self.job_details
    - 'full_desc' in self.job_details
    - 'skills' in self.job_details
    - 'latitutde' in self.job_details
    - 'longitude' in self.job_details
    - 'city' in self.job_details
    - 'country' in self.job_details
    - 'pay_period' in self.job_details
    - 'pay' in self.job_details
    - 'job_id' in self.job_details
    - 'image_url' in self.job_details
    - self.job_details['country'] in {'Canada', 'United States'}
    """

    job_details: dict[str, Any]
    decisions: list[int]

    def __init__(self, job_details: dict[str, Any]) -> None:
        """
        Constructor for a Job instance.

        Preconditions:
        - 'job_title' in job_details
        - 'employer_name' in job_details
        - 'rating' in job_details
        - 'link' in job_details
        - 'fragmented_desc' in job_details
        - 'full_desc' in job_details
        - 'skills' in job_details
        - 'latitutde' in job_details
        - 'longitude' in job_details
        - 'city' in job_details
        - 'country' in job_details
        - 'pay_period' in self.job_details
        - 'pay' in self.job_details
        - 'job_id' in job_details
        - 'image_url' in job_details
        """
        self.job_details = job_details
        self.decisions = self._get_decision_bools()

    def __str__(self) -> str:
        """
        Returns the string representation of this job, which is simply the job id.
        """
        return self.job_details["job_id"]

    def _check_keyword(self, keyword: str) -> bool:
        """
        Returns whether <keyword> is in at least one of
        the job title, fragmented description, or full description.
        """
        if keyword in str.lower(self.job_details["job_title"]):
            return True
        elif keyword in str.lower(self.job_details["fragmented_desc"]):
            return True
        elif keyword in str.lower(self.job_details["full_desc"]):
            return True
        else:
            return False

    def _check_remote(self) -> bool:
        """
        Returns whether this Job instance is remote.
        """
        return self._check_keyword("remote")

    def _check_frontend(self) -> bool:
        """
        Returns whether this Job instance is likely to be frontend.
        """
        return self._check_keyword("frontend") or self._check_keyword("front-end")

    def _check_fullstack(self) -> bool:
        """
        Returns whether this Job instance is likely to be fullstack.
        """
        if self._check_keyword("fullstack"):
            return True
        elif self._check_keyword("full-stack"):
            return True
        elif self._check_keyword("full stack"):
            return True

    def _get_decision_bools(self) -> list[bool]:
        """
        Canada, United States, or Don't Care? DONE
        Remote, Not Remote, or Don't Care? DONE
        Frontend, Backend, or Don't Care? DONE
        Would you like a rating score above 3 (Yes/No/Don't Care)? DONE
        Are you skilled at Python? (Yes/No/Don't Care) DONE
        Are you skilled at Java? (Yes/No/Don't Care) DONE
        Are you skilled at C/C++? (Yes/No/Don't Care) DONE
        """
        decisions = []
        if self.job_details["country"] == "United States":
            decisions.append(1)
        else:
            decisions.append(0)

        if self._check_remote():
            decisions.append(1)
        else:
            decisions.append(0)

        if self._check_fullstack():
            decisions.append(randint(0, 1))
        else:
            if self._check_frontend():
                decisions.append(1)
            else:
                decisions.append(0)

        if self.job_details["rating"] >= 3:
            decisions.append(1)
        else:
            decisions.append(0)

        if any(["python" == str.lower(skill) for skill in self.job_details["skills"]]):
            decisions.append(1)
        elif self._check_keyword("python"):
            decisions.append(1)
        else:
            decisions.append(0)

        if any(["java" == str.lower(skill) for skill in self.job_details["skills"]]):
            decisions.append(1)
        elif self._check_keyword("java"):
            decisions.append(1)
        else:
            decisions.append(0)

        if any(["c++" == str.lower(skill) for skill in self.job_details["skills"]]):
            decisions.append(1)
        elif self._check_keyword("c++"):
            decisions.append(1)
        else:
            decisions.append(0)

        return decisions
