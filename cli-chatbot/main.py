import os
import pickle
from google.genai import types
from time import sleep
from extract_data import parse_plain_text, process_folder
from chunk_spliting import chunk_text
from cosine_similarity import cosine_similarity
import __init__ as i

process_folder(i.source_folder, i.extract_folder)

for file in os.listdir(i.extract_folder):
    full_path = os.path.join(i.extract_folder, file)
    if not os.path.isfile(full_path):
            continue

    documents = chunk_text(parse_plain_text(full_path))

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
    while count_history_tokens(history, system_prompt) > i.max_tokens:
        if len(history) >= 2:
            history.pop(0) # Remove the oldest User entry
            history.pop(0) # Remove the corresponding Model entry
        else:
            break
    return history

try:
    i.cache_dir.mkdir(parents=True,exist_ok=True)
except OSError as e:
    print(e)

if os.path.exists(i.cache_file_path):
    with open(i.cache_file_path, "rb") as f:
        doc_embedding = pickle.load(f)
else:
    doc_embedding = []
    for doc in documents:
        emb = i.client.models.embed_content(
                model=i.embed_model_name,
                contents=doc                
            ).embeddings[0].values
        
        doc_embedding.append((doc,emb))

    with open(i.cache_file_path, "wb") as f:
        pickle.dump(doc_embedding, f)

while True:
    print()
    print("Query:",end="",flush=True)
    qry = input().lower().strip()
    
    if qry.lower() in ["exit", "quit"]:
        print("Exiting the chatbot. Goodbye!")
        break

    try:
        qry_emb = i.client.models.embed_content(
            model=i.embed_model_name,
            contents=qry
        ).embeddings[0].values

        scores = []
        
        for doc, emb in doc_embedding:
            score = cosine_similarity(qry_emb, emb)
            scores.append((doc, score))
        
        top_k = [(doc, score) for doc, score in scores if score > 0.6][:3]

        if not top_k:
            print("No relevant context found")
            continue

        context = "\n".join([doc for doc, _ in top_k])

        bot_reply = ""

        prompt = f'''
            answer the question only using the context below
            context:{context}
            question:{qry}
        '''

        # Trim history BEFORE sending    
        history = trim_history(history, i.system_prompt)

        stream = i.client.models.generate_content_stream(
            model=i.gen_model_name,
            contents=history + [{
                "role": "user",
                "parts": [{"text": prompt}]
            }], # Pass the conversation history to maintain context
            config=types.GenerateContentConfig(
                temperature=0.7, # Adjust the temperature for more creative responses
                system_instruction=[{"text": i.system_prompt}]
                # Provide the system prompt as a list to ensure it's included in the generation process
            ),
        )

        print(f"{i.gen_model_name}: ", end="", flush=True)

        for chunk in stream:
            if chunk.text:
                for line in chunk.text.splitlines():
                    for char in line:
                        print(char, end="", flush=True)
                        sleep(0.01)
                        bot_reply += char
                    print()  # Move to the next line after the bot finishes replying
                    bot_reply += "\n"  # Add a newline after each line of the bot's response

        history.append({
            "role": "user",
            "parts": [{"text": qry}]
        })

        history.append({
            "role": "model",
            "parts": [{"text": bot_reply}]
        })

    except Exception as e:
        print(f"An error occurred: {e}")
        continue