import argparse

# Load the variable domains
def load_variables(filepath):
  domains = {}
  with open(filepath, 'r') as file:
    for line in file:
      parts = line.strip().split(':')
      variable = parts[0].strip()
      values = [int(x) for x in parts[1].strip().split()]
      domains[variable] = values
  return domains

# Load the constraints on variables
def load_constraints(filepath):
  constraints = []
  operators = ['=', '!', '>', '<']  # define possible operators
  with open(filepath, 'r') as file:
    for line in file:
      op_index = -1
      op_char = ''
      for op in operators:  # find the operator in the line
        op_index = line.find(op)
        if op_index != -1:
          op_char = op
          break
      if op_index != -1:  # if an operator was found
        var1 = line[:op_index].strip()
        var2 = line[op_index+1:].strip()
        constraints.append((var1, op_char, var2))
  return constraints
    
# Create an undirected graph, implemented as a dict
def make_graph(domains, constraints):
  graph = {var: set() for var in domains}
  for var1, op, var2 in constraints:
    graph[var1].add(var2)
    graph[var2].add(var1)
  return graph

# A general check function
def evaluate_constraint(var1, val1, var2, val2, op):
  if op == '=':
    return val1 == val2
  elif op == '!':
    return val1 != val2
  elif op == '>':
    return val1 > val2
  elif op == '<':
    return val1 < val2
  else:
    raise ValueError(f"Unknown operator: {op}")
  
# A pairwise constraint check function for LCV heuristic,
# where order of variables var1, var2 does not matter  
def pairwise_constraints_check(var1, value1, var2, value2, constraints):
  for constraint in constraints:
    # Check for both possibilities
    if constraint[0] == var1 and constraint[2] == var2:
      if not evaluate_constraint(var1, value1, var2, value2, constraint[1]):
        result = False
      else:
        result = True
    elif constraint[2] == var1 and constraint[0] == var2:
      if not evaluate_constraint(var2, value2, var1, value1, constraint[1]):
        result = False
      else:
        result = True
  return result

# Check constraints after new assignment
def constraints_check(assignment, constraints):
  for var1, op, var2 in constraints:
    if var1 in assignment and var2 in assignment:
      if not evaluate_constraint(var1, assignment[var1], var2, assignment[var2], op):
        return False
  return True

# Heuristic to chose the variable
def get_variable(assignment, domains, graph):
  unassigned_vars = [v for v in domains if v not in assignment]
  # Sort based on MRV, then MCV, then alphabetically
  unassigned_vars.sort(key=lambda var: (
    len(domains[var]),  # Fewest legal values first
    -len([other_var for other_var in graph[var] if other_var not in assignment]),  # Most constraining variable
    var                 # Alphabetically
  ))
  return unassigned_vars[0]


# Heurisitc to choose the value
def get_values(var, assignment, tried_values, domains, constraints, graph):
  # Initialize a dictionary to keep track of how many options each value eliminates for each unassigned neighbor
  elimination_counts = {value: 0 for value in domains[var] if value not in tried_values[var]}
  connected_vars = graph[var]

  # Check for all values given value in domain of var
  for value in elimination_counts.keys():
    for other_var in connected_vars:
      if other_var not in assignment:  # consider only unassigned neighbors
        for other_value in domains[other_var]:
          # Check if the current value would eliminate the other_value as an option
          if not pairwise_constraints_check(var, value, other_var, other_value, constraints):
            elimination_counts[value] += 1

  # Sort the values based on LCV, then by value itself
  sorted_values = sorted(elimination_counts, key=lambda x: (elimination_counts[x], x))
  return sorted_values

# Print function with desired output
def print_formatted(assignment, condition, branches):
  result = f"{len(branches)}. "
  items = list(assignment.items())  # Convert to list of tuples (key, value)
  for idx, (var, val) in enumerate(items):
    result += f"{var}={val}"
    if idx < len(items) - 1:
      result += ", "
  result += "  failure" if not condition else "  solution"
  print(result)

# Forward checking
def forward_checking(var, value, assignment, domains, constraints, graph):
  # Make a copy of domains to modify it without affecting the original
  new_domains = domains.copy()
  
  for other_var in graph[var]:
    if other_var not in assignment:  # Only consider unassigned variables
      # For each unassigned connected variable, remove values that are inconsistent
      new_domains[other_var] = [other_value for other_value in domains[other_var]
                                if pairwise_constraints_check(var, value, other_var, other_value, constraints)]
      # If any domain becomes empty, there's no solution with the current assignment, return None
      if not new_domains[other_var]:
        return None
  return new_domains


# Backtrack function to find the solution
def backtrack(assignment, branches, tried_values, domains, constraints, graph, consistency_check):
  # Check if assignment is complete
  if len(assignment) == len(domains):
    return assignment, branches, tried_values

  # Get the next variable to assign
  var = get_variable(assignment, domains, graph)
  # Try all values for this variable
  for value in get_values(var, assignment, tried_values, domains, constraints, graph):
    new_assignment = assignment.copy()
    new_assignment[var] = value
    tried_values[var].append(value)

    # Apply forward checking if 'fc' enabled
    if consistency_check:
      new_domains = forward_checking(var, value, new_assignment, domains, constraints, graph)
      if new_domains is None:  # Forward checking failed
        branches.append(f"{new_assignment} failure")
        print_formatted(new_assignment, False, branches)
        continue  # Skip to the next value since this one leads to a dead end
      # Forward checking succeeded; continue with new domains
      result, branches, tried_values = backtrack(new_assignment, branches, tried_values, new_domains, constraints, graph, consistency_check)
      if result is not None:  # Found a solution or need to backtrack
        if len(new_assignment) == len(domains):
          branches.append(f"{new_assignment} solution")
          print_formatted(new_assignment, True, branches)
        return result, branches, tried_values
    else:  # 'none' case or naive backtracking
      if constraints_check(new_assignment, constraints):
        result, branches, tried_values = backtrack(new_assignment, branches, tried_values, domains, constraints, graph, consistency_check)
        if result is not None:  # Found a solution or need to backtrack
          if len(new_assignment) == len(domains):
            branches.append(f"{new_assignment} solution")
            print_formatted(new_assignment, True, branches)
          return result, branches, tried_values
      else:
        branches.append(f"{new_assignment} failure")
        print_formatted(new_assignment, False, branches)
  # If no assignment was successful, backtrack
  tried_values[var] = []
  return None, branches, tried_values


def main(var_file, con_file, check):
    domains = load_variables(var_file)
    constraints = load_constraints(con_file)
    graph = make_graph(domains, constraints)
    
    assignment = {}
    branches = []
    tried_values = {var: [] for var in domains}

    consistency_check = True if check == "fc" else False if check == "none" else False
    solution, branches_visited, _ = backtrack(assignment, branches, tried_values, domains, constraints, graph, consistency_check)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve CSP with Backtracking and Forward Checking.")
    parser.add_argument("var_file", help="Path to the .var file with variables and their domains.")
    parser.add_argument("con_file", help="Path to the .con file with constraints.")
    parser.add_argument("consistency_checking", help="An option to perform consistency checking")
    args = parser.parse_args()

    main(args.var_file, args.con_file, args.consistency_checking)