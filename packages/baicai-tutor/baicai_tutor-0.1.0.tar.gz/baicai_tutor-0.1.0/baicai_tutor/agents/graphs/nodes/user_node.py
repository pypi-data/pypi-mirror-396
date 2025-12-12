import json
import logging
from typing import Any, Dict

import numpy as np
from baicai_base.agents.graphs.nodes import BaseNode
from baicai_base.utils.data import get_tmp_folder
from girth import ability_map
from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt

from baicai_tutor.agents.graphs.state import TutorState
from baicai_tutor.agents.roles.student import student
from baicai_tutor.utils import calculate_probability_correct


class UserNode(BaseNode):
    """
    Node for user answering questions and irt analysis.
    """

    def __init__(self, llm: Any, logger: logging.Logger = None) -> None:
        """
        Initialize the UserNode with a language model and an optional logger.

        Args:
            llm: The language model to be used for user answering questions.
            logger: Optional logger for logging information.
        """
        super().__init__(llm=llm, logger=logger)
        self.runnable = student(self.llm)

    def __call__(self, state: TutorState, config: RunnableConfig) -> Dict[str, Any]:
        """
        Execute the node logic.

        Args:
            state (StudentsState): The current state of the students process.
            config (RunnableConfig): Configuration details for the node.

        Returns:
            dict: Updated state after execution.
        """
        # Extract and initialize state components with defaults for potential None values
        questions = state.get("questions", {})
        students = state.get("students", {})
        p_range = config["configurable"].get("p_range", [])

        self.logger.info("## User Node")

        if "self_ability" in students:
            self_ability = students["self_ability"]
        else:
            self_ability = -100

        # get answers from the user
        # Calculate probabilities for all questions
        # When user ability is unknown, use a more conservative approach
        if self_ability == -100:
            # Use a lower ability estimate to get more reasonable probabilities
            # This ensures we don't filter out too many questions initially
            ability_for_calculation = -1.0  # More conservative estimate
        else:
            ability_for_calculation = self_ability

        probabilities_correct = calculate_probability_correct(
            ability_for_calculation,
            students["discrimination"],
            students["difficulty"],
        )

        # Debug logging
        self.logger.info(f"User ability: {self_ability}")
        self.logger.info(f"Ability used for calculation: {ability_for_calculation}")
        self.logger.info(f"P_range: {p_range}")
        self.logger.info(f"Questions structure: {questions}")
        self.logger.info(f"Students structure: {students}")
        self.logger.info(f"Calculated probabilities: {probabilities_correct}")
        self.logger.info(f"Total questions: {len(questions.get('questions', []))}")

        # Check if questions structure is correct
        if "questions" not in questions:
            self.logger.error("Questions structure missing 'questions' key!")
            return {"user": None}

        if not questions["questions"]:
            self.logger.error("No questions found in questions structure!")
            return {"user": None}

        # Filter questions based on probability range
        # Add safety check for p_range
        if len(p_range) >= 2:
            filtered_questions = [
                q for i, q in enumerate(questions["questions"])
                if p_range[0] <= probabilities_correct[i] <= p_range[1]
            ]
            self.logger.info(f"Filtered questions count: {len(filtered_questions)}")
            for i, prob in enumerate(probabilities_correct):
                in_range = p_range[0] <= prob <= p_range[1]
                self.logger.info(f"Question {i+1}: prob={prob:.6f}, in_range={in_range}")
        else:
            # If p_range is not properly set, use all questions
            self.logger.warning("p_range not properly configured, using all questions")
            filtered_questions = questions["questions"]

        user_answers = interrupt({"questions": filtered_questions})

        # 没有self_ability，或者需要重新测量，开始测量
        if self_ability == -100 or state.get("renew_self_ability", False):
            if not state.get("renew_self_ability", False):
                self.logger.warning("Warning: Self ability does not exist. We will measure it from the user's answers.")

            # Get indices of filtered questions
            if len(p_range) >= 2:
                filtered_indices = [
                    i for i, q in enumerate(questions["questions"])
                    if p_range[0] <= probabilities_correct[i] <= p_range[1]
                ]
            else:
                # If p_range is not properly set, use all question indices
                filtered_indices = list(range(len(questions["questions"])))

            # Create response matrix only for filtered questions
            response_matrix = np.array(
                [1 if answer["user_answer"] == answer["answer"] else 0 for answer in user_answers]
            ).reshape(-1, 1)

            # Filter discrimination and difficulty parameters for the selected questions
            filtered_discrimination = np.array([students["discrimination"][i] for i in filtered_indices])
            filtered_difficulty = np.array([students["difficulty"][i] for i in filtered_indices])

            self_ability = ability_map(response_matrix, filtered_discrimination, filtered_difficulty)

        # Create user object with filtered answers
        user = {"id": "user", "theta": float(self_ability), "answers": user_answers, "question_id": questions["id"]}

        temp_folder = get_tmp_folder("user_info")
        temp_folder.mkdir(parents=True, exist_ok=True)
        with open(temp_folder / "user.json", "w", encoding="utf-8") as f:
            json.dump(user, f, ensure_ascii=False, indent=2)
        self.logger.info("Answer sheet of user saved")

        return {
            "user": user,
        }
