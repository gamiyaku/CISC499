import re
import copy
from mathesis.grammars import BasicGrammar
from mathesis.semantics.truth_table import ClassicalTruthTable


def parse_truth_assignments(text):
    """
    Parses truth assignments from a given text.

    Args:
    - text (str): A string containing truth assignments in the form "A=True, B=False".

    Returns:
    - dict: A dictionary mapping variables to their truth values (True or False).
    """
    # Match all assignments in the form "Variable=True/False"
    assignments = re.findall(r'\b([A-Za-z]+) = (T|F)\b', text)

    # Convert assignments to a dictionary, converting 'True'/'False' strings to boolean values
    truth_values = {var: 1 if val == 'T' else 0 for var, val in assignments}

    return truth_values


def format_formula(raw_formula):
    # Format the formula using special characters
    return raw_formula.replace('!', '¬').replace('&', '∧').replace('|', '∨').replace('->', '→')


def evaluate_pl(table, truth_values):
    # Check whether the truth values are satisfiable
    rows = table.to_string().split('\n')
    headers = [item.strip() for item in rows[0].split()]
    # Map variables to indices
    variable_indices = {item: idx for idx, item in enumerate(headers)}

    for row in rows[1:]:
        values = [int(item.strip()) for item in row.split()]
        # Find the matching row
        match_row = True
        for variable, value in truth_values.items():
            if variable not in variable_indices:
                continue
            idx = variable_indices[variable]
            if values[idx] != value:
                match_row = False
                break
        if match_row:
            # Check if the formula is evaluated to True
            return values[-1] == 1

    return False


# get all possible truth assignments
def get_all_truth_assignments(variables):
    def inter_func(curr, truth_assignments, all_values):
        if curr == len(variables):
            all_values.append(copy.deepcopy(truth_assignments))
            return
        variable = variables[curr]
        for value in [True, False]:
            truth_assignments[variable] = value
            inter_func(curr + 1, truth_assignments, all_values)
        del truth_assignments[variable]

    all_values = []
    inter_func(0, {}, all_values)
    return all_values


# Determine whether this formula has no satisfiable truth assignments
def is_no_satisfiable_formula(raw_formula):
    # Find all variables
    variables = list(set(re.findall(r'[A-Za-z]+', raw_formula)))

    # Try different truth assignments
    for truth_assignments in get_all_truth_assignments(variables):
        assignment_text = ', '.join(f'{var} = {"T" if val else "F"}' for var, val in truth_assignments.items())
        if evaluate(raw_formula, assignment_text):
            return assignment_text

    return None


# Evaluate whether truth assignment is correct
def evaluate(raw_formula, truth_assignment):
    if len(truth_assignment) == 0:
        assignment_text = is_no_satisfiable_formula(raw_formula)
        if assignment_text is None:
            return True
        else:
            return assignment_text

    # Create the formula
    grammar = BasicGrammar()
    formula = format_formula(raw_formula)
    fml = grammar.parse(formula)
    table = ClassicalTruthTable(fml)
    # Evaluate the formula using the given truth assignment
    truth_values = parse_truth_assignments(truth_assignment)
    return evaluate_pl(table, truth_values)


if __name__ == '__main__':
    formula = '(s & !s)'
    value = ''
    print(evaluate(formula, value))
