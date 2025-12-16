from agno.os import AgentOS

from server_agents.debug.core import agent as debug_agent
from server_agents.code.template.core import agent as code_template_agent


agent_os = AgentOS(
    id="debug_01",
    description="一个用于改错和提问",
    agents=[debug_agent, code_template_agent],
    # teams=[basic_team],
    # workflows=[basic_workflow]
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


