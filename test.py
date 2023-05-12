from src import PromptEngineer
from rich import print

if __name__ == "__main__":
    c = PromptEngineer()

    # Add examples
    c.run(add_example="the beach")
    c.run(add_example="a concert")
    c.run(add_example="the gym")
    c.run(add_example="a date")
    c.run(add_example="a job interview")
    c.run(add_example="a wedding", wait_for_fit=True)

    # Set inital prompt
    init_template = "list outfit ideas for what to wear to {example}"
    c.run(init_template=init_template, wait_for_fit=True)

    # Iteratively make a good prompt!
    for _ in range(15):
        res, fit_event = c.run(refine=True, return_fit_event=True)
        _, prompt, _ = res
        fit_event.events["update_cost"].wait()

        print(prompt)
        print(f"Approximate cost so far: ${c.read_state('cost')}")

    # Show the best results
    fit_event.events["update_template"].wait()
    print(f"Best template: {c.read_state('best_template')}")
    c.shutdown()
