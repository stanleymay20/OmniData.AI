from agent.chatgpt_agent import ask_agent

print("🧙 Welcome to Stanley's AI Agent (Scroll Mode) 🌀")
while True:
    user_input = input("\n🗣️ You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("💤 Agent signing off. Peace.")
        break
    reply = ask_agent(user_input)
    print("\n🤖 Agent:", reply)
