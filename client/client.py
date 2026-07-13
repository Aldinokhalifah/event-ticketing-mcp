from openai import AsyncOpenAI
from mcp import StdioServerParameters
from schemas import ChatRequest, ChatResponse
from mcp import ClientSession, stdio_client
from utils.system_prompt import SYSTEM_PROMPT
import json
import traceback  # tambahkan di atas
import os
from dotenv import load_dotenv
load_dotenv()

llm = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

server_params = StdioServerParameters(
    command="python",
    args=["server/server.py"],
    env={"API_BASE_URL": os.getenv("API_BASE_URL", "")}
)

async def run_agent(request: ChatRequest) -> ChatResponse:
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                }
                for tool in tools_result.tools
            ]

            actions_taken = []

            # Bangun conversation history
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            # Tambahkan history sebelumnya
            history = request.conversation_history or []
            for h in history[:-1]:  # ← [:-1] skip item terakhir
                messages.append({"role": h.role, "content": h.content})

            # Tambahkan pesan user terbaru
            message = request.message
            messages.append({"role": "user", "content": message})
            
            # Agent loop — maksimal 6 iterasi untuk hindari infinite loop
            max_iterations = 6
            iteration = 0
            
            while iteration <= max_iterations:
                iteration += 1

                response = llm.chat.completions.create(
                    model=os.getenv("OPENROUTER_MODEL"),
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    max_tokens=1000,
                    temperature=0.3,
                )
                
                choice = response.choices[0]
                message_response = choice.message
                
                # Kalau tidak ada tool call → LLM sudah selesai
                if not message_response.tool_calls:
                    return ChatResponse(
                        response=message_response.content or "Maaf, aku tidak bisa memproses permintaan ini.",
                        actions_taken=actions_taken
                    )
                
                if choice.finish_reason == "tool_calls":
                    # model minta eksekusi tool
                    # Tambahkan response LLM ke history
                    messages.append({
                        "role": "assistant",
                        "content": message_response.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in (message_response.tool_calls or [])
                        ] if message_response.tool_calls else None
                    })
                    
                    # loop setiap tool yang diminta
                    for tool_call in message_response.tool_calls:
                        # ambil nama dan arguments
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)

                        # inject token
                        tool_args['token'] = request.token
                        actions_taken.append(tool_name)

                        # eksekusi via MCP server
                        try:
                            tool_result = await session.call_tool(tool_name, tool_args)
                            result_str = json.dumps(
                                tool_result.content[0].text if tool_result.content else "Tool tidak mengembalikan hasil",
                                ensure_ascii=False
                            )
                        except Exception as e:
                            # Tambahkan print untuk debug
                            print(f"[Tool Error] {tool_name}: {str(e)}")
                            traceback.print_exc()
                            result_str = json.dumps({
                                "error": True,
                                "message": str(e)
                        }, ensure_ascii=False)

                        # append result ke messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_str
                        })

            return ChatResponse(
                response="Maaf, proses terlalu panjang dan dihentikan.",
                actions_taken=actions_taken
            )
