from functools import wraps
from typing import Dict, Set
from z3 import *


# TODO can probably do this in a nicer way using EnumSort, but want to be able to do addition
# An enum would probably make output more readable ('Innocent' and 'Criminal' instead of 0 and 1)
INNOCENT = 0
CRIMINAL = 1


def role_to_str(role):
    return "Innocent" if role == INNOCENT else "Criminal"


def Even(x):
    q = FreshInt()
    return Exists([q], x == 2 * q)


def Odd(x):
    return Not(Even(x))


class ClueSolver:
    known: Set
    s: Solver
    people: Dict

    def __init__(self, grid):
        self.known = set()
        self.s = Solver()
        self.grid = grid
        self.people = {person: Int(person) for row in grid for person in row}
        for p in self.people.values():
            self.s.add(Or(p == INNOCENT, p == CRIMINAL))

    def find_new_info(self):
        new_info = False
        for p in self.people.values():
            if p in self.known:
                continue
            for role in [INNOCENT, CRIMINAL]:
                self.s.push()
                self.s.add(Not(p == role))
                if self.s.check() == unsat:
                    print(f"[+] {p} must be:", role_to_str(role), sep="\t")
                    self.known.add(p)
                    new_info = True
                self.s.pop()
        if not new_info:
            print("[!] No new information")

    def add(self, clue):
        print("... Adding clue:", clue, sep="\n")

        self.s.add(clue)
        if self.s.check() == unsat:
            print("[!] Inconsistent model! No possible solutions.")
            return
        self.find_new_info()
        print()
        if len(self.known) == len(self.grid[0]) * len(self.grid):
            print("Puzzle complete! All roles have been identified!")

    def find_person(self, person):
        for y, row in enumerate(self.grid):
            try:
                return y, row.index(str(person))
            except ValueError:
                continue
        raise Exception(f"Person {person} not found")

    def to_persons(generator):
        @wraps(generator)
        def wrapper(self, *args, **kwargs):
            return set([self.people[x] for x in generator(self, *args, **kwargs)])

        return wrapper

    def get_from_grid(self, *coordinates):
        for row, col in coordinates:
            if 0 <= row < len(self.grid) and 0 <= col < len(self.grid[row]):
                yield self.grid[row][col]

    @to_persons
    def neighbors(self, person):
        row, col = self.find_person(person)

        yield from self.get_from_grid(
            (row - 1, col - 1),
            (row - 1, col),
            (row - 1, col + 1),
            (row, col - 1),
            (row, col + 1),
            (row + 1, col - 1),
            (row + 1, col),
            (row + 1, col + 1),
        )

    @to_persons
    def above(self, person):
        row, col = self.find_person(person)
        yield from self.get_from_grid(*[(r, col) for r in range(0, row)])

    @to_persons
    def below(self, person):
        row, col = self.find_person(person)
        yield from self.get_from_grid(
            *[(r, col) for r in range(row + 1, len(self.grid))]
        )

    @to_persons
    def right_of(self, person):
        row, col = self.find_person(person)
        yield from self.get_from_grid(
            *[(row, c) for c in range(col + 1, len(self.grid[row]))]
        )

    @to_persons
    def left_of(self, person):
        row, col = self.find_person(person)
        yield from self.get_from_grid(*[(row, c) for c in range(0, col)])

    @to_persons
    def corners(self):
        w = len(self.grid[0])
        h = len(self.grid)
        yield from self.get_from_grid((0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1))

    @to_persons
    def edges(self):
        w = len(self.grid[0])
        h = len(self.grid)
        edges = (
            [(0, col) for col in range(w)]
            + [(h - 1, col) for col in range(w)]
            + [(row, 0) for row in range(h)]
            + [(row, w - 1) for row in range(h)]
        )
        yield from sorted(self.get_from_grid(*(set(edges))))

    @to_persons
    def row(self, i):
        return self.grid[i - 1]

    @to_persons
    def column(self, a):
        col = ord(a.upper()) - ord("A")
        return [row[col] for row in self.grid]

    @staticmethod
    def num_innocents(people):
        return len(people) - sum(people)

    @staticmethod
    def num_criminals(people):
        return sum(people)

    def connected(self, role, column=None, row=None):
        if row is not None:
            people = self.row(row)
            before, after = self.left_of, self.right_of
        elif column is not None:
            people = self.column(column)
            before, after = self.above, self.below
        else:
            raise Exception("Specify either a row or a column")

        if role == CRIMINAL:
            num_role = self.num_criminals
        elif role == INNOCENT:
            num_role = self.num_innocents

        return And(
            *(
                Not(
                    And(
                        p == 1 - role,
                        num_role(before(p)) > 0,
                        num_role(after(p)) > 0,
                    )
                )
                for p in people
            )
        )
