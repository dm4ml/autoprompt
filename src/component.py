from motion import Component

import asyncio
import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_not_exception_type,
)  # for exponential backoff

import os
import re

from rich import print

from typing import List, Dict, Tuple

from src.utils import Prompt
from src.evaluate import (
    evaluate_examples,
    eval_examples_many_templates,
    find_best_prompt,
)

"""
Generic prompt engineering utility.

Iteratively generates prompts for a given question, and
returns the prompt that gives the best performance.

User provides starting prompt & examples.

We maintain 3 AIs:
- Prompt Engineer: Generates prompts
- Answer Model: Generates answers to prompts
- Evaluator Model: Compares the answers from different prompt templates
"""

PromptEngineer = Component("PromptEngineer")


@PromptEngineer.init_state
def setUp():
    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompteng_system_message = {
        "role": "system",
        "content": "You are a prompt engineer, and your goal is to generate the best prompt template for a large language model to perform some task.",
    }
    return {
        "prompteng_system_message": prompteng_system_message,
        "prompteng_messages": [],
        "templates_and_results": [],
        "examples": [],
        "cost": 0.0,
        "best_template": None,
        "best_results": None,
        "initial_template": None,
    }


@PromptEngineer.fit("add_example", batch_size=1)
def add_example(state, values, infer_results):
    return {"examples": state["examples"] + values}


@PromptEngineer.fit("remove_example", batch_size=1)
def remove_example(state, values, infer_results):
    examples = state["examples"]
    examples.remove(values[0])
    return {"examples": examples}


@PromptEngineer.fit("init_template", batch_size=1)
def set_template(state, values, infer_results):
    results, cost = asyncio.run(
        evaluate_examples(state["examples"], values[0])
    )
    return {
        "templates_and_results": [(values[0], results)],
        "initial_template": values[0],
        "best_template": values[0],
        "best_results": results,
        "task": values[0],
        "cost": state["cost"] + cost,
    }


@PromptEngineer.infer("refine")
@retry(
    retry=retry_if_not_exception_type(KeyError),
    wait=wait_random_exponential(min=1, max=60),
    stop=stop_after_attempt(6),
)
def execute_prompt(state, value):
    user_feedback = value

    if "best_template" not in state:
        raise KeyError("Must set template first")

    template = state["best_template"]
    results = state["best_results"]
    cost = 0.0
    # results, cost = asyncio.run(evaluate_examples(state, template))

    prompt = Prompt(template=template, task=state["task"])

    # Get feedback on the results
    prompt_for_feedback = prompt.assemble_for_feedback(str(results))
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[state["prompteng_system_message"]]
        + state["prompteng_messages"]
        + [{"role": "user", "content": prompt_for_feedback}],
        stop=["\n"],
    )
    cost += response["usage"]["total_tokens"] * 0.002 / 1000.0
    feedback = response["choices"][0].message["content"]

    # Get a new prompt
    user_prompt = prompt.assemble_for_new_prompt(feedback, user_feedback)
    messages = [{"role": "user", "content": user_prompt}]
    while True:
        current_messages = state["prompteng_messages"] + messages
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[state["prompteng_system_message"]]
                + current_messages,
                stop=["\n"],
            )
        except Exception as e:
            print(response)
            # print([state["prompteng_system_message"]] + current_messages)
            raise e
        cost += response["usage"]["total_tokens"] * 0.002 / 1000.0
        better_prompt = response["choices"][0].message["content"]

        # Extract the quote from the better prompt
        if ":" in better_prompt:
            better_prompt = "".join(better_prompt.split(":")[1:])
        better_prompt = better_prompt.strip()
        if (
            "{example}" in better_prompt
            and len(set(re.findall(r"\{(.*?)\}", better_prompt))) == 1
        ):
            break
        else:
            # print("The prompt is not valid; retrying.")
            # print(response)
            user_message = {
                "role": "user",
                "content": "Please include the phrase {example} in the prompt template. Don't include any other template variables.",
            }
            messages += [
                # {"role": "assistant", "content": better_prompt},
                user_message,
            ]

    # Return feedback, better prompt, and cost so far
    return messages[0], better_prompt, cost


@PromptEngineer.fit("refine", batch_size=1)
def update_cost(state, values, infer_results):
    return {"cost": state["cost"] + infer_results[0][2]}


@PromptEngineer.fit("refine", batch_size=5)
def update_template(state, values, infer_results):
    # Update state vars, including best prompt
    cost = 0.0

    best_template = state["best_template"]
    task = state["task"]
    best_results = state["best_results"]

    new_templates = [result[1] for result in infer_results]

    # Get all the results for all the new templates and examples
    new_eval_results, eval_cost = asyncio.run(
        eval_examples_many_templates(state["examples"], new_templates)
    )
    cost += eval_cost

    # Run pairwise comparisons to find the best prompt
    templates_and_results: List[Tuple[str, Dict[str, str]]] = [
        (new_template, new_eval_result)
        for new_template, new_eval_result in zip(
            new_templates, new_eval_results
        )
    ]
    templates_and_results.append((best_template, best_results))
    best_template_result, compare_cost = asyncio.run(
        find_best_prompt(task, templates_and_results)
    )
    cost += compare_cost
    best_template = best_template_result[0]
    best_results = best_template_result[1]

    # Find the message for the best template
    updated_messages = []
    if best_template != state["best_template"]:
        updated_messages += [
            msg
            for msg, template, _ in infer_results
            if template == best_template
        ]
        updated_messages += [{"role": "assistant", "content": best_template}]

    return {
        "prompteng_messages": state["prompteng_messages"] + updated_messages,
        "cost": state["cost"] + cost,
        "best_template": best_template,
        "best_results": best_results,
        "templates_and_results": state["templates_and_results"]
        + templates_and_results[:-1],
    }
