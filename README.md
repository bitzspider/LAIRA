# LAIRA: Langchain Artificial Intelligence Research Assistant  

**LAIRA** is an intelligent research assistant designed to process research queries by performing web searches and generating comprehensive reports. This project simplifies research by integrating real-time web data.  

🚀 **Runs locally with Ollama and a built-in web scraping search function.**  
✅ **No API subscription required.**  
💯 **100% FREE**  

---

## 📖 Installation Instructions  

### 1️⃣ Clone the Repository  
Open your terminal and run:  
```sh
git clone https://github.com/bitzspider/LAIRA.git  
cd LAIRA
```

### 2️⃣ Create a Virtual Environment  
#### Windows (CMD/PowerShell)  
```sh
python -m venv venv  
venv\Scripts\activate
```
#### macOS/Linux  
```sh
python3 -m venv venv  
source venv/bin/activate
```

### 3️⃣ Install Dependencies  
With the virtual environment activated, install the required packages:  
```sh
pip install -r requirements.txt
```

### 4️⃣ Run the Application  
Start the application by executing:  
```sh
python main.py
```

---

## 🛠️ Resources Used  
- [LangChain](https://python.langchain.com/en/latest/) - Framework for building LLM-powered applications  
- [Ollama](https://ollama.com/) - Local LLM execution  
- [Selenium](https://www.selenium.dev/) - Web scraping and automation  
- [Gradio](https://www.gradio.app/) - Simple UI for AI applications  

---

## ⚙️ Configuring LLM & Research Assistants  

LAIRA uses **locally installed LLMs** via **Ollama**. You can configure which LLM model to use by modifying the `.env` file.

### 🔹 LLM Selection & Ollama  
- **USE_OLLAMA**: Set to `true` to enable **Ollama** for local LLM execution.  
- **OLLAMA_MODEL**: Defines the LLM model (default: `llama3.1`).  
- **No API or cloud processing required**—everything runs **entirely on your machine**.  

### 🔹 Researcher Configuration  
LAIRA operates using **three AI research assistants**, each with a specific role:  

| Researcher | Role | Description |
|------------|------|-------------|
| **Lead Researcher** | `RESEARCHER_0` | Manages workflow, decides if further research is needed. |
| **Search Researcher** | `RESEARCHER_1` | Performs web searches and filters relevant data. |
| **Report Researcher** | `RESEARCHER_2` | Generates a structured research report. |

Each researcher is assigned:  
- **An LLM model** (`llama3.1` by default).  
- **A toolset** (e.g., web search capabilities).  
- **A defined role** with specialized tasks.  

These settings can be modified in the `.env` file to customize **research depth**, **search iterations**, and **reporting structure**.

---

## 📌 Usage  
1. Once the application is running, open your web browser and navigate to the provided URL (commonly [http://127.0.0.1:7860](http://127.0.0.1:7860)).  
2. Enter your research query into the interface and let **LAIRA** process your query.  
3. Review the generated report and refine your search if needed.  
