import json
import logging
from typing import Any, Dict

import numpy as np
from baicai_base.agents.graphs.nodes import BaseNode
from baicai_base.utils.data import get_saved_students_path, get_tmp_folder, safe_extract_json
from langchain_core.runnables import RunnableConfig

from baicai_tutor.agents.graphs.state import TutorState
from baicai_tutor.agents.roles.student import student
from baicai_tutor.utils import IRT, convert_numpy_to_native


class StudentsNode(BaseNode):
    """
    Node for LLM-generated students with different ability levels and their answers.
    """

    def __init__(self, llm: Any, logger: logging.Logger = None) -> None:
        """
        Initialize the StudentsNode with a language model and an optional logger.

        Args:
            llm: The language model to be used for students generation.
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
        num_students = config["configurable"].get("num_students", 10)
        generate_students = config["configurable"].get("generate_students", True)
        students = state.get("students", {})

        self.logger.info("## Students Answer Node")

        if not questions:
            error_message = "Warning: No questions found. Please run the questioner node first."
            self.logger.warning(error_message)
            raise ValueError(error_message)

        if not generate_students:
            id = questions["id"]
            students_path = get_saved_students_path(id)
            if students_path.exists():
                with open(students_path, "r", encoding="utf-8") as f:
                    students = json.load(f)
                    self.logger.info(f"### Answer sheet of generated students: \n{students}")
                    if "response_matrix" not in students:
                        error_message = "Warning: No response matrix found."
                        self.logger.warning(error_message)
                        raise ValueError(error_message)

                    # return {"students": students, "self_ability": students["students"][0]["theta"]}
                    return {"students": students}
            else:
                error_message = "Warning: No students found. Beginning to generate students..."
                self.logger.warning(error_message)

        students["students"] = []

        # generate students one by one
        for i in range(num_students):
            theta = int(np.random.normal(0, 1.7))

            original_solution, generated_answers, reflections, failed = safe_extract_json(
                self.runnable,
                {"messages": [("user", "用户答题情况：\n" + str(questions["questions"]))], "theta": theta},
                start_tag="<start_json>",
                end_tag="</end_json>",
            )
            answer_sheet = generated_answers["answers"]

            self.logger.info(f"### Student {i} Answer sheet: \n{answer_sheet}")

            if len(questions["questions"]) != len(answer_sheet):
                error_message = (
                    f"The number of questions and answer sheet does not match. Please check the questioner node.\n \
                Number of questions: {len(questions['questions'])}, Number of answer sheet: {len(answer_sheet)}"
                )
                self.logger.warning(error_message)
                raise ValueError(error_message)

            student = {"id": f"{i}", "theta": theta, "answers": []}

            for question, answer in zip(questions["questions"], answer_sheet, strict=True):
                if int(question["id"]) != int(answer["id"]):
                    error_message = (
                        f"The question id and answer id does not match. Please check the questioner node.\n \
                        Question id: {int(question['id'])}, Answer id: {int(answer['id'])}"
                    )
                    self.logger.warning(error_message)
                    raise ValueError(error_message)

                student["answers"].append(
                    {
                        "id": f"{question['id']}",
                        "student_answer": f"{answer['student_answer']}",
                        "answer": f"{question['answer']}",
                        "difficulty": float(question["difficulty"]),
                        "discrimination": float(question["discrimination"]),
                        "correct": bool(question["answer"] == answer["student_answer"]),
                    }
                )

            students["students"].append(student)

        irt = IRT(students["students"])
        students["students"] = irt.update_question_user_params()
        students["discrimination"] = irt.irt_params["Discrimination"]
        students["difficulty"] = irt.irt_params["Difficulty"]

        # Convert numpy array to native Python types for serialization
        if hasattr(irt, "response_matrix") and isinstance(irt.response_matrix, np.ndarray):
            response_matrix = irt.response_matrix.tolist()
        else:
            response_matrix = []

        students["response_matrix"] = response_matrix

        # Get user ability and ensure it's a native Python float
        # self_ability = irt.get_user_ability(user_index=0)
        # if isinstance(self_ability, np.number):
        #     self_ability = float(self_ability)

        # Convert any remaining numpy types in students dictionary
        students = convert_numpy_to_native(students)

        temp_folder = get_tmp_folder("user_info")
        temp_folder.mkdir(parents=True, exist_ok=True)
        with open(temp_folder / f"{questions['id']}.json", "w", encoding="utf-8") as f:
            json.dump(students, f, ensure_ascii=False, indent=2)
        self.logger.info("Answer sheet of generated students saved")

        return {
            "students": students,
        }
