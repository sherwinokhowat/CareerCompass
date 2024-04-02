from __future__ import annotations
from typing import Optional
from utility import similarity_calculation
from job import Job

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
# Decision Tree
# ====================================================================================


class DecisionTree:
    """A decision tree used to filter jobs based on certain preferences.

    Representation Invariants:
        - self._root is not None or self._subtrees == []
        - all(not subtree.is_empty() for subtree in self._subtrees)
    """

    _root: int | Job
    _subtrees: list[DecisionTree]

    def __init__(self, root: int | Job, subtrees: list[DecisionTree]) -> None:
        """Initialize a new Tree with the given root value and subtrees.

        Preconditions:
            - root is not none or subtrees == []
        """
        self._root = root
        self._subtrees = subtrees

    def is_empty(self) -> bool:
        """Return whether this tree is empty.

        >>> t1 = DecisionTree(None, [])
        >>> t1.is_empty()
        True
        >>> t2 = DecisionTree(3, [])
        >>> t2.is_empty()
        False
        """
        return self._root is None

    def insert_job(self, items: list[int | Job]) -> None:
        """
        [1,0,1,1,1,1,0, Jobinstance]
        """
        if not self._subtrees and items:  # tree is a single value
            self._subtrees.append(DecisionTree(items.pop(0), []))
            self._subtrees[0].insert_job(items)
        elif items:  # tree has at least one subtree
            found = False
            for subtree in self._subtrees:
                if not found and subtree._root == items[0]:
                    found = True
                    subtree.insert_job(items[1:])

            if not found:
                self._subtrees.append(DecisionTree(items.pop(0), []))
                self._subtrees[-1].insert_job(items)

    def get_jobs_by_answer(self, answers: list[int]) -> set[Job]:
        """
        This function returns the list of jobs according ot the information given by the questionaire
        and returns a set of Job instances determined when reading the file.

        The index is the value at which we look for a number equal to or greater than it.
        """
        list_so_far = []
        roots = self._traverse_path(answers)
        for root in roots:
            for job_id_vertex in root._subtrees:
                list_so_far.append(job_id_vertex._root)

        return set(list_so_far)

    def _traverse_path(self, inputs: list[int]) -> list[DecisionTree]:
        """
        returns the node right after traversing the inputs. That is, when going down each node, each root
        must equal to the correct index of the inputs.

        Note: The first step of traversal is after the _root of the tree. Since with animal decision trees
        the first node is only a placeholder.
        """
        if self.is_empty():
            return []
        elif not self._subtrees:  # tree is a single value
            return []
        elif inputs:  # tree has at least one subtree
            if inputs[0] == 2:
                list_of_vertices = []
                for subtree in self._subtrees:
                    list_of_vertices += subtree._traverse_path(inputs[1:])
                return list_of_vertices
            else:
                for subtree in self._subtrees:
                    if subtree._root == inputs[0]:
                        return subtree._traverse_path(inputs[1:])
                return [DecisionTree(None, [])]
        else:
            return [self]
