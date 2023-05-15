"""Creates a FastAPI app instance around the Motion component.
"""

from fastapi import FastAPI, HTTPException, Response, Body
from fastapi.staticfiles import StaticFiles
from src import PromptEngineer

from typing import List, Dict


app = FastAPI()
app.state.component = PromptEngineer()


@app.post("/add_example")
async def add_examples(text: str = Body(..., embed=True)) -> Response:
    example = text
    if example in app.state.component.read_state("examples"):
        return Response(
            status_code=500,
            media_type="text/plain",
            content=f"Example {example} already exists. No examples added.",
        )
    app.state.component.run(add_example=example, wait_for_fit=True)

    # Return 200 OK
    return Response(
        status_code=200,
        content=f"Added example: {example}",
        media_type="text/plain",
    )


@app.post("/remove_example")
async def remove_examples(text: str = Body(..., embed=True)) -> Response:
    example = text
    if example not in app.state.component.read_state("examples"):
        return Response(
            status_code=500,
            media_type="text/plain",
            content=f"Example {example} not found. No examples removed.",
        )

    app.state.component.run(remove_example=example, wait_for_fit=False)

    return Response(
        status_code=200,
        media_type="text/plain",
        content=f"Removed example: {example}",
    )


@app.post("/init_template")
async def init_template(text: str = Body(..., embed=True)) -> Response:
    template = text
    if "{example}" not in template:
        err_str = "Template must contain {example}"
        return Response(
            status_code=500,
            content=err_str,
            media_type="text/plain",
        )

    if len(app.state.component.read_state("examples")) == 0:
        return Response(
            status_code=500,
            media_type="text/plain",
            content=f"Add some examples before setting a template.",
        )

    app.state.component.run(init_template=template, wait_for_fit=True)
    return Response(
        status_code=200,
        media_type="text/plain",
        content=f"Set a new template: {template}",
    )


@app.post("/refine")
async def refine(text: str = Body(..., embed=True)) -> Response:
    user_feedback = text
    try:
        res, fit_event = app.state.component.run(
            refine=user_feedback, return_fit_event=True
        )
        _, prompt, _ = res
        # fit_event.events["update_cost"].wait()
        return Response(
            status_code=200,
            media_type="text/plain",
            content=f"Refined prompt: {prompt}",
        )
    except Exception as e:
        return Response(
            status_code=500,
            media_type="text/plain",
            content=f"Error: {e}",
        )


@app.get("/cost")
async def cost() -> float:
    return app.state.component.read_state("cost")


@app.get("/best_template")
async def best_template() -> str:
    return app.state.component.read_state("best_template")


@app.get("/best_results")
async def best_results() -> Dict[str, str]:
    return app.state.component.read_state("best_results")


# @app.get("/")
# def read_root():
#     return {"Hello": "World"}


@app.on_event("shutdown")
async def shutdown():
    app.state.component.shutdown()


app.mount("/", StaticFiles(directory="autoprompt-ui/dist", html=True))
