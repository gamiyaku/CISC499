# -*- coding: utf-8 -*-
import random
import re
from jinja2 import Environment, FileSystemLoader
import requests
import os
from PLEvaluate import evaluate
import sys
import time

if len(sys.argv) != 2 or not sys.argv[1].isdigit():
    print('Usage: python3 AskAI.py <num_atoms>')
    sys.exit(0)

num_atoms = int(sys.argv[1])


def randProp(atoms):
    return random.choice(atoms)


def generate_formula(n, atoms_count, available_atoms):
    if atoms_count == 1:
        return randProp(available_atoms)
    else:
        operation = random.choice([
            lambda x: "(!" + x + ")",
            lambda x, y: "(" + x + " & " + y + ")",
            lambda x, y: "(" + x + " | " + y + ")",
            lambda x, y: "(" + x + " -> " + y + ")"
        ])
        if operation.__code__.co_argcount == 2:
            left_atoms_count = random.randint(1, atoms_count - 1)
            right_atoms_count = atoms_count - left_atoms_count
            left_formula = generate_formula(n - 1, left_atoms_count, available_atoms)
            right_formula = generate_formula(n - 1, right_atoms_count, available_atoms)
            return operation(left_formula, right_formula)
        else:
            return operation(generate_formula(n - 1, atoms_count, available_atoms))


DIR = ''
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('template_T7_A.html')

available_atoms = ['p', 'q', 'r', 's', 't']
formulas = [generate_formula(random.randint(1, 10), num_atoms, available_atoms) for _ in range(50)]
questions_text = template.render(formulas=formulas)
questions = questions_text.split('\n')

conversation = [
    {"role": "system", "content": "You are familiar with propositional logic formulas."}
]


def ask_chatgpt(api_key, question, examples):
    # Add the messages to the conversation
    conversation.extend([{'role': 'user', 'content': question}])
    if len(conversation) <= 2:
        conversation.extend([{"role": "assistant", "content": 'Please provide some examples.'},
                             {'role': 'user', 'content': examples}])
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',  # Use the v1/chat/completions port
        headers={'Authorization': f'Bearer {api_key}'},
        json={
            'model': 'gpt-3.5-turbo-0125',  # specified model
            'messages': conversation  # Message send to CGPT
        }
    )
    response_data = response.json()

    if 'choices' in response_data and response_data['choices']:  # CGPT answer element returned
        answer = response_data['choices'][0]['message']['content']
        conversation.append({"role": "assistant", "content": answer})
        return answer
    else:  # Prevent error reporting
        return "Error: Unable to get a valid response from the API."


def extract_truth_assignment(answer):
    # Extract assignments using regular expression
    assignments = re.findall(r'([pqrst])\s*=\s*([TF])', answer)
    assignment_text = ', '.join(f'{var} = {val}' for var, val in assignments)
    return assignment_text


def get_question_and_examples(raw_question):
    # Extract question and examples from the raw question
    try:
        index = raw_question.index('Here are some example')
        question = raw_question[:index]
        examples = raw_question[index:]
    except:
        index = raw_question.index('Question')
        question = raw_question[index:]
        examples = raw_question[:index]
    return question, examples


OUTPUT_DIR = 'outputs/'
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
output_filename = os.path.join(OUTPUT_DIR, 'chatgpt_T7_b.txt')
num_correct = 0
with open(output_filename, 'w', encoding='utf-8') as file:
    api_key = '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'
    question_number = 0  # question number count
    num_error = 0
    for raw_question in questions:  # Iterate over the question list
        if raw_question.strip():  # Make sure the question is not empty
            file.flush()
            time.sleep(1)
            question_number += 1
            formula = formulas[question_number - 1]
            # Ask for AI to answer the question
            question, examples = get_question_and_examples(raw_question)
            answer = ask_chatgpt(api_key, question, examples)
            if answer.startswith('Error: '):
                print(f'Question {question_number}: {question}')
                file.write(f'Question {question_number}: {question}\n')
                print('Failed to request the AI to answer this question.\n')
                file.write('Failed to request the AI to answer this question\n\n')
                num_error += 1
                continue
            extracted_assignment = extract_truth_assignment(answer)
            print(
                f'Question {question_number}: {question}\nAnswer: {answer}\nExtracted Truth Assignment: {extracted_assignment}')
            file.write(
                f'Question {question_number}: {question}\nAnswer: {answer}\nExtracted Truth Assignment: {extracted_assignment}\n')

            # Check whether this answer is correct
            result = evaluate(formula, extracted_assignment)
            if isinstance(result, bool) and result:
                num_correct += 1
                print('Correct answer.\n')
                file.write('Correct answer.\n\n')
            else:
                if isinstance(result, str):
                    print('Found one truth assignment:', result)
                    file.write('Found one truth assignment: %s\n' % result)
                print('Incorrect answer.\n')
                file.write('Incorrect answer.\n')

    print('There are a total of %d questions, of which %d have error responses.' % (question_number, num_error))
    file.write('There are a total of %d questions, of which %d have error responses.\n' % (question_number, num_error))
    rest_number = question_number - num_error
    if rest_number > 0:
        print('%d questions have valid response。 Among those questions, %d have correct answers.' % (rest_number, num_correct))
        file.write('%d questions have valid response。 Among those questions, %d have correct answers.\n' % (rest_number, num_correct))
        accuracy = num_correct / rest_number
        print('The accuracy rate is %.2f%%.' % (100 * accuracy))
        file.write('The accuracy rate is %.2f%%.\n' % (100 * accuracy))
