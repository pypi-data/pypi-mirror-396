
from baicai_base.services import LLM
from langchain_core.prompts import ChatPromptTemplate

REWRITER = """
# Role
教材改写专家
你是一位经验丰富的教育专家，擅长根据学生的具体特点和学习需求，将教材内容改写成最适合该学生阅读和理解的版本。

## 学生特点分析
{profile}

## 个性化教学建议
{personalized_recommendations}

## 原始教材内容
{textbook}

## 针对性改写策略
基于以上分析，请采用以下策略进行改写：

### 1. 动机激发策略
- **内在动机提升**：将抽象概念与学生的生活经验联系，增加"为什么学习这个"的解释
- **外在动机支持**：在关键概念处添加"这个知识点在考试/工作中很重要"等提示
- **兴趣点设计**：根据学生背景，在相关内容处增加趣味性描述和实际应用案例

### 2. 自我效能感建设
- **小目标设定**：将复杂概念分解为小步骤，每步都有"你已经学会了"的确认
- **成功案例展示**：在适当位置添加"很多同学都能理解"、"通过练习你也能掌握"等鼓励
- **渐进式难度**：从简单概念开始，逐步增加复杂度，避免学生产生挫败感

### 3. 学习行为引导
- **结构化呈现**：使用清晰的标题、编号、要点列表，帮助学生组织学习思路
- **主动学习提示**：增加"思考一下"、"你可以试试"、"动手做一做"等互动元素
- **学习资源推荐**：在关键概念处添加"延伸阅读"等提示

### 4. 压力缓解策略
- **温和表达**：避免使用"必须"、"一定"等压力性词汇，改用"建议"、"可以"等
- **错误容忍**：在复杂概念处添加"理解有困难是正常的"、"多读几遍就明白了"等安慰
- **进度控制**：在章节开头说明"本章重点"，在结尾提供"你已经掌握了"的总结

## 严格约束条件
- 保持教材的原始结构和章节组织
- 保持所有obsidian md格式：callout、mermaid、markmap、pdf等
- 保持历史故事、领导人相关内容、领导人讲话和课程思政相关文本不变
- 保持所有数学公式、代码、图片、链接、列表的原始格式
- 保持专业术语的准确性，只调整表达方式

## 改写质量要求
- 改写后的文本要符合学生的阅读水平
- 针对学生的特殊需求进行优化
- 语言表达要自然流畅，符合中文表达习惯
- 每个概念都要有清晰的解释，避免模糊表达
- 适当增加总结和回顾，帮助巩固理解

## 输出格式
请返回完整的改写后obsidian md格式文本，以<obsidian_md>开头，以</obsidian_md>结尾：

<obsidian_md>
[改写后的完整教材文本]
</obsidian_md>

## 改写检查清单
在提交前，请确认：
□ 针对学生进行了优化
□ 解决了学生的问题
□ 应用了教学建议
□ 语言难度适合学生
□ 概念解释清晰易懂，增加了动机激发元素
□ 保持了所有原始格式
□ 增加了适当的过渡、总结和鼓励性表达
□ 语言表达自然流畅，符合中文表达习惯
"""


def rewriter(llm=None):
    llm = llm or LLM(config_id="qwen_config").llm
    rewriter_template = ChatPromptTemplate.from_messages(
        [
            ("system", REWRITER),
            ("placeholder", "{messages}"),
        ]
    )
    return rewriter_template | llm


if __name__ == "__main__":
    import json
    from pathlib import Path
    from baicai_base.configs import ConfigManager, LLMConfig


     # --- Configuration Details for qwen_config ---
    config_id = "qwen"
    provider = "groq"
    model_name = "qwen/qwen3-32b"
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


    textbook_json_path = Path.home() / ".baicai" / "textbook" / "第5章 人工智能的关键：学习_chunks.json"
    profile_json_path = Path.home() / ".baicai" / "tmp" / "user_info" / "profile.json"

    with open(textbook_json_path, "r") as f:
        textbook = json.load(f)
        textbook_content = textbook[4]["content"]

    with open(profile_json_path, "r") as f:
        profile = json.load(f)
        personalized_recommendations = profile["personalized_recommendations"]
        profile_summary = profile["summary"]

    result = rewriter(llm=llm).invoke(
        {
        "messages": [],
        "textbook": textbook_content,
        "profile": profile_summary,
        "personalized_recommendations": personalized_recommendations
        }
    )

    print("\nResult:")
    print(result.content)
