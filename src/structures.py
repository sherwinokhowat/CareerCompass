"""
CSC111 Winter 2024 Course Project 2: CareerCompass

This Python module contains the data structures necessary for
our application to function including a decision tree and weighted graph.

Copyright and Usage Information
===============================
This file is provided solely for the personal and private use of the instructors
and teaching assistants of CSC111 at the University of Toronto St. George campus.
All forms of distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright of these files,
please contact us through Github using the "contact" button within our application.

This file is Copyright (c) 2024 Sherwin Okhowat, Kush Gandhi, David Cen, Tony Qi.
"""

from __future__ import annotations
from typing import Optional
from random import sample
from src.utility import similarity_calculation, load_jobs_csv
from src.job import Job


# ====================================================================================
# Weighted Graph
# ====================================================================================


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


class WeightedGraph:
    """
    Class representing a weighted graph used to represent each job posting and their similarity
    score to the other job postings.

    Private Instance Attributes:
    - _vertices: The Job vertices in this graph.

    Representation Invariants:
    - all(job == self._vertices[job].job for job in self._vertices)
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

        Precondititions:
        - job1 != job2
        """
        v1 = self._vertices[job1]
        v2 = self._vertices[job2]

        return v1.neighbours.get(v2, 0)

    def get_similar_jobs(
        self, job: Job, limit: Optional[int] = 5, offset: Optional[int] = 10
    ) -> list[Job]:
        """
        Returns the <limit> jobs with the highest similarity score to <job>.

        The <offset>  offset introduced to introduce a 'random'
        aspect to the <limit> similar jobs retrieved.
        """
        if (offset + limit) > len(self):
            raise ValueError("Limit / Offset are too high!")
        elif job not in self._vertices:
            raise ValueError("Job does not exist in this <WeightedGraph> instance!")

        job_vertex = self._vertices[job]
        sorted_jobs = sorted(
            job_vertex.neighbours.items(), key=lambda item: item[1], reverse=True
        )

        similar_jobs = [
            neighbour_vertex.item for neighbour_vertex, _ in sorted_jobs[: limit + 10]
        ]

        return sample(similar_jobs, limit)

    def get_vertices(self) -> dict[Job, _WeightedVertex]:
        """
        Returns self._vertices.
        """
        return self._vertices

    def get_average_salary(self) -> int:
        """
        Returns the estimated average salary of all jobs
        stored in self._vertices.
        """
        total = 0.0
        for job in self._vertices:
            total += job.get_annual_pay()
        return int(total / len(self))

    def __len__(self) -> int:
        """
        Returns the length of this WeightedGraph instance.
        """
        return len(self._vertices)


# ====================================================================================
# Decision Tree
# ====================================================================================


class DecisionTree:
    """A decision tree used to filter jobs based on certain preferences.

    Representation Invariants:
        - self._root is not None or self._subtrees == []
        - all(not subtree.is_empty() for subtree in self._subtrees)

    Private Instance Attributes:
    - _root: The set of jobs stored at this DecisionTree's root
    - _left: The left subtree of this DecisionTree
    - _right: The right subtree of this DecisionTree
    """

    _root: set[Job]
    _left: Optional[DecisionTree] = None
    _right: Optional[DecisionTree] = None

    def __init__(self) -> None:
        """
        Initialize a DecisionTree instance.
        """
        self._root = set()

    def insert(self, job: Job, depth: int = 0) -> None:
        """
        Inserts <job> into the decision tree based on <job.decisions>.

        Preconditions:
        - all([i in {0, 1} for i in job.decisions])
        """
        decisions = job.decisions
        if len(decisions) == depth:
            if self._root is None:
                self._root = set()
            self._root.add(job)
        else:
            curr = decisions[0]
            if curr == 0:
                if self._left is None:
                    self._left = DecisionTree()
                self._left.insert(job, depth + 1)
            else:  # curr == 1
                if self._right is None:
                    self._right = DecisionTree()
                self._right.insert(job, depth + 1)

    def get_jobs(self, decisions: list[int]) -> set[Job]:
        """
        Returns the set of jobs in the tree corresponding to
        the path given by <decisions>. If not enough jobs
        correspond to the path, it randomly adjusts decisions
        until there are enough paths.
        """
        for i in range(len(decisions)):
            j = self.get_jobs_helper(decisions.copy())
            if len(j) >= 5:
                return j
            decisions[i] = 2
        return self.get_jobs_helper(decisions.copy())

    def get_jobs_helper(self, decisions: list[int]) -> set[Job]:
        """
        Returns the set of jobs in the tree corresponding to
        the path given by <decisions>.
        """
        if not decisions:
            return self._root
        else:
            curr = decisions.pop(0)
            if curr == 0:
                if self._left is None:
                    return set()
                return self._left.get_jobs(decisions)
            elif curr == 1:
                if self._right is None:
                    return set()
                return self._right.get_jobs(decisions)
            else:  # 2 => traverse both
                left = (
                    self._left.get_jobs(decisions) if self._left is not None else set()
                )
                right = (
                    self._right.get_jobs(decisions)
                    if self._right is not None
                    else set()
                )
                return set.union(left, right)


def load_graph_and_tree() -> tuple[WeightedGraph, DecisionTree]:
    """
    Returns a <WeightedGraph> of every job stored in <jobs.csv>.

    NOTE: Inherently, constructing a complete graph is O(n^2).
    """
    g = WeightedGraph()
    jobs = load_jobs_csv()
    new_tree = DecisionTree()
    for job in jobs:
        g.add_vertex(job)
        new_tree.insert(job)
    count = 0
    for job1 in jobs:  # no optimization available :(
        count += 1
        for job2 in jobs:
            if job1 != job2:
                g.add_edge(job1, job2)
    return g, new_tree


if __name__ == "__main__":
    import python_ta

    # NOTES FOR PYTHON-TA:
    python_ta.check_all(
        config={
            "max-line-length": 120,
            "extra-imports": ["typing", "random", "utility", "job"],
        }
    )
