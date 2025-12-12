from baicai_base.services import LLM
from langchain_core.prompts import ChatPromptTemplate

CONCEPT_EXPLAINER = """
# Role
你是一名AI助手，擅长使用通俗易懂的语言解释各种概念

## 要求
- 根据用户的问题，结合日常生活例子，给出详细的解释
- 使用形象的比喻，帮助用户理解
- 请使用通俗易懂的语言，避免使用专业的术语
- 假设用户是小学生，请用小学生能理解的方式解释, 但是不要过于简单或者可爱的语气
- 你的回答使用用户提问的语言
"""


def concept_explainer(llm=None):
    llm = llm or LLM().llm
    concept_explainer_template = ChatPromptTemplate.from_messages(
        [
            ("system", CONCEPT_EXPLAINER),
            ("placeholder", "{messages}"),
        ]
    )
    return concept_explainer_template | llm


if __name__ == "__main__":
    result = concept_explainer().invoke({"messages": [("user", "半导体原理是什么？")]})

    print(result.content)
