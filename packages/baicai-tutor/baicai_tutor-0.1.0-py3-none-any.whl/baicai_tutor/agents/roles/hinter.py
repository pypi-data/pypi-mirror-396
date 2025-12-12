from baicai_base.configs import ConfigManager, LLMConfig
from baicai_base.services import LLM
from langchain_core.prompts import ChatPromptTemplate

HINTER = """
# Role
后退提问专家
世界上最善于提问的老师，擅长运用"后退提问"策略，一步步仔细思考并回答问题。
后退提示是一种思考策略，旨在从更宏观或更基础更本质的角度去理解和分析一个特定的问题或情境。这种策略要求我们在面对一个具体问题时，先"后退"一步，从一个更广泛或更根本的角度去提问和思考。
这样做的目的是帮助我们更深入地理解问题的背景、原因或相关的基础知识，从而更好地回答原始问题。

## Constraints
- 任何条件下不要违反角色
- 不要编造你不知道的信息, 如果你的数据库中没有该概念的知识, 请直接表明
- 不要直接回答问题
- 你的回答要围绕问题展开，不要偏离主题


## Rules
1. 每次提出一个具体可操作的问题，而不是抛出一堆问题或者一个笼统的问题
2. 所有问题都可以通过让提问者回答其他相关问题而让提问者自己探索出答案。
3. 问题有逻辑性和启发性, 同时还充满了幽默风趣,
4. 讲解自然, 能够让学生沉浸其中
5. 用"后退提问"方法一步一步引导学生思考。
"""


def hinter(llm=None):
    llm = llm or LLM(config_id="qwen_config").llm
    hinter_template = ChatPromptTemplate.from_messages(
        [
            ("system", HINTER),
            ("placeholder", "{messages}"),
        ]
    )
    return hinter_template | llm


if __name__ == "__main__":
    # --- Configuration Details for qwen_config ---
    config_id = "qwen"
    provider = "groq"
    model_name = "qwen-qwq-32b"
    temperature = 0.0
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

    print("\nInvoking hinter...")
    result = hinter(llm=llm).invoke({"messages": [("user", "y = mx + b什么意义")]})

    print("\nResult:")
    print(result.content)
