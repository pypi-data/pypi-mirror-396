from agno.agent import Agent
from agno.models.openai.like import OpenAILike
from agno.tools.user_control_flow import UserControlFlowTools
from agno.tools.memory import MemoryTools
from agno.tools.reasoning import ReasoningTools
from agno.db.sqlite import SqliteDb
import os


API_KEY = os.getenv("api_key")
BASE_URL = os.getenv("base_url")
REASONING_EFFORT = os.getenv("reasoning_effort")
print(API_KEY,'API_KEY')
print(BASE_URL,'BASE_URL')

db = SqliteDb(db_file="tmp/agents.db")



agent = Agent(
    id = "debug_agent",
    model=OpenAILike(
            id="gemini-2.5-flash-preview-05-20-thinking",
            name="Agno Agent",
            api_key=API_KEY,
            base_url=BASE_URL,
            reasoning_effort=REASONING_EFFORT,
        ),
    session_state={"shopping_list": []},
    db=db,
    tools=[
        ReasoningTools(add_instructions=True,# 许多工具包都带有预先编写的指导，解释如何使用其工具。设置add_instructions=True将这些指令注入代理提示中
                       # ReasoningTools(enable_think=True, enable_analyze=True,
                       add_few_shot=True # 给定几个预编写好的 few - shot
                      ),
        MemoryTools(db=db, 
                    add_instructions=True,
                    add_few_shot=True,
                    enable_analyze=True,
                    enable_think=True,
                      ),
        UserControlFlowTools()
    ],
    # instructions=None,# str system_prompt
    markdown=True,
    add_history_to_context=True, # 控制是否携带上下文
    # debug_mode = True,
)
