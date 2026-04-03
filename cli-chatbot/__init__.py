import os
from dotenv import load_dotenv
import google.genai as genai
from pathlib import Path

load_dotenv()

client = genai.Client(api_key=os.getenv("API_KEY"))

max_tokens = int(os.getenv("Max_Tokens").strip() or 8000)

max_history_length = int(os.getenv("Max_History_Length").strip() or 6)

script_dir = os.path.dirname(os.path.abspath(__file__))

cache_file = "embeddings.pkl"
cache_dir = Path.cwd()/"data"

cache_file_path = cache_dir/cache_file

source_folder = os.getenv("SOURCE_FOLDER_NAME").strip() or "source"
extract_folder = os.getenv("EXTRACT_FOLDER_NAME").strip() or "extract"

gen_model_name = ""

if gen_model_name == "":
    gen_model_name = os.getenv("GEN_MODEL_NAME").strip() or client.models.list()[0].name

embed_model_name = ""

if embed_model_name == "":
    embed_model_name = os.getenv("EMBEDDING_MODEL_NAME").strip() or "BAAI/bge-base-en-v1.5"
    # "gemini-embedding-001"

system_prompt = """
    Rules:
    - Answer in friendly and easy to understand terms,
    - Explain step by step when necessary like implementation or if the user question requires step by step guide,
    - Do not use outside knowledge,
    - Do not hallucinate,
    - If you don't have the answer, don't make something up instead inform the user,
    - Never share any personal information or sensitive data
    """