"""CSC111 Exercise 2: Recursion with Lists and Trees

Module Description
==================
This module contains the Tree class we developed in this week's lectures, as well as
various methods and functions for you to implement as part of Exercise 2.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2024 UofT DCS Teaching Team
"""
from __future__ import annotations

import csv
from typing import Any, Optional

from python_ta.contracts import check_contracts


class DecisionTree:
    """A recursive tree data structure.

    NOTE: The tree will be ordered such that the categorical measures are on the top
    and numerical on the bottom.

    Representation Invariants:
        - self._root is not None or self._subtrees == []
        - all(not subtree.is_empty() for subtree in self._subtrees)
    """
    _root: Optional[Any]
    _subtrees: list[DecisionTree]

    def __init__(self, root: Optional[Any], subtrees: list[DecisionTree]) -> None:
        """Initialize a new Tree with the given root value and subtrees.

        If root is None, the tree is empty.

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

    def get_list_of_jobs(self, list_of_answers: list[int]) -> list[Any]:
        """
        This function returns the list of jobs according ot the information given by the questionaire
        and returns a set of Job instances determined when reading the file.

        The index is the value at which we look for a number equal to or greater than it.
        """
        list_so_far = []
        roots = self.traverse_path(list_of_answers)
        for root in roots:
            for job_id_vertex in root._subtrees:
                list_so_far.append(job_id_vertex._root)

        return list_so_far

    def traverse_path(self, inputs: [int]) -> list[DecisionTree]:
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
                    list_of_vertices += subtree.traverse_path(inputs[1:])
            else:
                for subtree in self._subtrees:
                    if subtree._root == inputs[0]:
                        return subtree.traverse_path(inputs[1:])
                return [DecisionTree(None, [])]
        else:
            return [self]

    def insert_sequence(self, items: list) -> None:
        """Insert the given items into this tree.

        The inserted items form a chain of descendants, where:
            - items[0] is a child of this tree's root
            - items[1] is a child of items[0]
            - items[2] is a child of items[1]
            - etc.

        Do nothing if items is empty.

        The root of this chain (i.e. items[0]) should be added as a new subtree within this tree, as long as items[0]
        does not already exist as a child of the current root node. That is, create a new subtree for it
        and append it to this tree's existing list of subtrees.

        If items[0] is already a child of this tree's root, instead recurse into that existing subtree rather
        than create a new subtree with items[0]. If there are multiple occurrences of items[0] within this tree's
        children, pick the left-most subtree with root value items[0] to recurse into.

        Hints:

        To do this recursively, you'll need to recurse on both the tree argument
        (from self to a subtree) AND on the given items, using the "first" and "rest" idea
        from RecursiveLists. To access the "rest" of a built-in Python list, you can use
        list slicing: items[1:len(items)] or simply items[1:], or you can use a recursive helper method
        that takes an extra "current index" argument to keep track of the next move in the list to add.

        Preconditions:
            - not self.is_empty()

        """
        if not self._subtrees and items:  # tree is a single value
            self._subtrees.append(DecisionTree(items.pop(0), []))
            self._subtrees[0].insert_sequence(items)
        elif items:  # tree has at least one subtree
            found = False
            for subtree in self._subtrees:
                if not found and subtree._root == items[0]:
                    found = True
                    subtree.insert_sequence(items[1:])

            if not found:
                self._subtrees.append(DecisionTree(items.pop(0), []))
                self._subtrees[-1].insert_sequence(items)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

    # import python_ta
    # python_ta.check_all('ex2_part2.py', config={
    #     'max-line-length': 120,
    #     'extra-imports': ['csv', 'random'],
    #     'allowed-io': ['build_decision_tree', 'get_user_input', 'run_animal_guesser']
    # })
