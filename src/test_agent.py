import os
import json
import litert_lm

MODEL_PATH = os.path.expanduser(
    os.getenv(
        "LITERT_MODEL_PATH",
        "~/litert-models/models/gemma-4-E2B-it.litertlm"
    )
)

mock_tool_registry = {
    "name": "execute_bash_command",
    "description": "Executes a shell command inside the secure OpenClaw workspace.",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "The exact shell command string to run."},
            "timeout_seconds": {"type": "integer", "default": 5}
        },
        "required": ["command"]
    }
}

system_instruction = f"""
You are an OpenClaw AI Core. You must solve the user's objective by executing tools.
Available Tool:
{json.dumps(mock_tool_registry, indent=2)}

To use a tool, you MUST output a raw valid JSON object matching this structural schema:
{{
  "tool": "execute_bash_command",
  "arguments": {{
    "command": "your_command_here",
    "timeout_seconds": 5
  }}
}}
Respond with the JSON block ONLY. Do not wrap it in markdown block tags, and do not write conversational filler text.
"""

user_objective = "Check the contents of the root workspace directory to find out what files are available."

print("🚀 Initializing LiteRT-LM CPU Engine...")
try:
    with litert_lm.Engine(MODEL_PATH) as engine:
        with engine.create_conversation() as conversation:
            full_prompt = f"System: {system_instruction}\nUser: {user_objective}\nAssistant:"
            print("🧠 Generating tool schema call structure...")
            raw_response = ""
            
            for chunk in conversation.send_message_async(full_prompt):
                try:
                    if isinstance(chunk, dict):
                        content = chunk.get("content", {})
                        text = content.get("text", "") if isinstance(content, dict) else str(content)
                    else:
                        content = getattr(chunk, "content", "")
                        text = getattr(content, "text", str(content))
                except Exception:
                    text = str(chunk)
                
                raw_response += text
                print(text, end="", flush=True)
            print("\n" + "="*40)
            
            print("🔍 Evaluating JSON structural validity...")
            try:
                parsed_json = json.loads(raw_response.strip())
                if "tool" in parsed_json and "arguments" in parsed_json:
                    print("✅ Success! The model parsed the schema perfectly.")
                    print(f"   Target Command: {parsed_json['arguments'].get('command')}")
                else:
                    print("❌ Failure: Missing required OpenClaw keys ('tool' or 'arguments').")
            except json.JSONDecodeError:
                print("❌ Failure: Model did not output valid raw JSON.")
except Exception as e:
    print(f"💥 Engine runtime exception occurred: {e}")
