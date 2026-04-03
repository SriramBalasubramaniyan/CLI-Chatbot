import os
import pickle
from google.genai import types
from time import sleep
from extract_data import parse_plain_text, process_folder
from chunk_spliting import chunk_text
import __init__ as i
import faiss
import numpy as np
from local_embedding import LocalEmbeddingEngine

process_folder(i.source_folder, i.extract_folder)

documents=[]

for file in os.listdir(i.extract_folder):
    full_path = os.path.join(i.extract_folder, file)

    if not os.path.isfile(full_path):
        continue
    
    chunks = chunk_text(parse_plain_text(full_path))
    documents.extend(chunks)

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

embed_engine = LocalEmbeddingEngine()

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

        # emb = i.client.models.embed_content(
        #         model=i.embed_model_name,
        #         contents=doc                
        #     ).embeddings[0].values

        emb = embed_engine.create_embedding(doc)[0]

        doc_embedding.append((doc,emb))

    with open(i.cache_file_path, "wb") as f:
        pickle.dump(doc_embedding, f)

dimension = len(doc_embedding[0][1])
index = faiss.IndexFlatL2(dimension)
# vector = np.array([emb for _, emb in doc_embedding]).astype("float32")
vector = np.vstack([emb for _, emb in doc_embedding]).astype("float32")
index.add(vector)

while True:
    print()
    print("Query:",end="",flush=True)
    qry = input().lower().strip()
    
    if qry.lower() in ["exit", "quit"]:
        print("Exiting the chatbot. Goodbye!")
        break

    try:
        # qry_emb = i.client.models.embed_content(
        #     model=i.embed_model_name,
        #     contents=qry
        # ).embeddings[0].values

        qry_emb = embed_engine.create_embedding(qry)[0]

        # query_vector = np.array([qry_emb]).astype("float32")
        query_vector = np.vstack([qry_emb]).astype("float32")
        
        distance, indices = index.search(query_vector, k=3)

        top_k = [doc_embedding[i][0] for i in indices[0]]

        if not top_k:
            print("No relevant context found")
            continue

        context = "\n\n".join([f"-{doc}" for doc in top_k])

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