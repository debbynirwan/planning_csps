"""CSP Backtracking Algorithm

Description:
    This module solves a CSP given to it, if any.

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
from encoder import Encoder, Assignment
from typing import List, Optional, Set, Tuple, Dict
import itertools


class BacktrackAlgorithm(object):

    def __init__(self, dom_file: str, problem_file: str, plan_length):
        self._csp = Encoder(dom_file, problem_file, plan_length).csp

    def __call__(self, assignments: Optional[List[Assignment]],
                 unassigned_variables: Optional[Set]) -> \
            Optional[List[Assignment]]:

        if unassigned_variables is None:
            unassigned_variables = self._csp.variables

        if assignments is None:
            assignments = []
            for constraint in self._csp.constraints:
                if len(constraint) == 1:
                    assignments.append(constraint[0])
                    unassigned_variables.remove(constraint[0].variable)

        if unassigned_variables == set():
            return assignments

        variable = unassigned_variables.pop()
        domains = self._csp.domains[variable]

        print(f"Assigning variable {variable}")

        # update domains by checking constraints
        updated_domains = self._get_updated_domains(variable,
                                                    domains,
                                                    assignments,
                                                    self._csp.constraints)

        print(f"Updated domains {updated_domains}")

        if updated_domains == set():
            # cannot assign value to variable, no solution available
            return None

        # nondeterministically choose a value from domains
        for value in updated_domains:
            assgn = Assignment()
            assgn.variable = variable
            assgn.value = value
            assignments.append(assgn)
            final_assignments = self.__call__(assignments,
                                              unassigned_variables)
            if final_assignments is None:
                assignments.remove(assgn)
            else:
                return final_assignments

        return None

    @staticmethod
    def _variable_in_constraint(variable, constraint, assignments) -> bool:
        var_found = False
        for assignment in constraint:
            if assignment.variable == variable:
                var_found = True
                break
        if not var_found:
            return False
        else:
            for assignment in constraint:
                for assignment2 in assignments:
                    if assignment.variable == assignment2.variable:
                        return True
        return False

    def _get_relevant_constraints(self, variable, assignments, constraints):
        relevant_constraints: List[Tuple[Assignment]] = []
        for constraint in constraints:
            if self._variable_in_constraint(variable, constraint, assignments):
                relevant_constraints.append(constraint)
        return relevant_constraints

    @staticmethod
    def _get_value_from_constraint(constraint, variable):
        for assignment in constraint:
            if assignment.variable == variable:
                return assignment.value
        return None

    def _get_updated_domains(self, variable, domains, assignments,
                             constraints):
        updated_domains = set()
        relevant_constraints = self._get_relevant_constraints(variable,
                                                              assignments,
                                                              constraints)
        if not relevant_constraints:
            return domains

        domain_assignments = []
        for value in domains:
            domain_assignments.append(Assignment(variable, value))
        for pair in list(itertools.product(domain_assignments, assignments)):
            for constraint in relevant_constraints:
                if pair[0] in constraint and pair[1] in constraint:
                    updated_domains.add(pair[0].value)

        return updated_domains


if __name__ == "__main__":
    bt_algo = BacktrackAlgorithm('../domain/dock-worker-robot-domain.pddl',
                                 '../domain/dock-worker-robot-problem.pddl',
                                 1)
    solution = bt_algo(None, None)
    if solution:
        action_solutions = []
        for sol in solution:
            if sol.variable[1] == 'act':
                action_solutions.append(sol)
        import pprint
        pprint.pp(action_solutions)
    else:
        print("Failed")
