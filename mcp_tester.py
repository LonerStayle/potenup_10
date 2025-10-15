from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import asyncio
from dotenv import load_dotenv

load_dotenv()
import os


async def main():
    MCP_KEY = os.getenv("MCP_KEY")

    client = MultiServerMCPClient(
        {
            # 테스트용 mcp 는 미국 날씨를 가져오는 mcp로 세팅했어욤
            "weather": {
                "command": "cmd",
                "args": [
                    "/c",
                    "npx",
                    "-y",
                    "@smithery/cli@latest",
                    "run",
                    "@meowhuman/weather",
                    "--key",
                    MCP_KEY,
                ],
                "transport": "stdio",
            },
        }
    )

    # MCP 도구를 가져옵니다.
    tools = await client.get_tools()
    print(tools)
    # react 패턴의 agent 생성 했어요 궁금하시면 더 말씀해주십셔
    # tools 인자를 넣음으로써, agent 생성할 때 도구를 쥐어주는 겁니다.
    agent = create_react_agent("openai:gpt-4.1", tools)

    user_query = input("질문을 입력하세요: ")
    response = await agent.ainvoke({"messages": user_query})
    print(response)


# 실행 법은 uv run ~현재파일 경로.py
if __name__ == "__main__":
    asyncio.run(main())


