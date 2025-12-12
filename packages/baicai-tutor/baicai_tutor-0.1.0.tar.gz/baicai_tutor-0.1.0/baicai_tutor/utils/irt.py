from typing import Any, List, Optional, TypedDict

import numpy as np
from girth import twopl_mml


def convert_numpy_to_native(obj):
    """
    Convert numpy types to native Python types for serialization.

    Args:
        obj: The object to convert

    Returns:
        The object with numpy types converted to native Python types
    """
    if isinstance(obj, np.ndarray):
        return [convert_numpy_to_native(item) for item in obj]
    elif isinstance(
        obj,
        (np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64),
    ):
        return int(obj)
    elif isinstance(obj, (np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_to_native(item) for item in obj]
    elif isinstance(obj, dict):
        return {convert_numpy_to_native(k): convert_numpy_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj


# Define TypedDicts for better structure understanding and type checking
class QuestionResponse(TypedDict):
    id: Any  # Or str, int
    answer: Any
    original_answer: Any
    difficulty: float
    discrimination: float
    correct: bool
    probability_correct: Optional[float]  # Added new field, make it optional for flexibility


class UserResponseJson(TypedDict):
    id: str
    theta: float
    answers: List[QuestionResponse]


def calculate_probability_correct(theta: float, discrimination: np.ndarray, difficulty: np.ndarray) -> List[float]:
    """
    Calculate probability of correct response using the 2PL model.

    Args:
        theta: User ability parameter
        discrimination: Array of discrimination parameters for each question
        difficulty: Array of difficulty parameters for each question

    Returns:
        List of probabilities of correct response for each question
    """
    if len(discrimination) != len(difficulty):
        raise ValueError(
            f"Mismatch between number of discrimination ({len(discrimination)}) "
            f"and difficulty ({len(difficulty)}) parameters."
        )

    probabilities = []
    for i in range(len(discrimination)):
        a = float(discrimination[i])
        b = float(difficulty[i])
        exponent = -a * (theta - b)
        prob = 1.0 / (1.0 + np.exp(exponent))
        probabilities.append(float(prob))

    return probabilities


class IRT:
    """
    Handles Item Response Theory calculations for a list of user response data.
    Internally, the response matrix is stored as (n_questions, n_users).
    Girth library functions expecting (n_users, n_questions) will receive a transposed view.

    The `response_json_list` input to the constructor should be a list,
    where each element is a dictionary structured as:
    {
      "id": "user_or_session_id_string",
      "theta": initial_user_ability_float,
      "questions": [
        {
          "id": "question_id_string_or_int",
          "answer": "user_submitted_answer",
          "original_answer": "correct_answer",
          "difficulty": initial_question_difficulty_float,
          "discrimination": initial_question_discrimination_float,
          "correct": boolean_is_user_answer_correct
        },
        // ... more questions (assumed to be the same set and order for all users)
      ]
    }
    """

    def __init__(self, response_json_list: List[UserResponseJson]):
        self.response_json_list: List[UserResponseJson] = response_json_list
        self.response_matrix = self.generate_response_matrix()  # Now (n_questions, n_users)
        self.irt_params = self.calculate_irt_params()  # Estimates item params

    def generate_response_matrix(self) -> np.ndarray:
        """
        Generate response matrix from a list of user response JSONs.
        It first constructs a matrix of (users, questions) and then transposes it.
        Assumes all users have the same questions in the same order.
        Output matrix shape will be (number_of_questions, number_of_users).
        """
        if not self.response_json_list:
            return np.array([]).reshape(0, 0)

        first_user_data = self.response_json_list[0]
        user_id_for_error = ""

        try:
            user_id_for_error = first_user_data.get("id", "first user")
            if "answers" not in first_user_data or not isinstance(first_user_data["answers"], list):
                raise ValueError(f"User '{user_id_for_error}' is missing 'answers' key or 'answers' is not a list.")

            expected_num_questions = len(first_user_data["answers"])
            num_users = len(self.response_json_list)

            # Handle 0 users or 0 questions explicitly for correct empty matrix shapes
            if num_users == 0:
                return np.array([]).reshape(0, 0)  # Shape (0,0) for no users
            if expected_num_questions == 0:  # num_users > 0 is implied here
                return np.array([]).reshape(0, num_users)  # Shape (0, num_users) if no questions

            all_users_correctness_vectors = []
            for user_idx, user_data in enumerate(self.response_json_list):
                user_id_for_error = user_data.get("id", f"user at index {user_idx}")
                if "answers" not in user_data or not isinstance(user_data["answers"], list):
                    raise ValueError(f"User '{user_id_for_error}' is missing 'answers' key or 'answers' is not a list.")
                current_user_questions_list = user_data["answers"]
                if len(current_user_questions_list) != expected_num_questions:
                    raise ValueError(
                        f"User '{user_id_for_error}' has {len(current_user_questions_list)} questions, "
                        f"but {expected_num_questions} were expected (based on the first user)."
                    )
                try:
                    correctness_vector = [int(q_resp["correct"]) for q_resp in current_user_questions_list]
                    all_users_correctness_vectors.append(correctness_vector)
                except KeyError as e_key:
                    offending_q_idx = -1
                    for q_idx, q_resp_dict in enumerate(current_user_questions_list):
                        if "correct" not in q_resp_dict:
                            offending_q_idx = q_idx
                            break
                    if offending_q_idx != -1:
                        raise KeyError(
                            f"'correct' key missing in question data at index {offending_q_idx} for user '{user_id_for_error}'."
                        )
                    else:
                        raise KeyError(
                            f"A key ({e_key}) is missing in a question response for user '{user_id_for_error}'. Review question structures."
                        )
                except (TypeError, ValueError) as e_val_type:
                    raise type(e_val_type)(
                        f"Error converting 'correct' field to int for a question for user '{user_id_for_error}': {e_val_type}"
                    )

            # If all_users_correctness_vectors is empty here, it implies expected_num_questions was > 0
            # but all current_user_questions_list were empty, which shouldn't happen due to len check.
            # Or, if expected_num_questions was 0, we would have returned earlier.
            # This check is more of a safeguard; the earlier returns for 0 questions / 0 users are key.
            if not all_users_correctness_vectors:  # Should not be hit if logic above is correct for non-empty users
                return np.array([]).reshape(expected_num_questions, num_users)  # or (0,0) if both are 0

            response_matrix_users_as_rows = np.array(all_users_correctness_vectors, dtype=int)
            return response_matrix_users_as_rows.T

        except Exception as e:
            raise ValueError(f"Error generating response matrix (context: around user '{user_id_for_error}'): {e}")

    def calculate_irt_params(self):
        """
        Calculate IRT item parameters (Difficulty, Discrimination, Ability) from the response matrix.
        The internal response matrix (self.response_matrix) is (n_questions, n_users),
        which is the format expected by girth's twopl_mml function as per documentation.
        """
        try:
            # Explicitly handle (0,0), (N,0), and (0,N) shapes for self.response_matrix
            # to ensure 'Ability' key is always part of the returned dict for consistency.
            if self.response_matrix.shape[0] == 0:  # No items/questions
                return {"Difficulty": np.array([]), "Discrimination": np.array([]), "Ability": np.array([])}
            if self.response_matrix.shape[1] == 0:  # No users (but potentially questions, e.g. shape (N,0) )
                return {"Difficulty": np.array([]), "Discrimination": np.array([]), "Ability": np.array([])}

            # If matrix has dimensions, proceed with twopl_mml
            return twopl_mml(self.response_matrix)
        except Exception as e:
            matrix_shape_info = self.response_matrix.shape if hasattr(self, "response_matrix") else "N/A"
            raise ValueError(
                f"Error calculating IRT parameters (input matrix shape for girth: {matrix_shape_info}): {e}"
            )

    def get_user_ability(self, user_index=-1) -> float:
        """
        Retrieves the estimated user ability from the pre-computed IRT parameters.
        Assumes 'Ability' array is populated in self.irt_params by calculate_irt_params
        (which calls girth's twopl_mml).
        Returns the ability estimate for the specified user_index.
        If user_index is -1 (default), returns the ability of the last user.
        """
        try:
            if not self.irt_params or "Ability" not in self.irt_params:
                raise ValueError(
                    "Ability parameters not found in self.irt_params. Ensure calculate_irt_params populates it via twopl_mml."
                )

            user_abilities = self.irt_params["Ability"]

            if not isinstance(user_abilities, np.ndarray):
                # twopl_mml should return a numpy array for 'Ability'. If not, it's unexpected.
                raise TypeError(f"Expected 'Ability' in irt_params to be a numpy array, got {type(user_abilities)}.")

            num_users_with_ability_estimates = len(user_abilities)

            if num_users_with_ability_estimates == 0:
                raise IndexError("No ability estimates available (empty Ability array).")

            # Handle negative indices (e.g., -1 for last user)
            if user_index == -1:
                user_index = num_users_with_ability_estimates - 1

            if not (0 <= user_index < num_users_with_ability_estimates):
                # Check against the length of the abilities array provided by twopl_mml
                raise IndexError(
                    f"user_index {user_index} is out of bounds. "
                    f"Available ability estimates for {num_users_with_ability_estimates} users (indices 0 to {num_users_with_ability_estimates - 1})."
                )

            return float(user_abilities[user_index])  # Ensure the return type is float

        except KeyError:  # Should be caught by the 'Ability' not in self.irt_params check
            raise ValueError("'Ability' key not found in self.irt_params.")
        except IndexError as e:  # If user_index is out of bounds for user_abilities array
            abilities_len = len(self.irt_params.get("Ability", [])) if self.irt_params else 0
            raise IndexError(
                f"Error accessing ability for user_index {user_index}: {e}. Abilities array length: {abilities_len}"
            )
        except Exception as e:  # Catch any other unexpected errors
            raise ValueError(f"Error getting user ability for user_index {user_index}: {e}")

    def get_question_irt_params(self):
        """
        Get the estimated question IRT parameters (Difficulty, Discrimination).
        These are derived from the full dataset.

        Returns:
            A tuple containing (difficulty_list, discrimination_list), where each list
            contains float values for each question. Both lists are the same length.
        """
        try:
            if not self.irt_params or "Difficulty" not in self.irt_params or "Discrimination" not in self.irt_params:
                raise ValueError("IRT parameters not calculated or do not contain Difficulty/Discrimination.")

            # Convert numpy arrays to lists of native Python types
            difficulty = [float(d) for d in self.irt_params["Difficulty"]]
            discrimination = [float(d) for d in self.irt_params["Discrimination"]]

            return difficulty, discrimination
        except Exception as e:
            raise ValueError(f"Error getting question IRT parameters: {e}") from e

    def probability_correct(self, user_idx: int) -> List[float]:
        """
        Calculates the probability of a correct response for all questions for a given user
        using the 2PL model.

        Args:
            user_idx: The index of the user in the response_json_list (0-based).

        Returns:
            A list of probabilities of a correct response (float) for each question.
            Returns an empty list if no questions are available.
        """
        try:
            if not self.irt_params:
                raise ValueError("IRT parameters have not been calculated yet. Call calculate_irt_params first.")

            required_keys = ["Discrimination", "Difficulty", "Ability"]
            for key in required_keys:
                if key not in self.irt_params:
                    raise ValueError(f"IRT parameter '{key}' not found in self.irt_params.")

            discrimination_params = self.irt_params["Discrimination"]
            difficulty_params = self.irt_params["Difficulty"]
            ability_params = self.irt_params["Ability"]

            if not (0 <= user_idx < len(ability_params)):
                raise IndexError(
                    f"user_idx {user_idx} is out of bounds for Ability array (len: {len(ability_params)}). Users are 0-indexed."
                )

            # Ensure theta is a native Python float
            theta = float(ability_params[user_idx])

            return calculate_probability_correct(theta, discrimination_params, difficulty_params)

        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"Error calculating probabilities for user_idx={user_idx}: {e}")
        except Exception as e:
            raise ValueError(
                f"An unexpected error occurred while calculating probabilities for user_idx={user_idx}: {e}"
            )

    def update_question_user_params(self) -> List[UserResponseJson]:
        """
        Update user and question parameters with calculated IRT values.
        Ensures all values are native Python types for serialization.

        Returns:
            A list of user response JSON objects with updated parameters.
        """
        try:
            updated_response_json_list = []
            difficulty_params, discrimination_params = self.get_question_irt_params()

            for user_idx, user_data in enumerate(self.response_json_list):
                user_copy = user_data.copy()

                # Update theta with estimated ability if available
                if "Ability" in self.irt_params and user_idx < len(self.irt_params["Ability"]):
                    user_copy["theta"] = float(self.irt_params["Ability"][user_idx])

                # Calculate probability correct for each question for this user
                # Skip probability calculation if no abilities are available or array is empty
                probabilities = []
                if "Ability" in self.irt_params and len(self.irt_params["Ability"]) > user_idx:
                    try:
                        probabilities = self.probability_correct(user_idx)
                    except ValueError:
                        # If we can't calculate probabilities, continue with empty list
                        probabilities = []

                # Update question parameters
                updated_answers = []
                for q_idx, q_data in enumerate(user_data["answers"]):
                    q_copy = q_data.copy()

                    # Update difficulty and discrimination if available
                    if q_idx < len(difficulty_params):
                        q_copy["difficulty"] = float(difficulty_params[q_idx])

                    if q_idx < len(discrimination_params):
                        q_copy["discrimination"] = float(discrimination_params[q_idx])

                    # Add probability of correct response
                    if q_idx < len(probabilities):
                        q_copy["probability_correct"] = float(probabilities[q_idx])
                    else:
                        # Set to None if not available
                        q_copy["probability_correct"] = None

                    # Ensure correct is a native boolean
                    if "correct" in q_copy:
                        q_copy["correct"] = bool(q_copy["correct"])

                    # Convert any other numpy types to native types
                    q_copy = convert_numpy_to_native(q_copy)

                    updated_answers.append(q_copy)

                user_copy["answers"] = updated_answers

                # Convert any remaining numpy types to native types at the user level
                user_copy = convert_numpy_to_native(user_copy)

                updated_response_json_list.append(user_copy)

            return updated_response_json_list

        except Exception as e:
            raise ValueError(f"Error updating question and user parameters: {e}") from e


# Example usage (for illustration, not part of the class)
if __name__ == "__main__":
    # Sample data with 3 questions for more interesting probabilities
    sample_user_1_data: UserResponseJson = {
        "id": "user1",
        "theta": 0.0,
        "answers": [
            {
                "id": "q1",
                "answer": "A",
                "original_answer": "A",
                "difficulty": -1.0,
                "discrimination": 1.5,
                "correct": True,
                "probability_correct": None,
            },
            {
                "id": "q2",
                "answer": "B",
                "original_answer": "C",
                "difficulty": 0.0,
                "discrimination": 1.0,
                "correct": False,
                "probability_correct": None,
            },
            {
                "id": "q3",
                "answer": "D",
                "original_answer": "D",
                "difficulty": 1.0,
                "discrimination": 0.8,
                "correct": True,
                "probability_correct": None,
            },
        ],
    }
    sample_user_2_data: UserResponseJson = {
        "id": "user2",
        "theta": 0.1,
        "answers": [
            {
                "id": "q1",
                "answer": "B",
                "original_answer": "A",
                "difficulty": -1.0,
                "discrimination": 1.5,
                "correct": False,
                "probability_correct": None,
            },
            {
                "id": "q2",
                "answer": "C",
                "original_answer": "C",
                "difficulty": 0.0,
                "discrimination": 1.0,
                "correct": True,
                "probability_correct": None,
            },
            {
                "id": "q3",
                "answer": "E",
                "original_answer": "D",
                "difficulty": 1.0,
                "discrimination": 0.8,
                "correct": False,
                "probability_correct": None,
            },
        ],
    }

    print("--- Initializing IRT Instance ---")
    try:
        irt_instance = IRT([sample_user_1_data, sample_user_2_data])
        print("Response Matrix (questions x users):\n", irt_instance.response_matrix)
        print("\n--- Calculated IRT Parameters ---")
        print(irt_instance.irt_params)

        print("\n--- Individual User Abilities ---")
        print("Ability User 0:", irt_instance.get_user_ability(user_index=0))
        print("Ability User 1:", irt_instance.get_user_ability(user_index=1))

        print("\n--- P(Correct) for User 0 (All Questions) ---")
        probs_user0 = irt_instance.probability_correct(user_idx=0)
        print(probs_user0)

        print("\n--- Updated User/Question Params (including P(Correct)) ---")
        updated_data = irt_instance.update_question_user_params()
        # Example: Show updated difficulty and P(Correct) for User 0, Question 1 (index 0)
        if updated_data and updated_data[0]["answers"]:
            print("Updated Data Example (User 0, Q1):")
            print("  Difficulty:", updated_data[0]["answers"][0]["difficulty"])
            print("  Discrimination:", updated_data[0]["answers"][0]["discrimination"])
            print("  P(Correct):", updated_data[0]["answers"][0]["probability_correct"])
        # Pretty print the first user's updated data
        # import json
        # print("\nUpdated Data User 0 (Full):\n", json.dumps(updated_data[0], indent=2))

    except ValueError as e:
        print(f"\nError during IRT processing: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
