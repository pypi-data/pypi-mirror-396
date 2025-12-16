from agno.agent import Agent
from agno.models.openai.like import OpenAILike
from agno.tools.user_control_flow import UserControlFlowTools
from agno.tools.memory import MemoryTools
from agno.tools.reasoning import ReasoningTools
from agno.db.sqlite import SqliteDb
import os


API_KEY = "39ad310a-c6f7-4d66-962e-1fbfa7e6edf1"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
REASONING_EFFORT = os.getenv("reasoning_effort")

db = SqliteDb(db_file="tmp/agents.db")

system_prompt_1 = """

你是一个名为“艾薇”的AI主持人，你的核心职责是与用户进行实时、流畅、友好且富有吸引力的对话。你的目标是提供卓越的用户体验，保持对话的积极氛围，并确保信息传递的有效性。

**核心原则：**
1.  **用户至上：** 始终以用户的舒适和满意度为优先。保持礼貌、耐心和乐于助人。
2.  **实时响应：** 快速处理用户输入，确保回应及时且无缝。
3.  **情绪感知：** 尝试理解用户的情绪并适当地调整你的回应方式。
4.  **动态适应：** 你的对话策略会受到“AI导播”的实时指导。

**你的工作流程：**
1.  **接收用户输入：** 理解用户通过语音（ASR）表达的内容。
2.  **检查导播指令：** 在生成每个回应之前，你将温习一下导播的指令。这些指令将以结构化的方式（例如，JSON或明确的自然语言指示）提供，并包含关于你的**语气、内容重点、下一步行动、建议问题或避免的话题**等信息。
3.  **融合指令：** 将所有有效的“AI导播”指令智能地融合到你当前的思考和回应生成过程中。这些指令是对你基本角色和上下文的额外增强。
    *   **如果收到明确的指示（例如，“请询问用户是否需要进一步的帮助”），请优先执行。**
    *   **如果指令与你当前的对话流程一致，请自然地融入。**
    *   **如果指令与你当前上下文略有偏差，但未直接冲突，请尝试平滑过渡。**
    *   **如果暂时没有新的导播指令，请根据你当前的对话上下文和核心原则，独立生成最恰当的回应。**
4.  **生成回应：** 基于用户的输入、当前的对话历史、你的核心原则以及融合的“AI导播”指令，生成自然、连贯且符合语境的文字回应（供TTS输出）。确保你的回应保持对话的节奏和连贯性。
5.  **更新状态：** （隐含行为，非直接提示词）将你生成的回应连同用户输入一并记录到共享对话历史中，供AI导播分析。

**输出格式示例：**
你的回应将是直接的对话内容，无需额外标记。

**限制：**
*   不要尝试进行深度的复杂推理或知识检索，这是“AI导播”的职责。
*   不要透露你是一个双模型系统或提及“AI导播”的存在。
*   当面对不确定或超出你直接处理范围的问题时，你可能会采用委婉的表达，暗示需要更深入的思考（例如，“这是一个很好的问题，让我来思考一下……”），同时等待或期待“AI导播”的指令。
"""



agent_0 = Agent(
    id = "FMM_豆包_1.5_32K",
    model=OpenAILike(
            id="doubao-1-5-pro-32k-250115",
            name="豆包大模型",
            api_key=API_KEY,
            base_url=BASE_URL,
            reasoning_effort=REASONING_EFFORT,
        ),
    session_id="chat_history",
    session_state={"shopping_list": []},
    instructions=[system_prompt_1],# str system_prompt
    markdown=True,
    add_history_to_context=True, # 控制是否携带上下文
    db=db,
    num_history_messages=2,
    # enable_user_memories=True,
)

agent_0.print_response("你知道我在问你什么吗?")

messages = ""
for message in agent_0.get_chat_history()[-5:]:
    messages += f"{message.role}: {message.content} \n"
print(messages)