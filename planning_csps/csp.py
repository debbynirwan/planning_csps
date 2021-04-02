"""CSP Backtracking Algorithm

Description:
    This module solves a CSP given to it, if any.
    The CSP code is from: https://freecontent.manning.com/constraint-satisfaction-problems-in-python/

License:
    Copyright 2021 Debby Nirwan

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
from encoder import Encoder, Assignment


class Constraint(ABC):

    def __init__(self, variables: List[Tuple]) -> None:
        self.variables: List[Tuple] = variables

    @abstractmethod
    def satisfied(self, assignments, variable) -> bool:
        ...


class CSP(object):

    def __init__(self, variables, domains) -> None:
        self.variables = variables
        self.domains = domains
        self.constraints = {}
        for variable in self.variables:
            self.constraints[variable] = []
            if variable not in self.domains:
                raise LookupError("Every variable should have a domain "
                                  "assigned to it.")

    def add_constraint(self, constraint) -> None:
        for variable in constraint.variables:
            if variable not in self.variables:
                raise LookupError("Variable in constraint not in CSP")
            else:
                self.constraints[variable].append(constraint)

    def consistent(self, variable, assignment) -> bool:
        for constraint in self.constraints[variable]:
            if not constraint.satisfied(assignment, variable):
                return False
        return True

    def backtracking_search(self, assignment=None) -> Optional[Dict]:

        if assignment is None:
            assignment = {}
        if len(assignment) == len(self.variables):
            return assignment

        unassigned = [v for v in self.variables if v not in assignment]
        unassigned.sort(key=lambda tup: tup[0])

        first = unassigned[0]
        for value in self.domains[first]:
            local_assignment = assignment.copy()
            local_assignment[first] = value
            if self.consistent(first, local_assignment):
                result = self.backtracking_search(local_assignment)
                if result is not None:
                    return result
        return None


class UnaryConstraint(Constraint):

    def __init__(self, action_constraint: Tuple[Assignment]):
        self.constraints: List[Assignment] = list(action_constraint)
        variables: List[Tuple] = []
        for assignment in self.constraints:
            variables.append(assignment.variable)
        super().__init__(variables)

    def satisfied(self, assignments, variable) -> bool:
        constraint = self.constraints[0]

        if constraint.variable != variable:
            return True

        if constraint.value == assignments[variable]:
            return True
        else:
            return False


class ActionsConstraint(Constraint):

    def __init__(self, action_constraint: Tuple[Assignment]):
        self.constraints: List[Assignment] = list(action_constraint)
        variables: List[Tuple] = []
        for assignment in self.constraints:
            variables.append(assignment.variable)
        super().__init__(variables)

    def satisfied(self, assignments, variable) -> bool:
        constraint1 = self.constraints[0]
        constraint2 = self.constraints[1]

        # variable is act
        if variable == constraint1.variable:
            if assignments[variable] != constraint1.value:
                return True
            # Has constraint2.variable been assigned?
            for var, value in assignments.items():
                if var == constraint2.variable:
                    if value == constraint2.value:
                        return True
                    else:
                        return False
            # constraint2 has not been assigned
            return True

        if variable == constraint2.variable:
            for var, value in assignments.items():
                if var == constraint1.variable:
                    if value == constraint1.value:
                        if assignments[variable] == constraint2.value:
                            return True
                        else:
                            return False
                    else:
                        # act(j) != constraint
                        return True
            # constraint1 has not been assigned
            return True


class FrameAxiomsConstraint(Constraint):

    def __init__(self, frame_axiom_constraint: Tuple[Assignment]):
        self.constraints: List[Assignment] = list(frame_axiom_constraint)
        variables: List[Tuple] = []
        for assignment in self.constraints:
            variables.append(assignment.variable)
        super().__init__(variables)

    def satisfied(self, assignments, variable) -> bool:

        if 'act' in variable:
            # we are not restricting action
            return True

        # act must have been assigned for this constraint to be valid
        constraint1 = self.constraints[0]
        constraint2 = self.constraints[1]
        constraint3 = self.constraints[2]

        if constraint1.variable not in assignments:
            # act(j) has not been assigned
            return True

        if assignments[constraint1.variable] != constraint1.value:
            # irrelevant constraint
            return True

        if variable == constraint2.variable:
            if assignments[constraint2.variable] != constraint2.value:
                return True
            if constraint3.variable not in assignments:
                # act(j) has not been assigned
                return True
            if assignments[constraint3.variable] == constraint3.value:
                return True
            else:
                return False

        if variable == constraint3.variable:
            if assignments[constraint3.variable] != constraint3.value:
                return True
            if constraint2.variable not in assignments:
                # act(j) has not been assigned
                return True
            if assignments[constraint2.variable] == constraint2.value:
                return True
            else:
                return False

        return True


if __name__ == "__main__":
    encoder = Encoder('../domain/dock-worker-robot-domain.pddl',
                      '../domain/dock-worker-robot-problem.pddl',
                      4)
    csp = CSP(encoder.csp.variables, encoder.csp.domains)
    initial_assignments = {}
    for constr in encoder.csp.constraints:
        if len(constr) == 1:
            csp.add_constraint(UnaryConstraint(constr))
        elif len(constr) == 2:
            csp.add_constraint(ActionsConstraint(constr))
        elif len(constr) == 3:
            csp.add_constraint(FrameAxiomsConstraint(constr))
        else:
            raise ValueError(f"Unexpected constraint with length "
                             f"= {len(constr)}")
    solution = csp.backtracking_search(initial_assignments)
    if solution is None:
        print("No solution found!")
    else:
        import pprint

        pp = pprint.PrettyPrinter()
        pp.pprint(solution)
