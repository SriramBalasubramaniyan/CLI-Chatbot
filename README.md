🤖 CLI Chatbot using Google GenAI

A simple command-line chatbot built using Google Generative AI (Gemini).
This chatbot maintains conversation history and generates responses using a selected model.

🚀 Features
•💬 Interactive CLI-based chatbot
•🧠 Maintains conversation history (context-aware responses)
•🔥 Uses Google GenAI (Gemini models)
•⚙️ Configurable temperature for response creativity
•📁 Automatically saves available model details to a file

🛠️ Tech Stack
•Python
•google-genai
•python-dotenv

📂 Project Structure
.
├── main.py
├── .env
└── data/
    └── models.txt

⚙️ Setup Instructions
Clone Repo -> 
  create virtual environment -> 
    install google-genai and python-dotenv packages -> 
      create .env file in root dir and declare API_KEY=your_google_genai_api_key ->
        specify model name in main.py model_name variable ->
          run the python file.

🧠 How It Works
1.Loads API key using .env
2.Fetches all available models from Google GenAI
3.Saves model details into data/models.txt
4.Starts an interactive CLI loop:
  •Takes user input
  •Appends it to conversation history
  •Sends request to model
  •Prints AI response
