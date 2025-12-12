import json
import logging
from datetime import datetime
from typing import Any, Dict

from baicai_base.agents.graphs.nodes import BaseNode
from baicai_base.utils.data import get_saved_question_path, get_tmp_folder, safe_extract_json
from langchain_core.runnables import RunnableConfig

from baicai_tutor.agents.graphs.state import TutorState
from baicai_tutor.agents.roles import questioner


class QuestionerNode(BaseNode):
    """
    Node for question generation using Item Response Theory (IRT) models.
    """

    def __init__(self, llm: Any, logger: logging.Logger = None) -> None:
        """
        Initialize the QuestionerNode with a language model and an optional logger.

        Args:
            llm: The language model to be used for question generation.
            logger: Optional logger for logging information.
        """
        super().__init__(llm=llm, logger=logger)
        self.runnable = questioner(self.llm)

    def __call__(self, state: TutorState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the node logic.

        Args:
            state (TutorState): The current state of the tutor process.
            config (RunnableConfig): Configuration details for the node.

        Returns:
            dict: Updated state after execution.
        """
        # Extract and initialize state components with defaults for potential None values
        question_sheet_id = config["configurable"].get("question_sheet_id", "")

        if question_sheet_id:
            question_path = get_saved_question_path(question_sheet_id)
            if question_path.exists():
                with open(question_path, "r", encoding="utf-8") as f:
                    questions = json.load(f)
                return {"questions": questions}

        messages = state.get("messages", [])
        subject = config["configurable"]["subject"]
        level = config["configurable"]["level"]
        grade = config["configurable"]["grade"]
        background = config["configurable"]["background"]
        profile = config["configurable"]["profile"]
        charpt_name = config["configurable"]["charpt_name"]
        keywords = config["configurable"]["keywords"]
        summary = config["configurable"]["summary"]
        num_questions = config["configurable"]["num_questions"]

        self.logger.info("## Question Generator")

        original_solution, questions, reflections, failed = safe_extract_json(
            self.runnable,
            {
                "messages": messages,
                "subject": subject,
                "level": level,
                "grade": grade,
                "background": background,
                "profile": profile,
                "charpt_name": charpt_name,
                "keywords": keywords,
                "summary": summary,
                "num_questions": num_questions,
            },
            start_tag="<start_json>",
            end_tag="</end_json>",
        )

        level_mapping = {
            "Level 1: REMEMBER": "level_1",
            "Level 2: UNDERSTAND": "level_2",
            "Level 3: APPLY": "level_3",
            "Level 4: ANALYZE": "level_4",
            "Level 5: EVALUATE": "level_5",
            "Level 6: CREATE": "level_6",
        }

        questions["id"] = (
            f"{subject}-{charpt_name}-{grade}-{level_mapping[level]}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        questions["meta"] = {
            "subject": subject,
            "level": level,
            "grade": grade,
            "background": background,
            "charpt_name": charpt_name,
        }
        self.logger.info(f"### Questions generated: \n{questions}")

        temp_folder = get_tmp_folder("question")
        temp_folder.mkdir(parents=True, exist_ok=True)
        with open(temp_folder / f"{questions['id']}.json", "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

        return {
            "questions": questions,
        }
