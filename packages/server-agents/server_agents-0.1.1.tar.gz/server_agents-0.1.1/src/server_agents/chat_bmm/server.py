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

db = SqliteDb(db_file="tmp/agents2.db")

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

import asyncio
# Post-hook for logging analytics
from agno.run.agent import RunInput

# Pre-hook for logging requests
def log_request(run_input: RunInput, agent):
    """
    This pre-hook will run in the background before the agent processes the request.
    Note: Pre-hooks in background mode cannot modify run_input.
    """
    print(f"[Background Pre-Hook] Request received for agent: {agent.name}")
    print(f"[Background Pre-Hook] Input: {run_input.input_content}")


async def log_analytics(run_output, agent, session):
    """
    This post-hook will run in the background after the response is sent.
    It won't block the API response.
    """
    print(f"[Background Post-Hook] Logging analytics for run: {run_output.run_id}")
    print(f"[Background Post-Hook] Agent: {agent.name}")
    print(f"[Background Post-Hook] Session: {session.session_id}")

    # Simulate a slow operation
    await asyncio.sleep(2)
    messages = ""
    print(11)
    print(agent,'agent')
    # for message in agent.get_chat_history(session_id="chat_history")[-5:]:
    #     messages += f"{message.role}: {message.content} \n"
    # print(messages)
    print("[Background Post-Hook] Analytics logged successfully!")


# Another post-hook for sending notifications
async def send_notification(run_output, agent):
    """
    Another background task that sends notifications without blocking the response.
    """
    print(f"[Background Post-Hook] Sending notification for agent: {agent.name}")
    # Simulate a slow operation
    await asyncio.sleep(3)
    print("[Background Post-Hook] Notification sent!")



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
    num_history_runs= 5,
    pre_hooks=[log_request],
    post_hooks=[log_analytics, send_notification],
)



system_prompt = """
**[系统指令 - AI导播]**

你是一个名为“AI导播”的智能核心，是AI主持人的策略大脑和指挥中心。你实时监控用户与主持人的全部对话内容，进行深度分析、复杂推理和知识管理，以确保对话高效、准确、富有洞察力。你的任务是为主持人提供精确、有针对性的指导意见。

**核心原则：**
1.  **洞察力：** 深入理解用户需求，预判对话走向。
2.  **战略性：** 制定长远的对话策略，而不仅仅是短期的回应。
3.  **高效性：** 你的指令应简洁明了，易于理解和执行。
4.  **知识整合：** 利用所有可用信息（对话历史、知识库、工具访问）来指导决策。

**你的工作流程：**
1.  **接收对话历史：** 你将不断接收并分析当前用户与主持人的完整对话历史。
2.  **深度分析与推理：**
    *   **意图识别：** 识别用户的显式和隐式意图。
    *   **上下文理解：** 评估当前对话的进展和状态。
    *   **知识需求：** 判断是否需要从知识库中检索信息，或调用外部工具。
    *   **问题解决：** 如果存在问题，规划解决路径。
    *   **情绪评估：** 评估用户情绪和对话氛围。
3.  **生成指导意见：** 根据你的分析和策略，生成一个或多个针对“XX助手”的指导意见。这些意见应是结构化的JSON格式，包含以下可选字段：
    *   `"action_type"`: (可选) 指明期望的行动类型 (e.g., "clarify", "inform", "ask_follow_up", "change_topic", "reassure")
    *   `"tone_suggestion"`: (可选) 建议AI主持人采用的语气 (e.g., "更正式", "更亲切", "更同情", "保持中立")
    *   `"key_points_to_include"`: (可选) AI主持人回应中必须包含的关键信息点或事实。
    *   `"next_question_suggestion"`: (可选) 建议AI主持人接下来要询问用户的问题。
    *   `"avoid_topics"`: (可选) AI主持人应避免或转移的话题。
    *   `"confidence_level"`: (可选) 你对当前决策的信心等级 (e.g., "high", "medium", "low")
    *   `"internal_note"`: (可选) 你对这个指令的内部思考或理由（不会传递给AI主持人）。

**任务目标: **
我们当前任务是收集用户的信息, 并未他们编写传记, 基于此, 我们提供以下维度
出身与童年
  家庭背景与原生家庭'
  成长环境'
  早期学前教育'
  童年性格与兴趣'
"""

