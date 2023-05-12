from src import PromptEngineer

from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.table import Table


# Create a console object
console = Console()
actions = [
    "add_example",
    "remove_example",
    "init_template",
    "refine_template",
    "show_cost",
    "show_best_template",
    "show_best_results",
    "exit",
]
examples = []

if __name__ == "__main__":
    c = PromptEngineer()

    while True:
        user_action = Prompt.ask(
            "[bold magenta]What action do you want to take?[/bold magenta]",
            choices=actions,
        )

        if user_action.lower() == "exit":
            exit()

        if user_action.lower() == "add_example":
            example = Prompt.ask(
                "[bold magenta]Enter an example to add, or enter to skip[/bold magenta]"
            )
            if example:
                examples.append(example)
                c.run(add_example=example, wait_for_fit=True)

        if user_action.lower() == "remove_example":
            example = Prompt.ask(
                "[bold magenta]Enter an example to remove, or enter to skip[/bold magenta]",
                choices=examples,
            )
            if example and example in examples:
                examples.remove(example)
                c.run(remove_example=example, wait_for_fit=True)

        if user_action.lower() == "init_template":
            init_template = Prompt.ask(
                "[bold magenta]Enter your starting prompt. Include the placeholder text {example} where you want the example to appear[/bold magenta]"
            )
            c.run(init_template=init_template, wait_for_fit=True)

        if user_action.lower() == "refine_template":
            console.rule("[bold cyan]Refining template[/bold cyan]")
            num_steps = IntPrompt.ask(
                "[bold magenta]How many new prompts do you want to generate?[/bold magenta]"
            )
            for _ in range(int(num_steps)):
                res, fit_event = c.run(refine=True, return_fit_event=True)
                _, prompt, _ = res
                fit_event.events["update_cost"].wait()
                console.print(
                    f"[bold cyan]New prompt generated:[/bold cyan] {prompt}"
                )

        if user_action.lower() == "show_cost":
            console.rule("[bold cyan]Cost[/bold cyan]")
            console.print(f"${c.read_state('cost')}")

        if user_action.lower() == "show_best_template":
            console.rule("[bold cyan]Best template[/bold cyan]")
            console.print(f"{c.read_state('best_template')}")

        if user_action.lower() == "show_best_results":
            console.rule("[bold cyan]Results for best prompt[/bold cyan]")
            table = Table()
            table.add_column("Example", style="cyan")
            table.add_column("Result", justify="right", style="green")
            for key, value in c.read_state("best_results").items():
                table.add_row(key, value)
            console.print(table)
