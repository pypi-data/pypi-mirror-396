from baicai_base.configs import ConfigManager, LLMConfig
from baicai_base.services import LLM
from langchain_core.prompts import ChatPromptTemplate

QUESTIONS = [
    {
        "id": 1,
        "question": "以下是关于线性回归的代码示例，问：如何通过代码实现线性回归来预测房价？",
        "options": ["从头开始实现线性回归", "使用现有的机器学习库", "使用统计学库", "不需要代码，可以直接计算"],
        "answer": 0,
        "explanation": "线性回归是机器学习中的基础算法之一，通常我们会使用现有的机器学习库（如scikit-learn）来实现线性回归，以提高效率和准确性。从头开始实现线性回归虽然可行，但在实际应用中并不常见，且容易出错。因此，使用现有的机器学习库是最合适的选择。",
        "difficulty": -2,
        "discrimination": 0.5,
    },
    {
        "id": 2,
        "question": "在以下代码中，如何通过梯度下降法优化线性回归模型？",
        "options": ["使用随机梯度下降法", "使用批量梯度下降法", "使用最小二乘法", "不需要优化，直接计算"],
        "answer": 0,
        "explanation": "梯度下降法是一种常用的优化算法，用于最小化线性回归模型的损失函数。随机梯度下降法（SGD）是一种常见的梯度下降实现方式，它通过逐个样本更新参数来优化模型。在代码中，我们可以看到对损失函数的计算和参数的更新，这与随机梯度下降法的实现相符。",
        "difficulty": 2,
        "discrimination": 1.5,
    },
    {
        "id": 3,
        "question": "在以下代码中，如何通过正则化来防止过拟合？",
        "options": ["添加L1正则化项", "添加L2正则化项", "增加训练数据量", "减少模型的特征数量"],
        "answer": 1,
        "explanation": "正则化是一种防止过拟合的技术，通过在损失函数中添加惩罚项来限制模型的复杂度。在代码中，我们可以看到正则化项的添加，这通常是L2正则化（即Ridge回归）。L2正则化通过添加模型权重的平方和来惩罚复杂模型，从而防止过拟合。",
        "difficulty": 0,
        "discrimination": 1.0,
    },
]

STUDENT = """
# Role
You are simulating a student with ability level {theta} for Item Response Theory (IRT) models.
- You will be given a list of questions with options in json format.
- You must answer questions honestly as that student.

## Ability level
* -3: Very low level, may answer every question wrong
* -2: Low level
* -1: A little low level
* 0: Medium level
* 1: A little high level
* 2: High level
* 3: Very high level, may answer every question correctly

## Output
Output should be in the format of JSON strickly, be sure start with <start_json> and end with </end_json>:
<start_json>
{{
    "answers": [
    {{
        "id": "id of the input questions",
        "student_answer": "Your answer of the option index, like 0, 1, 2, 3...",
    }},
    ...
    ]
}}
</end_json>
"""


def student(llm=None):
    llm = llm or LLM().llm
    student_template = ChatPromptTemplate.from_messages(
        [
            ("system", STUDENT),
            ("placeholder", "{messages}"),
        ]
    )
    return student_template | llm


if __name__ == "__main__":
    # --- Configuration Details for qwen_config ---
    config_id = "qwen_t7"
    provider = "groq"
    model_name = "qwen-qwq-32b"
    temperature = 0.7
    # --- ---

    # Ensure the qwen_config configuration exists
    manager = ConfigManager()
    config_path = manager.get_config_path(config_id)

    if not config_path.exists():
        print(f"Configuration file '{config_path}' not found. Creating it...")
        qwen_llm_config = LLMConfig(
            provider=provider,
            model_name=model_name,
            temperature=temperature,
        )
        manager.save_config(config_id, qwen_llm_config)
        print(f"Configuration '{config_id}' saved successfully.")
    else:
        print(f"Configuration '{config_id}' already exists at '{config_path}'.")

    # Now invoke the hinter, which uses config_id="qwen_config" internally

    llm = LLM(config_id="qwen").llm

    questions = [
        {
            "id": q["id"],
            "question": q["question"],
            "options": q["options"],
        }
        for q in QUESTIONS
    ]
    student_result = student(llm=llm).invoke(
        {
            "messages": [("user", str(questions))],
            "theta": -3,
        }
    )
    print(student_result.content)
