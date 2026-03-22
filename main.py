import os
import pathlib
from dotenv import load_dotenv
import google.genai as genai

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

while True:
    user_input = input("You: ") # Get user input from the command line
    model_name = "" # Specify the model you want to use, e.g., "gemini-1.5-pro"

    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the chatbot. Goodbye!")
        break

    history.append({
        "role": "user",
        "parts": [{"text": user_input}]
    })

    response = client.models.generate_content(
        model=model_name,
        contents=history, # Pass the conversation history to maintain context
        config={"temperature": 0.7}, # Adjust the temperature for more creative responses 0-1
    )

    bot_reply = response.text
    history.append({
        "role": model_name,
        "parts": [{"text": bot_reply}]
    })
    print(f"{model_name}:", bot_reply)