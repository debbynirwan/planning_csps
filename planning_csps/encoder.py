"""Encoder

Description:
    This module encodes Planning Problem into Constraint Satisfaction Problem

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
from pddl_adapter import PlanningProblem
from typing import Dict, Tuple, Set, List


class Assignment(object):

    def __init__(self, variable=None, value=None):
        self.variable = variable
        self.value = value

    def __repr__(self):
        return f'{self.variable} = {self.value}'

    def __eq__(self, other):
        if self.variable == other.variable and self.value == other.value:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.variable) + hash(self.value)


class PlanningCSP(object):

    def __init__(self):
        self.variables: Set = set()
        self.constraints: List[Tuple[Assignment]] = []
        self.domains: Dict[Tuple, Set] = {}

    def __repr__(self):
        csp_print = f"vars = {self.variables}\n" \
                    f"domains = {self.domains}\n" \
                    f"constraints = {self.constraints}"
        return csp_print

    def variables_at_step(self, step: int, exclude_action: bool = True) -> Set:
        variables = set()
        for variable in self.variables:
            if variable[0] == step:
                if not exclude_action or variable[1] != 'act':
                    variables.add(variable)
        return variables


class Encoder(object):

    def __init__(self, dom_file: str, problem_file: str, plan_length):
        self._plan_length = plan_length
        self._planning_problem = PlanningProblem(dom_file, problem_file)
        self._csp = self._encode()

    @property
    def csp(self):
        return self._csp

    def _encode(self) -> PlanningCSP:
        csp = PlanningCSP()
        predicates = self._planning_problem.fluents
        actions = self._planning_problem.actions
        # 1. Variables and domains
        for predicate in predicates:
            if len(predicate) <= 1:
                continue
            for j in range(self._plan_length + 1):
                var = (j, predicate[0], predicate[1])
                csp.variables.add(var)
                if var not in csp.domains:
                    csp.domains[var] = set()
                if len(predicate) == 2:
                    csp.domains[var].add(True)
                    csp.domains[var].add(False)
                elif len(predicate) == 3:
                    csp.domains[var].add(predicate[2])

        for j in range(self._plan_length):
            var = (j, 'act')
            csp.variables.add(var)
            if var not in csp.domains:
                csp.domains[var] = set()
            for action in actions:
                if action.effect_pos.issubset(action.precondition_pos):
                    continue
                csp.domains[var].add(action)

        # 2. Initial State and Goal State Unary Constraints
        for state in self._planning_problem.initial_state:
            if 'adjacent' in state:
                continue
            assignment = Assignment()
            assignment.variable = (0, state[0], state[1])
            if len(state) == 2:
                assignment.value = True
            elif len(state) == 3:
                assignment.value = state[2]
            csp.constraints.append((assignment,))

        for state in self._planning_problem.goal_state:
            if 'adjacent' in state:
                continue
            assignment = Assignment()
            assignment.variable = (self._plan_length, state[0], state[1])
            if len(state) == 2:
                assignment.value = True
            elif len(state) == 3:
                assignment.value = state[2]
            csp.constraints.append((assignment,))

        # 3. Actions (Binary) Constraints
        for action in actions:
            if action.effect_pos.issubset(action.precondition_pos):
                continue
            for j in range(self._plan_length):
                act_assignment = Assignment()
                act_assignment.variable = (j, 'act')
                act_assignment.value = action
                for precondition in action.precondition_pos:
                    if 'adjacent' in precondition:
                        continue
                    constraint = tuple()
                    constraint += (act_assignment,)
                    assignment = Assignment()
                    assignment.variable = (j, precondition[0], precondition[1])
                    if len(precondition) == 2:
                        assignment.value = True
                    elif len(precondition) == 3:
                        assignment.value = precondition[2]
                    constraint += (assignment,)
                    csp.constraints.append(constraint)
                for effect in action.effect_pos:
                    constraint = tuple()
                    constraint += (act_assignment,)
                    assignment = Assignment()
                    assignment.variable = (j + 1, effect[0], effect[1])
                    if len(effect) == 2:
                        assignment.value = True
                    elif len(effect) == 3:
                        assignment.value = effect[2]
                    constraint += (assignment,)
                    csp.constraints.append(constraint)
                for effect in action.effect_neg:
                    constraint = tuple()
                    constraint += (act_assignment,)
                    assignment = Assignment()
                    if len(effect) > 2:
                        continue
                    assignment.variable = (j + 1, effect[0])
                    assignment.value = False
                    constraint += (assignment,)
                    csp.constraints.append(constraint)

        # 4. Frame Axioms Constraints
        for action in actions:
            if action.effect_pos.issubset(action.precondition_pos):
                continue
            for j in range(self._plan_length):
                effect_vars = set()
                for predicate in (action.effect_pos | action.effect_neg):
                    effect_vars.add((j, predicate[0], predicate[1]))
                invariants = csp.variables_at_step(j) - effect_vars
                for invariant in invariants:
                    for value in csp.domains[invariant]:
                        act_assignment = Assignment()
                        act_assignment.variable = (j, 'act')
                        act_assignment.value = action
                        assignment_bef = Assignment()
                        assignment_aft = Assignment()
                        constraint = tuple()
                        constraint += (act_assignment,)
                        assignment_bef.variable = (invariant[0],
                                                   invariant[1],
                                                   invariant[2])
                        assignment_bef.value = value
                        assignment_aft.variable = (invariant[0] + 1,
                                                   invariant[1],
                                                   invariant[2])
                        assignment_aft.value = value
                        constraint += (assignment_bef, assignment_aft)
                        csp.constraints.append(constraint)
        return csp
