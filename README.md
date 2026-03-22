<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>CLI Chatbot using Google GenAI</title>

  <style>
    body {
      font-family: Arial, sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      margin: 0;
      padding: 0;
      line-height: 1.6;
    }

    .container {
      max-width: 900px;
      margin: auto;
      padding: 30px;
    }

    h1, h2 {
      color: #38bdf8;
    }

    h1 {
      text-align: center;
      margin-bottom: 10px;
    }

    p.subtitle {
      text-align: center;
      color: #94a3b8;
      margin-bottom: 30px;
    }

    .card {
      background: #1e293b;
      padding: 20px;
      border-radius: 12px;
      margin-bottom: 20px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    ul {
      padding-left: 20px;
    }

    li {
      margin-bottom: 8px;
    }

    code {
      background: #020617;
      padding: 4px 6px;
      border-radius: 6px;
      color: #facc15;
    }

    .steps li {
      margin-bottom: 10px;
    }

    footer {
      text-align: center;
      margin-top: 40px;
      color: #64748b;
    }
  </style>
</head>

<body>

  <div class="container">

    <h1>🤖 CLI Chatbot</h1>
    <p class="subtitle">Built using Google Generative AI (Gemini)</p>

    <div class="card">
      <p>
        A simple command-line chatbot built using Google Generative AI (Gemini).
        This chatbot maintains conversation history and generates intelligent,
        context-aware responses using a selected model.
      </p>
    </div>

    <div class="card">
      <h2>🚀 Features</h2>
      <ul>
        <li>💬 Interactive CLI-based chatbot</li>
        <li>🧠 Maintains conversation history (context-aware responses)</li>
        <li>🔥 Uses Google GenAI (Gemini models)</li>
        <li>⚙️ Configurable temperature for response creativity</li>
        <li>📁 Automatically saves available model details to a file</li>
      </ul>
    </div>

    <div class="card">
      <h2>🛠️ Tech Stack</h2>
      <ul>
        <li>Python</li>
        <li>google-genai</li>
        <li>python-dotenv</li>
      </ul>
    </div>

    <div class="card">
      <h2>📂 Project Structure</h2>
      <pre>
.
├── main.py
├── .env
└── data/
    └── models.txt
      </pre>
    </div>

    <div class="card">
      <h2>⚙️ Setup Instructions</h2>
      <ul class="steps">
        <li>Clone the repository</li>
        <li>Create a virtual environment</li>
        <li>Install dependencies:
          <br><code>pip install google-genai python-dotenv</code>
        </li>
        <li>Create a <code>.env</code> file in the root directory:</li>
        <li><code>API_KEY=your_google_genai_api_key</code></li>
        <li>Specify model name in <code>main.py</code></li>
        <li>Run the project:
          <br><code>python main.py</code>
        </li>
      </ul>
    </div>

    <div class="card">
      <h2>🧠 How It Works</h2>
      <ol>
        <li>Loads API key using <code>.env</code></li>
        <li>Fetches all available models from Google GenAI</li>
        <li>Saves model details into <code>data/models.txt</code></li>
        <li>Starts an interactive CLI loop:
          <ul>
            <li>Takes user input</li>
            <li>Appends it to conversation history</li>
            <li>Sends request to model</li>
            <li>Prints AI response</li>
          </ul>
        </li>
      </ol>
    </div>

    <footer>
      🚀 Built for learning & experimentation with Gemini AI
    </footer>

  </div>

</body>
</html>
