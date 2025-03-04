1. **Clone the Repository**  
   Open your terminal and run:  
   ```bash
   git clone https://github.com/bitzspider/LAIRA.git
   cd LAIRA
   ```

2. **Create a Virtual Environment**  
   It’s best to work within a virtual environment.  
   - **For Windows (CMD/PowerShell):**  
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```  
   - **For macOS/Linux:**  
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies**  
   With the virtual environment activated, run:  
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**  
   Start the application by executing:  
   ```bash
   python main.py
   ```

5. **Usage**  
   Once the application is running, open your web browser and go to the URL provided by Gradio (commonly [http://127.0.0.1:7860](http://127.0.0.1:7860)).  
   - Enter your research query into the interface.  
   - LAIRA will process your query, perform web searches, and generate a comprehensive report.


