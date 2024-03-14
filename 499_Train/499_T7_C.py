# -*- coding: utf-8 -*-
import random
from jinja2 import Environment, FileSystemLoader
import requests
import re

# Generate a random propositional atom
def randProp():
    atoms = ['p', 'q', 'r', 's', 't']
    return random.choice(atoms)

# Recursively generate a propositional logic formula
def generate_formula(n):
    if n <= 1:
        return randProp()
    else:
        operation = random.choice([
            lambda x: "(!" + x + ")",
            lambda x: "(" + x + " & " + generate_formula(n-1) + ")",
            lambda x: "(" + x + " | " + generate_formula(n-1) + ")",
            lambda x: "(" + x + " -> " + generate_formula(n-1) + ")",
            lambda x: "(" + x + " <-> " + generate_formula(n-1) + ")"
        ])
        return operation(generate_formula(n-1))

# Set Jinja environment
env = Environment(loader=FileSystemLoader('C:/Users/94070/Desktop/499/499_Train'))#Location of template
template = env.get_template('template_T7_C.html')#Choose Jinja template


# Generate serious of formula
formulas = [generate_formula(random.randint(1, 10)) for _ in range(5)]  # Generate any number of formula here

# Render template to generate questions
questions_text = template.render(formulas=formulas)
questions = questions_text.split('\n')

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

def eval_logic_expr(expr, assignments):
    for var, val in assignments.items():
        expr = expr.replace(var, val)
    expr = expr.replace("T", "True").replace("F", "False")

    expr = expr.replace("!", "not ").replace("&", " and ").replace("|", " or ")
    expr = expr.replace("->", ") <= (").replace("<->", ") == (")
    expr = "(" + expr + ")"

    try:
        result = eval(expr)
    except Exception as e:
        print(f"Error evaluating formula: {e}")
        return False
    return result


with open('C:/Users/94070/Desktop/499/499_Train/chatgpt_T7_check.txt', 'w', encoding='utf-8') as file:#Save location
    api_key = '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'
    question_number = 1
    for question in questions:
        if question.strip():
            answer = ask_chatgpt(question, api_key)
            verification_result = verify_answer(question, answer)
            print(f'Question {question_number}: {question}\nAnswer: {answer}\nVerification: {verification_result}\n')
            file.write(f'Question {question_number}: {question}\nAnswer: {answer}\nVerification: {verification_result}\n\n')
            question_number += 1