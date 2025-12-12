import json
import logging
from typing import Any, Dict

from baicai_base.agents.graphs.nodes import BaseNode
from baicai_base.utils.data import get_saved_user_info_path, get_tmp_folder, safe_extract_json
from langchain_core.runnables import RunnableConfig

from baicai_tutor.agents.graphs.state import TutorState
from baicai_tutor.agents.roles.surveyor import surveyor


class SurveyorNode(BaseNode):
    """
    Node for surveyor to survey the students' background information.
    """

    def __init__(self, llm: Any, logger: logging.Logger = None) -> None:
        """
        Initialize the SurveyorNode with a language model and an optional logger.

        Args:
            llm: The language model to be used for surveyor.
            logger: Optional logger for logging information.
        """
        super().__init__(llm=llm, logger=logger)
        self.runnable = surveyor(self.llm)

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
        generate_new_survey = config["configurable"].get("generate_new_survey", False)
        self.logger.info("## Surveyor")

        if not generate_new_survey:  # there should be a saved survey
            try:
                survey_path, _ = get_saved_user_info_path()
                with open(survey_path, "r", encoding="utf-8") as f:
                    surveys = json.load(f)
                    return {"surveys": surveys}
            except FileNotFoundError as err:
                error_message = "没有找到问卷文件。"
                self.logger.error(error_message)
                raise ValueError(error_message) from err
            except UnicodeDecodeError as err:
                error_message = "文件编码错误，请确保使用 UTF-8 编码。"
                self.logger.error(error_message)
                raise ValueError(error_message) from err

        messages = state.get("messages", [])

        grade = config["configurable"]["grade"]
        background = config["configurable"]["background"]
        subject = config["configurable"]["subject"]
        already_learn_subject = config["configurable"]["already_learn_subject"]

        solution, extracted_json, reflections, failed = safe_extract_json(
            self.runnable,
            {
                "messages": messages,
                "grade": grade,
                "background": background,
                "subject": subject,
                "already_learn_subject": already_learn_subject,
            },
        )
        surveys = extracted_json["questions"]

        temp_folder = get_tmp_folder("user_info")
        temp_folder.mkdir(parents=True, exist_ok=True)
        with open(temp_folder / "survey.json", "w", encoding="utf-8") as f:
            json.dump(surveys, f, ensure_ascii=False, indent=2)

        self.logger.info(f"### Survey Questions: \n{surveys}")

        return {
            "surveys": surveys,
        }
