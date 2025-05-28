import openai
import json
import os
import logging

# Load API key from environment variable or .env
openai.api_key = os.getenv("OPENAI_API_KEY")

MEMORY_FILE = "agent/memory.json"

# Load or initialize memory

def load_memory():
    path = "agent/memory.json"
    default_memory = [
        {
            "role": "system",
            "content": "You are Stanley's personal AI agent. Stay scroll-aligned, remember his goals, and speak with power and clarity."
        }
    ]
    # Auto-repair if file doesn't exist
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(default_memory, f, indent=4)
        return default_memory

    # Try to load and auto-fix if corrupt
    try:
        with open(path, "r") as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Memory must be a list")
            return data
    except Exception as e:
        logging.warning(f"⚠️ Memory file corrupted: {e}. Rebuilding memory.json...")
        with open(path, "w") as f:
            json.dump(default_memory, f, indent=4)
        return default_memory
    
def save_memory(messages):
    with open(MEMORY_FILE, "w") as f:
        json.dump(messages, f, indent=2)

def ask_agent(prompt):
    memory = load_memory()
    memory.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=memory,
        temperature=0.7
    )

    reply = response['choices'][0]['message']['content']
    memory.append({"role": "assistant", "content": reply})
    save_memory(memory)
    return reply
