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


class BacktrackAlgorithm(object):

    def __init__(self, dom_file: str, problem_file: str, plan_length):
        self._csp = Encoder(dom_file, problem_file, plan_length).csp

    def __call__(self, assignments: Optional[List[Assignment]],
                 unassigned_variables: Optional[Set]) -> \
            Optional[List[Assignment]]:
        if assignments is None:
            assignments = []
        if unassigned_variables is None:
            unassigned_variables = self._csp.variables

        if unassigned_variables == set():
            return assignments

        variable = unassigned_variables.pop()
        domains = self._csp.domains[variable]

        # update domains by checking constraints
        updated_domains = self._get_updated_domains(variable,
                                                    domains,
                                                    assignments,
                                                    self._csp.constraints)

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
        if not assignments:
            return []

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
        if not assignments:
            return domains

        updated_domains = set()
        relevant_constraints = self._get_relevant_constraints(variable,
                                                              assignments,
                                                              constraints)
        for relevant_constraint in relevant_constraints:
            # 1. self constraint
            if len(relevant_constraint) == 1:
                for assignment in relevant_constraint:
                    if assignment.variable == variable:
                        updated_domains.add(assignment.value)

            # 2. others
            for assignment in relevant_constraint:
                for assignment2 in assignments:
                    if assignment.variable == assignment2.variable and \
                            assignment.value == assignment2.value:
                        val = self._get_value_from_constraint(
                            relevant_constraint, variable)
                        updated_domains.add(val)

        return updated_domains


if __name__ == "__main__":
    bt_algo = BacktrackAlgorithm('../domain/dock-worker-robot-domain.pddl',
                                 '../domain/dock-worker-robot-problem.pddl',
                                 6)
    solution = bt_algo(None, None)
    action_solutions = []
    for sol in solution:
        if sol.variable[1] == 'act':
            action_solutions.append(sol)
    print(action_solutions)
