import os
import pathlib
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()

model_info = []

client = genai.Client(api_key=os.getenv("API_KEY"))

for model in client.models.list():
    model_info.append(model)

def update_model_information_in_file(filename, model_list):
    folder = pathlib.Path("../data")
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