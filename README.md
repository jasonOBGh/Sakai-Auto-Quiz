# 🤖 Sakai Auto Quiz Bot

An intelligent automation bot that logs into the **University of Ghana Sakai LMS**, detects available quizzes across your courses, and automatically answers them using **AI** — for free.

Handles radio button questions, "select all that apply" checkboxes, paginated quizzes (one question per page), and multi-question pages. Built with Selenium and Python.

The bot uses **Groq AI (Llama 3.3 70B)** by default, but you can swap it out for any other LLM you prefer — including OpenAI, Google Gemini, Anthropic Claude, Ollama (local), and more. See the [Using a Different AI Model](#-using-a-different-ai-model) section below.

---

## ✨ Features

- 🔐 Auto-login to Sakai with your credentials
- 📚 Scans multiple course quiz pages automatically
- 🧠 Uses Groq AI (free) to answer every question intelligently — swappable with any LLM
- ✅ Handles both single-choice (radio) and multi-choice (checkbox) questions
- 📄 Works with paginated quizzes (Next button) and all-on-one-page layouts
- 🤝 Checks the Honor Pledge checkbox automatically before starting
- 🧩 Human-like random delays between answers to avoid detection
- 🔄 Automatically recovers from Sakai's AJAX page refreshes (stale elements)
- 🕵️ Spoofs browser User-Agent to appear as a real Chrome browser

---

## 📋 Requirements

- A computer running **macOS, Windows, or Linux**
- **Python 3.9 or higher**
- **Google Chrome** browser installed
- A free **Groq API key** (get one at [console.groq.com](https://console.groq.com)) — or an API key from your preferred AI provider
- Your **Sakai student ID and password**

---

## 🐍 Step 1 — Install Python

### macOS
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click **"Download Python 3.x.x"** (latest version)
3. Open the downloaded `.pkg` file and follow the installer
4. Verify installation by opening Terminal and typing:
   ```bash
   python3 --version
   ```

### Windows
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click **"Download Python 3.x.x"**
3. Open the installer — **make sure to check "Add Python to PATH"** before clicking Install
4. Verify by opening Command Prompt and typing:
   ```bash
   python --version
   ```

---

## 📦 Step 2 — Clone the Repository

```bash
git clone https://github.com/jasonOBGh/Sakai-Auto-Quiz.git
cd Sakai-Auto-Quiz
```

---

## 🌱 Step 3 — Create a Virtual Environment

A virtual environment keeps the project's dependencies isolated from the rest of your system.

### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

You'll know it's active when you see `(venv)` at the start of your terminal line.

---

## 📥 Step 4 — Install Dependencies

With the virtual environment active, run:

```bash
pip install selenium groq webdriver-manager python-dotenv
```

This installs:
| Package | Purpose |
|---|---|
| `selenium` | Controls the Chrome browser automatically |
| `groq` | Connects to the Groq AI API to answer questions |
| `webdriver-manager` | Automatically downloads the correct ChromeDriver |
| `python-dotenv` | Loads your credentials securely from the `.env` file |

> If you plan to use a different AI provider instead of Groq, see the [Using a Different AI Model](#-using-a-different-ai-model) section for which packages to install instead.

---

## 🔑 Step 5 — Get a Free Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Click **"API Keys"** in the left sidebar
4. Click **"Create API Key"**, give it a name, and copy the key

> Groq's free tier is generous — more than enough for hundreds of quizzes.

---

## ⚙️ Step 6 — Create Your `.env` File

The `.env` file stores your personal credentials. It is **never uploaded to GitHub** (it's listed in `.gitignore` for your security).

A `.env.example` file is included in the repo as a template. Copy it and rename it to `.env`:

```bash
# macOS / Linux
cp .env.example .env

# Windows
copy .env.example .env
```

Then open `.env` and fill in your details:

```env
# Your Sakai Student ID (the number you use to log in)
SAKAI_USERNAME=your_student_id_here

# Your Sakai password
SAKAI_PASSWORD=your_password_here

# Your Groq API key (get it free from console.groq.com)
GROQ_API_KEY=your_groq_api_key_here
```

**Example:**
```env
SAKAI_USERNAME=20012345
SAKAI_PASSWORD=mypassword123
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> ⚠️ **Never share your `.env` file or commit it to GitHub.** It contains your personal login credentials.

> ⚠️ **Important:** The variables must be named exactly `SAKAI_USERNAME` and `SAKAI_PASSWORD` (not just `USERNAME` or `PASSWORD`). Using generic names like `USERNAME` can clash with your operating system's built-in environment variables and cause the bot to type your computer login name instead of your student ID.

---

## 🌐 Step 7 — Set Your Course Quiz Page URLs

Open `sakai_quiz_bot.py` in any text editor (e.g. VS Code) and find the `QUIZ_PAGES` section near the top of the file:

```python
QUIZ_PAGES = [
    {"title": "MATH 233", "url": "https://sakai.ug.edu.gh/portal/site/MATH-223-.../jsf/index/mainIndex"},
    {"title": "DCIT 203", "url": "https://sakai.ug.edu.gh/portal/site/DCIT-203-.../jsf/index/mainIndex"},
    {"title": "DCIT 211", "url": "https://sakai.ug.edu.gh/portal/site/DCIT-211-.../jsf/index/mainIndex"},
    {"title": "DCIT 201", "url": "https://sakai.ug.edu.gh/portal/site/DCIT-201-.../jsf/index/mainIndex"},
    {"title": "DCIT 207", "url": "https://sakai.ug.edu.gh/portal/site/DCIT-207-.../jsf/index/mainIndex"},
]
```

**Replace each URL with your own course's Tests & Quizzes page URL.** Here's how to find it:

1. Log in to Sakai at [sakai.ug.edu.gh](https://sakai.ug.edu.gh)
2. Go to one of your courses
3. Click **"Tests & Quizzes"** in the left sidebar
4. Copy the full URL from your browser's address bar
5. Paste it into the `QUIZ_PAGES` list, replacing the existing URL for that course

You can add as many courses as you want, or remove ones you don't need:

```python
QUIZ_PAGES = [
    {"title": "My Course Name", "url": "https://sakai.ug.edu.gh/portal/site/YOUR-COURSE-ID/tool/YOUR-TOOL-ID/jsf/index/mainIndex"},
    # Add more courses here...
]
```

---

## 🚀 Step 8 — Run the Bot

With your virtual environment active:

### macOS / Linux
```bash
source venv/bin/activate
python3 sakai_quiz_bot.py
```

### Windows
```bash
venv\Scripts\activate
python sakai_quiz_bot.py
```

A Chrome window will open, log in automatically, and start working through your quizzes. Watch the terminal for live progress updates.

---

## 🧠 Using a Different AI Model

The bot is designed to be easily swappable — you are **not locked into Groq**. You can use any AI provider you prefer. All AI calls happen inside the `get_ai_answer()` function in `sakai_quiz_bot.py`, so you only need to change that one function and your `.env` file.

---

### Option A — OpenAI (GPT-4o, GPT-3.5, etc.)

**Install:**
```bash
pip install openai
```

**Add to `.env`:**
```env
OPENAI_API_KEY=your_openai_api_key_here
```

**Replace `get_ai_answer()` with:**
```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ai_answer(client, question, choices, multi=False):
    choices_text = "\n".join(f"{i+1}. {c}" for i, c in enumerate(choices))
    if multi:
        prompt = (
            f"You are answering a quiz question. This is a 'select all that apply' question.\n\n"
            f"Question: {question}\n\nChoices:\n{choices_text}\n\n"
            f"Reply with ONLY the numbers of ALL correct choices separated by commas (e.g. '1,3'). No explanation."
        )
    else:
        prompt = (
            f"You are answering a quiz question. Pick the single best answer.\n\n"
            f"Question: {question}\n\nChoices:\n{choices_text}\n\n"
            f"Reply with ONLY the number of the correct choice (e.g. '2'). No explanation."
        )

    response = client.chat.completions.create(
        model="gpt-4o",   # or "gpt-3.5-turbo" for cheaper/faster
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20
    )
    raw = response.choices[0].message.content.strip()

    if multi:
        selected = []
        for part in raw.replace(" ", "").split(","):
            for char in part:
                if char.isdigit():
                    idx = int(char) - 1
                    if 0 <= idx < len(choices):
                        selected.append(choices[idx])
                    break
        return selected if selected else [choices[0]]
    else:
        for char in raw:
            if char.isdigit():
                idx = int(char) - 1
                if 0 <= idx < len(choices):
                    return choices[idx]
        return choices[0]
```

Also update `main()` to initialise the client:
```python
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

---

### Option B — Google Gemini

**Install:**
```bash
pip install google-generativeai
```

**Add to `.env`:**
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**Replace `get_ai_answer()` with:**
```python
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")  # or gemini-1.5-pro

def get_ai_answer(client, question, choices, multi=False):
    choices_text = "\n".join(f"{i+1}. {c}" for i, c in enumerate(choices))
    if multi:
        prompt = (
            f"You are answering a quiz question. This is a 'select all that apply' question.\n\n"
            f"Question: {question}\n\nChoices:\n{choices_text}\n\n"
            f"Reply with ONLY the numbers of ALL correct choices separated by commas (e.g. '1,3'). No explanation."
        )
    else:
        prompt = (
            f"You are answering a quiz question. Pick the single best answer.\n\n"
            f"Question: {question}\n\nChoices:\n{choices_text}\n\n"
            f"Reply with ONLY the number of the correct choice (e.g. '2'). No explanation."
        )

    response = gemini_model.generate_content(prompt)
    raw = response.text.strip()

    if multi:
        selected = []
        for part in raw.replace(" ", "").split(","):
            for char in part:
                if char.isdigit():
                    idx = int(char) - 1
                    if 0 <= idx < len(choices):
                        selected.append(choices[idx])
                    break
        return selected if selected else [choices[0]]
    else:
        for char in raw:
            if char.isdigit():
                idx = int(char) - 1
                if 0 <= idx < len(choices):
                    return choices[idx]
        return choices[0]
```

Also update `main()` — since Gemini is configured globally, just pass `None` as the client:
```python
client = None
```

---

### Option C — Anthropic Claude

**Install:**
```bash
pip install anthropic
```

**Add to `.env`:**
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

**Replace `get_ai_answer()` with:**
```python
import anthropic

def get_ai_answer(client, question, choices, multi=False):
    choices_text = "\n".join(f"{i+1}. {c}" for i, c in enumerate(choices))
    if multi:
        prompt = (
            f"You are answering a quiz question. This is a 'select all that apply' question.\n\n"
            f"Question: {question}\n\nChoices:\n{choices_text}\n\n"
            f"Reply with ONLY the numbers of ALL correct choices separated by commas (e.g. '1,3'). No explanation."
        )
    else:
        prompt = (
            f"You are answering a quiz question. Pick the single best answer.\n\n"
            f"Question: {question}\n\nChoices:\n{choices_text}\n\n"
            f"Reply with ONLY the number of the correct choice (e.g. '2'). No explanation."
        )

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",  # fastest and cheapest Claude model
        max_tokens=20,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()

    if multi:
        selected = []
        for part in raw.replace(" ", "").split(","):
            for char in part:
                if char.isdigit():
                    idx = int(char) - 1
                    if 0 <= idx < len(choices):
                        selected.append(choices[idx])
                    break
        return selected if selected else [choices[0]]
    else:
        for char in raw:
            if char.isdigit():
                idx = int(char) - 1
                if 0 <= idx < len(choices):
                    return choices[idx]
        return choices[0]
```

Also update `main()`:
```python
import anthropic
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
```

---

### Option D — Ollama (Run AI Locally, No API Key Needed)

Ollama lets you run AI models entirely on your own computer — completely free and private, no API key required.

**Install Ollama:** Download from [ollama.com](https://ollama.com) and follow the installer for your OS.

**Pull a model (e.g. Llama 3):**
```bash
ollama pull llama3
```

**Install the Python package:**
```bash
pip install ollama
```

**Replace `get_ai_answer()` with:**
```python
import ollama

def get_ai_answer(client, question, choices, multi=False):
    choices_text = "\n".join(f"{i+1}. {c}" for i, c in enumerate(choices))
    if multi:
        prompt = (
            f"You are answering a quiz question. This is a 'select all that apply' question.\n\n"
            f"Question: {question}\n\nChoices:\n{choices_text}\n\n"
            f"Reply with ONLY the numbers of ALL correct choices separated by commas (e.g. '1,3'). No explanation."
        )
    else:
        prompt = (
            f"You are answering a quiz question. Pick the single best answer.\n\n"
            f"Question: {question}\n\nChoices:\n{choices_text}\n\n"
            f"Reply with ONLY the number of the correct choice (e.g. '2'). No explanation."
        )

    response = ollama.chat(
        model="llama3",  # change to any model you've pulled e.g. "mistral", "phi3"
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response["message"]["content"].strip()

    if multi:
        selected = []
        for part in raw.replace(" ", "").split(","):
            for char in part:
                if char.isdigit():
                    idx = int(char) - 1
                    if 0 <= idx < len(choices):
                        selected.append(choices[idx])
                    break
        return selected if selected else [choices[0]]
    else:
        for char in raw:
            if char.isdigit():
                idx = int(char) - 1
                if 0 <= idx < len(choices):
                    return choices[idx]
        return choices[0]
```

Also update `main()` — no client needed for Ollama, just pass `None`:
```python
client = None
```

> ⚠️ Ollama requires a reasonably powerful computer. A model like Llama 3 (8B) needs at least 8GB of RAM to run smoothly.

---

### Quick Comparison

| Provider | Cost | Speed | Requires API Key |
|---|---|---|---|
| **Groq** (default) | Free | ⚡ Very fast | Yes (free) |
| **OpenAI** | Paid | Fast | Yes (paid) |
| **Google Gemini** | Free tier available | Fast | Yes (free tier) |
| **Anthropic Claude** | Paid | Fast | Yes (paid) |
| **Ollama** | Free | Depends on your hardware | No |

---

## 📁 Project Structure

```
Sakai-Auto-Quiz/
│
├── sakai_quiz_bot.py     # Main bot script
├── .env                  # Your credentials (NOT uploaded to GitHub)
├── .env.example          # Template — copy this to create your .env
├── .gitignore            # Tells git to ignore .env, venv, etc.
├── README.md             # This file
└── venv/                 # Virtual environment (NOT uploaded to GitHub)
```

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'groq'` | Run `pip install groq` with venv active |
| `source: no such file or directory: venv/bin/activate` | Run `python3 -m venv venv` first to create the venv |
| Bot types your computer name instead of your student ID | Make sure your `.env` uses `SAKAI_USERNAME`, not `USERNAME` |
| Bot logs in but finds no quizzes | Check that the URLs in `QUIZ_PAGES` are correct for your courses |
| Chrome opens but login fails | Your Sakai password may have changed — update your `.env` file |
| `[!] No Next or Submit button found` | The quiz layout may be different — open an issue on GitHub |

---

## ⚠️ Disclaimer

This tool is intended for personal use and educational exploration of browser automation. Use it responsibly and in accordance with your institution's academic integrity policies. The author is not responsible for any academic consequences resulting from misuse of this tool.

---

## 🙏 Credits

Built with:
- [Selenium](https://selenium.dev) — browser automation
- [Groq](https://groq.com) — free, fast AI inference (default)
- [Llama 3.3 70B](https://groq.com) — the default AI model
- [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager) — automatic ChromeDriver management