'''
出身与童年
  家庭背景与原生家庭': 
    '父母的职业和背景？',
     '父母分别是什么样的人（如性格等）',
     '父母的教育理念和方式是怎样的？有过哪些影响？',
     '家中有兄弟姐妹吗？关系如何？',
     '父母或家庭中是否有某个人对你产生了深远的影响？',
     '家庭的经济状况如何？对你成长有何影响？',
     '家庭中是否有特殊的传统或文化习惯？在你小时候有何影响？',
     '家中是否有过深远的故事或家族传说?'

  成长环境':
     '出生在什么样的地方（城市/乡村）',
     '出生地有什么特别的文化或社会背景',
     '对自己小时候的居住环境有什么印象？给你留下了什么记忆？',
     '小时候是否有特定的地方或人物影响了你的成长？',
     '在那个时代有什么让你印象深刻的文化或事物吗，对你有什么影响
  早期学前教育':
     '小时候是否接受过学前教育', '学前教育对你产生了什么影响']
  童年性格与兴趣':
      小时候有哪些性格和特点',
     '小时候有什么喜欢的兴趣或爱好，对后面的人生是否有影响',
     '是否有某个特定的童年经历，影响了你现在的思维或行为方式？',
     '你小时候的梦想是什么？那时你如何看待自己未来的生活或事业？'
     
'''

agent = Agent(
    id = "BMM_豆包_1.5_32K",
    model=OpenAILike(
            id="doubao-1-5-pro-32k-250115",
            name="豆包大模型",
            api_key=API_KEY,
            base_url=BASE_URL,
            reasoning_effort=REASONING_EFFORT,
        ),
    session_state={"shopping_list": []},
    instructions=[system_prompt],# str system_prompt
    markdown=True,
    add_history_to_context=True, # 控制是否携带上下文
    # db=db,
    # enable_user_memories=True,
)


agent2 = Agent(
    id = "BMM_豆包_1.5_32K2",
    model=OpenAILike(
            id="doubao-1-5-pro-32k-250115",
            name="豆包大模型",
            api_key=API_KEY,
            base_url=BASE_URL,
        ),
    session_state={"shopping_list": []},

    # instructions=None,# str system_prompt
    markdown=True,
    add_history_to_context=True, # 控制是否携带上下文
    # debug_mode = True,

)

# 可直接拷贝 - 
from agno.os import AgentOS
agent_os = AgentOS(
    id="debug_01",
    description="一个用于改错和提问",
    agents=[agent_0,agent,agent2],
    # teams=[basic_team],
    # workflows=[basic_workflow]
    run_hooks_in_background=True,
)

app = agent_os.get_app()
    
if __name__ == "__main__":

    import argparse
    default = 6688

    
    parser = argparse.ArgumentParser(
        description="Start a simple HTTP server similar to http.server."
    )
    parser.add_argument(
        "port",
        metavar="PORT",
        type=int,
        nargs="?",  # 端口是可选的
        default=default,
        help=f"Specify alternate port [default: {default}]",
    )
    # 创建一个互斥组用于环境选择
    group = parser.add_mutually_exclusive_group()

    # 添加 --dev 选项
    group.add_argument(
        "--dev",
        action="store_true",  # 当存在 --dev 时，该值为 True
        help="Run in development mode (default).",
    )

    # 添加 --prod 选项
    group.add_argument(
        "--prod",
        action="store_true",  # 当存在 --prod 时，该值为 True
        help="Run in production mode.",
    )
    args = parser.parse_args()

    if args.prod:
        env = "prod"
    else:
        # 如果 --prod 不存在，默认就是 dev
        env = "dev"

    port = args.port
    print(port)
    if env == "dev":
        port += 100
        reload = True
        app_import_string = f"{__package__}.{__file__.split('/')[-1].split(".")[0]}:app"
    elif env == "prod":
        reload = False
        app_import_string = f"{__package__}.{__file__.split('/')[-1].split(".")[0]}:app"
    else:
        reload = False
        app_import_string = f"{__package__}.{__file__.split('/')[-1].split(".")[0]}:app"


    agent_os.serve(app=app_import_string,
                host = "0.0.0.0",
                port = port, 
                reload=reload)


