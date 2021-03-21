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

    def __init__(self):
        self.variable = None
        self.value = None

    def __repr__(self):
        return f'{self.variable} = {self.value}'


class CSP(object):

    def __init__(self):
        self.variables: Set = set()
        self.constraints: List[Tuple[Assignment]] = []
        self.domains: Dict[Tuple, Set] = {}


class Encoder(object):

    def __init__(self, dom_file: str, problem_file: str, plan_length):
        self._plan_length = plan_length
        self._planning_problem = PlanningProblem(dom_file, problem_file)
        self._csp = self._encode()

    def _encode(self) -> CSP:
        csp = CSP()
        predicates = self._planning_problem.fluents
        actions = self._planning_problem.actions
        # 1. Variables and domains
        for predicate in predicates:
            if len(predicate) <= 1:
                continue
            for j in range(self._plan_length):
                if len(predicate) == 2:
                    var = (j, predicate[0])
                    csp.variables.add(var)
                    if var not in csp.domains:
                        csp.domains[var] = set()
                    csp.domains[var].add(True)
                    csp.domains[var].add(False)
                elif len(predicate) == 3:
                    var = (j, predicate[0], predicate[1])
                    csp.variables.add(var)
                    if var not in csp.domains:
                        csp.domains[var] = set()
                    csp.domains[var].add(predicate[2])

        for j in range(self._plan_length-1):
            var = (j, 'act')
            csp.variables.add(var)
            if var not in csp.domains:
                csp.domains[var] = set()
            for action in actions:
                if action.effect_pos.issubset(action.precondition_pos):
                    continue
                csp.domains[var].add(action)

        # 2. Initial State and Goal State Constraints
        for state in self._planning_problem.initial_state:
            if 'adjacent' in state:
                continue
            assignment = Assignment()
            if len(state) == 2:
                assignment.variable = (0, state[0])
                assignment.value = True
            elif len(state) == 3:
                assignment.variable = (0, state[0],
                                       state[1])
                assignment.value = state[2]
            csp.constraints.append((assignment, ))

        for state in self._planning_problem.goal_state:
            if 'adjacent' in state:
                continue
            assignment = Assignment()
            if len(state) == 2:
                assignment.variable = (self._plan_length, state[0])
                assignment.value = True
            elif len(state) == 3:
                assignment.variable = (self._plan_length, state[0],
                                       state[1])
                assignment.value = state[2]
            csp.constraints.append((assignment, ))

        # 3. Actions Constraints
        for action in actions:
            if action.effect_pos.issubset(action.precondition_pos):
                continue
            constraint = tuple()
            for j in range(self._plan_length):
                act_assignment = Assignment()
                act_assignment.variable = (j, 'act')
                act_assignment.value = action
                constraint += (act_assignment, )
                for precondition in action.precondition_pos:
                    if 'adjacent' in precondition:
                        continue
                    assignment = Assignment()
                    if len(precondition) == 2:
                        assignment.variable = (j, precondition[0])
                        assignment.value = True
                    elif len(precondition) == 3:
                        assignment.variable = (j, precondition[0],
                                               precondition[1])
                        assignment.value = precondition[2]
                    constraint += (assignment,)
                for effect in action.effect_pos:
                    assignment = Assignment()
                    if len(effect) == 2:
                        assignment.variable = (j+1, effect[0])
                        assignment.value = True
                    elif len(effect) == 3:
                        assignment.variable = (j+1, effect[0],
                                               effect[1])
                        assignment.value = effect[2]
                    constraint += (assignment,)
                for effect in action.effect_neg:
                    assignment = Assignment()
                    if len(effect) > 2:
                        continue
                    assignment.variable = (j+1, effect[0])
                    assignment.value = False
                    constraint += (assignment,)
                csp.constraints.append(constraint)

        # 4. Frame Axioms Constraints
        for action in actions:
            if action.effect_pos.issubset(action.precondition_pos):
                continue
            constraint = tuple()
            for j in range(self._plan_length):
                pass
            '''fluents - effect_pos and fluents - effect_neg_boolean_only'''



        print("done")


        return csp


if __name__ == "__main__":

    enc = Encoder('../domain/dock-worker-robot-domain.pddl',
                  '../domain/dock-worker-robot-problem.pddl',
                  2)
