import asyncio
import openai
import random
import re

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff

from typing import List, Dict, Tuple


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
async def run_prompts(prompts: List[str]):
    completion = await openai.Completion.acreate(
        model="text-babbage-001", prompt=prompts, max_tokens=50, stop=["\n"]
    )
    cost = completion["usage"]["total_tokens"] * 0.0005 / 1000.0
    results = {choice.index: choice.text for choice in completion.choices}
    results = [results[i] for i in range(len(results))]

    return results, cost


async def evaluate_examples(examples, template):
    prompts = [template.format(example=example) for example in examples]
    completions, cost = await run_prompts(prompts)
    results = {
        prompt: completion for prompt, completion in zip(prompts, completions)
    }

    return results, cost


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
async def comparison(
    task: str,
    prompt_result_left: Tuple[str, Dict[str, str]],
    prompt_result_right: Tuple[str, Dict[str, str]],
) -> str:
    """Evaluate which output is better."""
    swap_indicator = random.random() < 0.5
    random_prompt_left = (
        prompt_result_left[1] if swap_indicator else prompt_result_right[1]
    )
    random_prompt_right = (
        prompt_result_right[1] if swap_indicator else prompt_result_left[1]
    )

    prompt = f"Result 1: {random_prompt_left}\nResult 2: {random_prompt_right}\n\nPlease type Result 1 or Result 2."
    messages = [
        {
            "role": "system",
            "content": f"You are a human evaluator. You will be given two sets of results, and you should decide which one is more correct and useful for the task '{task}'. Type Result 1 or Result 2 to indicate which one is better.",
        },
        {"role": "user", "content": prompt},
    ]

    completion = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo", messages=messages, temperature=0
    )
    cost = completion["usage"]["total_tokens"] * 0.002 / 1000.0

    answer = completion.choices[0].message["content"].strip()
    choice = re.findall(r"Result (\d+)", answer)
    if choice:
        if "1" in choice[0]:
            if swap_indicator:
                return prompt_result_left, cost
            else:
                return prompt_result_right, cost
        elif "2" in choice[0]:
            if swap_indicator:
                return prompt_result_right, cost
            else:
                return prompt_result_left, cost

    # If the answer is invalid, return a random one
    return prompt_result_left, cost


def compute_pairs(templates_and_results: List[Tuple[str, Dict[str, str]]]):
    pairs = []
    for i in range(0, len(templates_and_results) - 1, 2):
        pair = [
            templates_and_results[i],
            templates_and_results[i + 1],
        ]
        pairs.append(pair)
    # Handle odd case
    if len(templates_and_results) % 2 == 1:
        pairs.append([templates_and_results[-1], templates_and_results[0]])

    return pairs


async def find_best_prompt(
    task: str, templates_and_results: List[Tuple[str, Dict[str, str]]]
):
    cost = 0.0
    while len(templates_and_results) > 1:
        pending_comparisons = compute_pairs(templates_and_results)
        tasks = [comparison(task, *pair) for pair in pending_comparisons]
        compare_results = await asyncio.gather(*tasks)
        cost += sum([result[1] for result in compare_results])
        templates_and_results = [result[0] for result in compare_results]

    return templates_and_results[0], cost


async def eval_examples_many_templates(examples, templates):
    tasks = [evaluate_examples(examples, template) for template in templates]
    results = await asyncio.gather(*tasks)
    return [result[0] for result in results], sum(
        [result[1] for result in results]
    )
