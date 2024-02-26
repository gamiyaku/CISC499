# -*- coding: utf-8 -*-
import random
from jinja2 import Environment, FileSystemLoader
import requests

# Generate propositional logic formula
def generate_formula():
    atoms = ['p', 'q', 'r', 's', 't']
    negation = ['!', '']
    operators = ['&', '|', '->', '<->']
    formula = ''
    bracket_stack = 0  # Track the depth of brackets
    bracket_atoms_count = []  # Track the number of atoms in each bracket level
    atom_count = 0  # Count the number of atoms added to the formula
    need_operator = False  # Flag to indicate if the next element should be an operator

    # Ensure at least 10 atoms are added and all brackets are closed
    while atom_count < 10 or bracket_stack > 0:
        if need_operator:
            formula += ' ' + random.choice(operators) + ' '
            need_operator = False
        else:
            if random.choice([True, False]) and bracket_stack < 3 and not need_operator:
                formula += ' (' if formula else '('
                bracket_stack += 1
                bracket_atoms_count.append(0)  # Initialize atom count for this new bracket level

            neg = random.choice(negation)
            if neg:  # Include negation if present
                formula += neg
            formula += random.choice(atoms) + ' '
            atom_count += 1
            if bracket_stack > 0:
                bracket_atoms_count[-1] += 1  # Increment atom count for the current bracket level
            need_operator = True

            if bracket_stack > 0 and bracket_atoms_count[-1] >= 2 and random.choice([True, False]):
                formula += ') '
                bracket_stack -= 1
                bracket_atoms_count.pop()  # Remove atom count for this closed bracket level
                if bracket_stack > 0:
                    bracket_atoms_count[-1] += 1  # Closing a bracket also counts as an atom for the outer bracket

    # Trim trailing operators or spaces if necessary
    formula = formula.rstrip()
    if formula[-1] in {'&', '|', '-', '>'}:
        formula = formula.rsplit(' ', 2)[0]

    return formula, atom_count


# Set Jinja environment
env = Environment(loader=FileSystemLoader('C:/Users/94070/Desktop/499'))#Location of template
template_names = [f'template_p{i}.html' for i in range(1, 7)]


# Generate serious of formula
formulas = [generate_formula() for _ in range(2)]  # Generate any number of formula here
formula_strings = [formula for formula, _ in formulas] 


# Sending questions to ChatGPT and receiving answers
def ask_chatgpt(question, api_key):
    # Prompts 1: Add prompt requirement AI to provide a specific example if the propositional logic formula can be satisfied
    # Prompts 2: Simplify(not test yet)
    # prompts = f"{question} If the formula is satisfiable, provide a set of atoms that make the formula true."
    
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',  # Use the v1/chat/completions port
        headers={'Authorization': f'Bearer {api_key}'},
        json={
            'model': 'gpt-3.5-turbo-0125',  # specified model
            'messages': [{'role': 'user', 'content': question}]#Message send to CGPT
        }
    )
    response_data = response.json()

    if 'choices' in response_data and response_data['choices']:#CGPT answer element returned
        return response_data['choices'][0]['message']['content']
    else:#Prevent error reporting
        return "Error: Unable to get a valid response from the API."


for template_idx, template_name in enumerate(template_names, start=1):
    # Render template to generate questions
    template = env.get_template(template_name)
    output_file_path = f'C:/Users/94070/Desktop/499/answer{template_idx}.txt'

    with open(output_file_path, 'w', encoding='utf-8') as file:#Save location
        api_key = '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'
        question_number = 1 # question number count
        
        questions_text = template.render(formulas=formula_strings) 
        questions = questions_text.split('\n')
            
        for question in questions:  # Iterate over the question list
            if question.strip():  # Make sure the question is not empty
                answer = ask_chatgpt(question, api_key)
                file.write(f'Question {question_number}: {question}\nAnswer: {answer}\n\n')
                print(f'Question {question_number}: {question}\nAnswer: {answer}\n')
                # print(f'Atom Count for Formula {formula_idx + 1}: {atom_count}')
                question_number += 1
