from typing import Optional, Any
from job import Job
from math import e, acos, sin, cos, pi
import csv

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
    elif job1.job_details["pay_period"] == "MONTHLY":
        estimated_salary1 = 12 * job1.job_details["pay"]
    else:
        estimated_salary1 = job1.job_details["pay"]

    if job2.job_details["pay_period"] == "HOURLY":
        estimated_salary2 = 40 * 52 * job2.job_details["pay"]
    elif job2.job_details["pay_period"] == "MONTHLY":
        estimated_salary2 = 12 * job2.job_details["pay"]
    else:
        estimated_salary2 = job2.job_details["pay"]

    var = abs((estimated_salary1 - estimated_salary2)) / 1000.0
    return sigmoid(x=(-0.75 * var), scale_factor=2)


def normalize_descriptions(job1: Job, job2: Job) -> float:
    """
    Returns a normalized similarity value based on the number
    of common words in <job1> and <job2> descriptions.
    """
    return 0.0


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
# Loading Functions
# ====================================================================================


def load_jobs_csv() -> list[Job]:
    """
    Returns a list of Job instances representing every job in <jobs.csv>.

    Note that duplicates are filtered out as a precautionary measure!
    """
    ids = set()
    jobs = []
    with open("jobs.csv", "r", newline="", encoding="utf-8") as csvfile:
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
                    "skills": row[5],
                    "latitutde": float(row[6]),
                    "longitude": float(row[7]),
                    "city": row[8],
                    "country": row[9],
                    "pay_period": row[10],
                    "pay": float(row[11]),
                    "job_id": row[12],
                    "full_desc": row[13],
                }
                if job_details["job_id"] not in ids:
                    jobs.append(Job(job_details))
                    ids.add(job_details["job_id"])
            except ValueError:
                continue
    return jobs


# ====================================================================================
# Writing to CSV Functions
# ====================================================================================


def write_csv(file: str, job_details: list) -> None:
    """
    A helper helper function for handle_jobs, which appends the information in the
    job_details list paramter to the csv file given.

    Preconditions:
    - file is a csv file
    """
    with open(file, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(job_details)


def clear_csv(file: str) -> None:
    """
    Clears the csv file associted to file.
    """
    column_names = [
        "job_title",
        "employer_name",
        "rating",
        "link",
        "fragmented_desc",
        "skills",
        "latitutde",
        "longitude",
        "city",
        "country",
        "pay_period",
        "pay",
        "job_id",
        "full-desc",
    ]
    with open(file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(column_names)


def sanitize_details(job_details: list[Any]) -> None:
    """
    Sanitizes <job_details> into an appropriate format in order
    to encode <job_details> into a UTF-8 format writable by csv.
    """
    for i in range(len(job_details)):
        field = job_details[i]
        if isinstance(field, str):
            job_details[i] = (
                field.replace("\u2010", "-").replace("\n", " ").replace("\r", " ")
            )
