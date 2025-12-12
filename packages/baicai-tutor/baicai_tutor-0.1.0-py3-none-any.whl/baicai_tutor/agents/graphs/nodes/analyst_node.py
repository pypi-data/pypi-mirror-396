import json
import logging
from typing import Any, Dict

from baicai_base.agents.graphs.nodes import BaseNode
from baicai_base.utils.data import get_saved_user_info_path, get_tmp_folder, safe_extract_json
from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt

from baicai_tutor.agents.graphs.state import TutorState
from baicai_tutor.agents.roles.surveyor import analyst


class AnalystNode(BaseNode):
    """
    Node for analyst to analyze the students' background information.
    """

    def __init__(self, llm: Any, logger: logging.Logger = None) -> None:
        """
        Initialize the AnalystNode with a language model and an optional logger.

        Args:
            llm: The language model to be used for analyst.
            logger: Optional logger for logging information.
        """
        super().__init__(llm=llm, logger=logger)
        self.runnable = analyst(self.llm)

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
        generate_new_profile = config["configurable"].get("generate_new_profile", False)

        if not generate_new_profile:  # there should be a saved profile
            try:
                _, profile_path = get_saved_user_info_path()
                with open(profile_path, "r", encoding="utf-8") as f:
                    profile = json.load(f)
                    return {"profile": profile}
            except FileNotFoundError as err:
                error_message = "没有找到用户档案文件。"
                self.logger.error(error_message)
                raise ValueError(error_message) from err
            except UnicodeDecodeError as err:
                error_message = "文件编码错误，请确保使用 UTF-8 编码。"
                self.logger.error(error_message)
                raise ValueError(error_message) from err

        # 获取用户问卷反馈数据
        surveys = interrupt({"surveys": state["surveys"]})

        if not surveys:
            error_message = "没有找到问卷信息"
            self.logger.error(error_message)
            raise ValueError(error_message)

        self.logger.info("## Analyst")

        original_solution, profile, reflections, failed = safe_extract_json(
            self.runnable,
            {"messages": [("user", "用户问卷反馈数据：\n" + str(surveys))]},
        )

        temp_folder = get_tmp_folder("user_info")
        temp_folder.mkdir(parents=True, exist_ok=True)
        with open(temp_folder / "profile.json", "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)

        self.logger.info(f"### Profile: \n{profile}")

        return {
            "profile": profile,
        }
