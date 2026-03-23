import os
from time import sleep
from dotenv import load_dotenv
import google.genai as genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("API_KEY"))

max_tokens = int(os.getenv("Max_Tokens", 8000))

max_history_length = int(os.getenv("Max_History_Length", 6))

model_name = "" # Specify the model you want to use, e.g., "gemini-1.5-pro"

system_prompt = """
    You are a senior software engineer.

    Rules:
    - Answer in bullet points
    - Explain step by step
    - Max 50 words
    - If you don't know the answer, say "I don't know" instead of making up an answer.
    - Never share any personal information or sensitive data.
    """

if model_name == "":
    model_name = client.models.list()[0].name

history = []

def estimate_tokens(text):
    return int(len(text) / 4)  # Rough estimate: 1 token ≈ 4 characters

def count_history_tokens(history, system_prompt):
    total_tokens = estimate_tokens(system_prompt)
    for entry in history:
        for part in entry["parts"]:
            total_tokens += estimate_tokens(part["text"])
    return total_tokens

def trim_history(history, system_prompt):
    while count_history_tokens(history, system_prompt) > max_tokens:
        if len(history) >= 2:
            history.pop(0) # Remove the oldest User entry
            history.pop(0) # Remove the corresponding Model entry
        else:
            break
    return history

while True:
    user_input = input("You: ") # Get user input from the command line

    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the chatbot. Goodbye!")
        break

    history.append({
        "role": "user",
        "parts": [{"text": user_input}]
    })
    
    # Trim history BEFORE sending    
    history = trim_history(history, system_prompt)

    bot_reply = ""
    
    try:
        stream = client.models.generate_content_stream(
            model=model_name,
            contents=history, # Pass the conversation history to maintain context
            config=types.GenerateContentConfig(
                temperature=0.7, # Adjust the temperature for more creative responses
                system_instruction=[{"text": system_prompt}]
                # Provide the system prompt as a list to ensure it's included in the generation process
            ),
        )

        print(f"{model_name}: ", end="", flush=True)

        for chunk in stream:
            if chunk.text:
                for line in chunk.text.splitlines():
                    for char in line:
                        print(char, end="", flush=True)
                        sleep(0.01)
                        bot_reply += char
                    print()  # Move to the next line after the bot finishes replying
                    bot_reply += "\n"  # Add a newline after each line of the bot's response

    except Exception as e:
        print(f"Error generating response: {e}")
        continue

    history.append({
        "role": "model",
        "parts": [{"text": bot_reply}]
    })