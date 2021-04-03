# planning_csps
AI Planning using Constraint Satisfaction Problems.

## Example

### PDDL for representing planning domain and problem
The Dock-Worker Robots Domain and Problem are provided in the [domain](domain) directory.
There are also Simple Domain and Problem in the same directory.
You can create your PDDL files, or you can download them from the internet.

### Use as a CLI Script
You can execute the script directly by passing it the required arguments which are:
* path to the domain file
* path to the problem file
* length of plan

example:
```commandline
python3 csp.py -d ../domain/dock-worker-robot-domain.pddl -p ../domain/dock-worker-robot-problem.pddl -l 4 --print
```

## Issues
Please report issues if you found bugs or raise a Pull Request.