"""
CSC111 Winter 2024: Internship Finder

DESCRIPTION OF MODULE HERE.

Copyright and Usage Information
===============================
This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2024 Sherwin Okhowat
"""

from __future__ import annotations
from typing import Any, Optional
from math import e, acos, sin, cos, pi
import csv


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
    """

    job_details: dict[str, Any]
    remote: bool

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
        self.remote = self._check_remote()

    def __str__(self) -> str:
        """
        Returns the string representation of this job, which is simply the job id.
        """
        return self.job_details["job_id"]

    def _check_remote(self) -> bool:
        """
        Returns whether this Job instance is remote.
        """
        if "remote" in str.lower(self.job_details["job_title"]):
            return True
        elif "remote" in str.lower(self.job_details["fragmented_desc"]):
            return True
        elif "remote" in str.lower(self.job_details["full_desc"]):
            return True
        else:
            return False


class _WeightedVertex:
    """
    Class representing a weighted vertex for a weighted graph.

    Instance Attributes:
    - item: The Job instance this weighted vertex represents.
    - neighbours: The vertices adjacent to this vertex, and their corresponding edge's weight.

    Preconditions:
    - self not in self.neighbours
    - all([self in u.neighbours for u in self.neighbours])
    """

    item: Job
    neighbours: dict[_WeightedVertex, float]

    def __init__(self, item: Job) -> None:
        """
        Initialize a new weighted vertex with the given Job.
        """
        self.item = item
        self.neighbours = {}

    def calculate_similarity(self, other: _WeightedVertex) -> float:
        """
        Returns the similarity score (i.e., the weight) of <self> and <other>.
        """
        return similarity_calculation(self.item, other.item)


# ====================================================================================
# Weighted Graph
# ====================================================================================


class WeightedGraph:
    """
    Class representing a weighted graph used to represent each job posting and their similarity
    score to the other job postings.
    """

    _vertices: dict[Job, _WeightedVertex]

    def __init__(self) -> None:
        """
        Initializes a WeightedGraph instance.
        """
        self._vertices = {}

    def add_vertex(self, job: Job) -> None:
        """
        Adds a vertex to this weighted graph instance.
        """
        if job not in self._vertices:
            self._vertices[job] = _WeightedVertex(job)

    def add_edge(self, job1: Job, job2: Job) -> None:
        """
        Adds an edge between job1 and job2 in this weighted graph instance.
        """
        if job1 not in self._vertices or job2 not in self._vertices:
            raise ValueError(
                f"<{str(job1)}> or <{str(job2)}> is not a vertex in this graph!"
            )
        else:
            v1, v2 = self._vertices[job1], self._vertices[job2]
            assert v1.calculate_similarity(v2) == v2.calculate_similarity(v1)

            similarity = v1.calculate_similarity(v2)
            v1.neighbours[v2], v2.neighbours[v1] = similarity, similarity

    def get_similarity(self, job1: Job, job2: Job) -> float:
        """
        Returns the similarity score between job1 and job2.
        """
        return self._vertices.get(
            self._vertices[job1].neighbours[self._vertices[job2]], 0
        )

    def get_similar_jobs(self, job: Job, limit: Optional[int] = 5) -> list[Job]:
        """
        Returns the <limit> jobs with the highest similarity score to <job>.
        """
        if job not in self._vertices:
            raise ValueError("Job does not exist in this <WeightedGraph> instance!")

        job_vertex = self._vertices[job]
        sorted_jobs = sorted(
            job_vertex.neighbours.items(), key=lambda item: item[1], reverse=True
        )

        return [neighbour_vertex.item for neighbour_vertex, _ in sorted_jobs[:limit]]

    def get_vertices(self) -> dict[Job, _WeightedVertex]:
        """
        Returns self._vertices.
        """
        return self._vertices


# ====================================================================================
# Load CSV
# ====================================================================================


def load_jobs_csv() -> list[Job]:
    """
    Returns a list of Job instances representing every job in <jobs.csv>.

    Note that duplicates are filtered out!
    """
    ids = set()
    jobs = []
    with open("jobs.csv", "r", newline="") as csvfile:
        job_reader = csv.reader(csvfile)
        next(job_reader)
        for row in job_reader:
            try:
                job_details = {
                    "job_title": row[0],
                    "employer_name": row[1],
                    "rating": float(row[2]),
                    "link": row[3],
                    "fragmented_desc": row[4],
                    "full_desc": row[5],
                    "skills": row[6],
                    "latitutde": float(row[7]),
                    "longitude": float(row[8]),
                    "city": row[9],
                    "country": row[10],
                    "pay_period": row[11],
                    "pay": float(row[12]),
                    "job_id": row[13],
                    "image_url": row[14],
                }
                if job_details["job_id"] not in ids:
                    jobs.append(Job(job_details))
                    ids.add(job_details["job_id"])
            except ValueError:
                continue
    return jobs


def load_job_graph() -> WeightedGraph:
    """
    Returns a <WeightedGraph> of every job stored in <jobs.csv>.
    """
    g = WeightedGraph()
    jobs = load_jobs_csv()

    for job in jobs:
        g.add_vertex(job)

    for job1 in jobs:  # no optimization available :(
        for job2 in jobs:
            if job1 != job2:
                g.add_edge(job1, job2)

    return g


# ====================================================================================
# Computation
# ====================================================================================


def sigmoid(x: float, scale_factor: Optional[int] = 1) -> float:
    """
    Returns the value of f(x) = scale_factor/(1 + e^(-x)).
    """
    try:
        return scale_factor / (1 + e ** (-x))
    except ValueError:
        print(x)
        return 0


def deg_to_rad(degrees: float) -> float:
    """
    Converts <degrees> into radians and returns it.
    """
    return degrees * (pi / 180.0)


def calculate_distance(
    coords1: tuple[float, float], coords2: tuple[float, float]
) -> float:
    """
    Calculates and returns the distance in km between the two coordinates using
    an approximated veresion of the harversine formula.

    Note that although this is an approximation, it takes into account the Earth's spherical shape.
    You can learn more about the harvesine formula used here:
    https://en.wikipedia.org/wiki/Haversine_formula.

    Preconditions:
    - coords1[0] and coords1[1] are the latitude and longitude of the coordinate respectively.
    - coords2[0] and coords2[1] are the latitude and longitude of the coordinate respectively.
    """
    lat1, lng1 = deg_to_rad(coords1[0]), deg_to_rad(coords1[1])
    lat2, lng2 = deg_to_rad(coords2[0]), deg_to_rad(coords2[1])
    cosine_angular_distance = (sin(lat1) * sin(lat2)) + (
        cos(lat1) * cos(lat2) * cos(lng2 - lng1)
    )
    clamped_value = max(min(cosine_angular_distance, 1), -1)
    distance = acos(clamped_value) * 6371
    return distance


def normalize_distance(job1: Job, job2: Job) -> float:
    """
    Returns a normalized distance between <job1> and <job2> between 0 and 1.

    The function used is a customly modified version of the sigmoid function,
    which is reflected across the y-axis and introduces a constant scaling factor
    for the distance. It is designed to result in a noramlization of 1 if the distance is 0,
    or near 0 if the distance approaches 'larger' values.

    The function used is f(d) =  2/(1 + e^(2d)

    >>> normalize_distance(0.0)
    1.000
    >>> normalize_distance(10000.0)
    0.000
    """
    coords1 = (job1.job_details["latitutde"], job1.job_details["longitude"])
    coords2 = (job2.job_details["latitutde"], job2.job_details["longitude"])
    distance = calculate_distance(coords1, coords2)
    return sigmoid(x=(-2 * distance / 1000.0), scale_factor=2)


def normalize_country(job1: Job, job2: Job) -> float:
    """
    Returns a normalized similarity value for <job1> and <job2> based on whether they are the same.
    """
    if job1.job_details["country"] == job2.job_details["country"]:
        return 0.8
    else:
        return 0


def normalize_rating(job1: Job, job2: Job) -> float:
    """
    Returns a normalized similarity value based on <job1> and <job2> ratings.
    """
    rating1, rating2 = job1.job_details["rating"], job2.job_details["rating"]
    return sigmoid(x=(-0.6 * abs(rating1 - rating2)), scale_factor=2)


def normalize_skills(job1: Job, job2: Job) -> float:
    """
    Returns a normalized similarity value based on the number of intersecting
    skills between <job1> and <job2>.
    """
    skills1 = set(job1.job_details["skills"])
    skills2 = set(job2.job_details["skills"])
    num_intersecting = len(set.intersection(skills1, skills2))
    return sigmoid(num_intersecting - 2)


def normalize_pay(job1: Job, job2: Job) -> float:
    """
    Returns a normalized similarity value based on <job1> and <job2> pay
    similarity.
    """
    if job1.job_details["pay_period"] == "HOURLY":
        estimated_salary1 = 40 * 52 * job1.job_details["pay"]
    else:
        estimated_salary1 = job1.job_details["pay"]

    if job2.job_details["pay_period"] == "HOURLY":
        estimated_salary2 = 40 * 52 * job2.job_details["pay"]
    else:
        estimated_salary2 = job2.job_details["pay"]

    var = abs((estimated_salary1 - estimated_salary2)) / 1000.0
    return sigmoid(x=(-0.75 * var), scale_factor=2)


def similarity_calculation(job1: Job, job2: Job) -> float:
    """
    This function is used to calculate the similarity score between two jobs.
    The similarity score is calculated based on a number of metrics.
    These metrics include:
    - Their distance from each other COMPLETE
    - Rating COMPLETE
    - Country COMPLETE
    - The similarity in pay COMPLETE
    - Skills COMPLETE
    - Job description ? Compare how many keywords there are
    - Etc
    """
    weights = [0.2, 0.3, 0.1, 0.15, 0.2, 0.05]
    normalized_distance = normalize_distance(job1, job2) * weights[0]
    normalized_country = normalize_country(job1, job2) * weights[1]
    normalized_rating = normalize_rating(job1, job2) * weights[2]
    normalized_skills = normalize_skills(job1, job2) * weights[3]
    normalized_pay = normalize_pay(job1, job2) * weights[4]
    normalized_description = 0 * weights[5]  # set to 0 for testing purposes

    similarity = (
        normalized_distance
        + normalized_country
        + normalized_rating
        + normalized_skills
        + normalized_pay
        + normalized_description
    )

    return similarity


# ====================================================================================
# Main Function
# ====================================================================================

if __name__ == "__main__":
    import python_ta

    # Need to read documentation to modify !
    # python_ta.check_all(
    #     config={
    #         "max-line-length": 100,
    #         "disable": ["E1136"],
    #         "extra-imports": ["csv", "networkx"],
    #         "allowed-io": ["load_review_graph"],
    #         "max-nested-blocks": 4,
    #     }
    # )

    graph = load_job_graph()
