# -*- coding: utf-8 -*-
import random
from jinja2 import Environment, FileSystemLoader
import requests

# Generate propositional logic formula
def generate_formula():
    atoms = ['p', 'q', 'r', 's', 't']
    negation = ['!', '']
    operators = ['&', '|', '->', '<->']
    formula = random.choice(atoms)
    length = random.randint(10, 30)  # Formula length
    atom_count = 1

    for _ in range(length):
        formula += random.choice(operators) + random.choice(negation) + random.choice(atoms)
        atom_count += 1  # count atoms

    return formula, atom_count

# Set Jinja environment
env = Environment(loader=FileSystemLoader('C:/Users/94070/Desktop/499'))#Location of template
template = env.get_template('template_p2.html')#Choose Jinja template


# Generate serious of formula
formulas = [generate_formula() for _ in range(30)]  # Generate any number of formula here
formula_strings = [formula for formula, _ in formulas] 

# Render template to generate questions
questions_text = template.render(formulas=formula_strings)
questions = questions_text.split('\n')

# Sending questions to ChatGPT and receiving answers
def ask_chatgpt(question, api_key):
    # Prompts 1: Add prompt requirement AI to provide a specific example if the propositional logic formula can be satisfied
    # Prompts 2: Simplify(not test yet)
    prompts = f"{question} If the formula is satisfiable, provide a set of atoms that make the formula true."
    
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',  # Use the v1/chat/completions port
        headers={'Authorization': f'Bearer {api_key}'},
        json={
            'model': 'gpt-3.5-turbo-0125',  # specified model
            'messages': [{'role': 'user', 'content': question + prompts}]#Message send to CGPT
        }
    )
    response_data = response.json()

    if 'choices' in response_data and response_data['choices']:#CGPT answer element returned
        return response_data['choices'][0]['message']['content']
    else:#Prevent error reporting
        return "Error: Unable to get a valid response from the API."



with open('C:/Users/94070/Desktop/499/chatgpt_answers2.txt', 'w', encoding='utf-8') as file:#Save location
    api_key = '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'
    question_number = 1 # question number count
    for question in questions:  # Iterate over the question list
        if question.strip():  # Make sure the question is not empty
            answer = ask_chatgpt(question, api_key)
            atom_count = formulas[question_number-1][1] #Count atom number
            print(f'Question {question_number}: {question}\nAnswer: {answer}\n')
            print(f'Atom Count for Formula {question_number}: {atom_count}')
            file.write(f'Question {question_number}: {question}\nAnswer: {answer}\nAtom Count: {atom_count}\n\n')
            question_number += 1
