import os
import pathlib
from time import sleep
from dotenv import load_dotenv
import google.genai as genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("API_KEY"))

model_info = []

for model in client.models.list():
    model_info.append(model)

def update_model_information_in_file(filename, model_list):
    folder = pathlib.Path("data")
    file_path = folder / filename
    folder.mkdir(exist_ok=True)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("[\n")  # Start the list bracket
            
            for i, model in enumerate(model_list):
                f.write(f"  {repr(model)}")                
                if i < len(model_list) - 1:
                    f.write(",\n")
                else:
                    f.write("\n")
                    
            f.write("]")  # End the list bracket

    except Exception as e:
        print(f"Error saving to file: {e}")

update_model_information_in_file("models.txt", model_info)

history = []

model_name = "" # Specify the model you want to use, e.g., "gemini-1.5-pro"

system_prompt = """
    You are a senior software engineer.

    Rules:
    - Answer in bullet points
    - Explain step by step
    """

if model_name == "":
    model_name = client.models.list()[0].name

while True:
    if len(str(history))>8000:
        history = history[-6:] 

    user_input = input("You: ") # Get user input from the command line

    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the chatbot. Goodbye!")
        break

    history.append({
        "role": "user",
        "parts": [{"text": user_input}]
    })
    
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
                        sleep(0.1)  # Simulate typing delay
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