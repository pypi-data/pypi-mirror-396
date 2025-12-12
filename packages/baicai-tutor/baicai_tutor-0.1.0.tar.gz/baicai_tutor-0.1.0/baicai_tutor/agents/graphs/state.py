from typing import Dict, List, Optional, TypedDict

import numpy as np


class TutorState(TypedDict):
    """State management for the tutor graph.

    Attributes:
        messages: List of tuples containing user-assistant message history.
            Format: [("user", "request"), ("assistant", "response")]
        fail_fast: Whether the graph should fail fast.
        surveys: List of surveys.
        profile: Profile of the user.
        questions: List of questions.
        user_answers: List of user answers.
        students: students.
        response_matrix: Response matrix.
        user: User.
        error_message: Error message.

    """

    messages: List[tuple[str, str]]
    fail_fast: bool
    surveys: List[Dict]
    profile: Dict
    questions: Dict
    students: Dict
    user_answers: List[Dict]
    response_matrix: np.ndarray
    user: Dict
    error_message: Optional[str]
