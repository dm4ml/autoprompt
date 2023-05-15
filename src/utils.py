from pydantic import BaseModel, validator


class Prompt(BaseModel):
    template: str
    task: str

    @validator("template", allow_reuse=True)
    def template_must_have_example(cls, v):
        if "{example}" not in v:
            raise ValueError("Template must have {example} in it.")
        return v

    def assemble_for_feedback(self, llm_result: str) -> str:
        prompt_str = "Current prompt template: {template}".format(
            template=self.template
        )
        result_str = "Result of current prompt template on examples: {llm_result}".format(
            llm_result=llm_result
        )
        joined = "\n".join([prompt_str, result_str])
        return (
            joined
            + f"\n\nProvide some high-level feedback on how well the results satisfy the task '{self.task}.' How should one change the prompt to get higher-quality results?"
        )

    def assemble_for_new_prompt(
        self, feedback: str, user_feedback: str = ""
    ) -> str:
        prompt_str = "Current prompt template: {template}".format(
            template=self.template
        )
        user_feedback_str = (
            "User feedback on the prompt template: {user_feedback}".format(
                user_feedback=user_feedback
            )
            if user_feedback
            else ""
        )
        feedback_str = (
            "Other feedback on the results: {feedback}".format(
                feedback=feedback
            )
            if feedback
            else ""
        )
        joined = (
            "\n".join([prompt_str, user_feedback_str, feedback_str])
            if user_feedback_str
            else "\n".join([prompt_str, feedback_str])
        )
        return (
            joined
            + "\n\nPlease provide a better prompt template, and return only the prompt template. Make sure you include {example} in your prompt template."
        )
