# Legal AI Assistant for Law Enforcement

A robust, AI-powered assistant designed to support law enforcement agencies in legal research, FIR management, and intelligent query handling. Built with Rasa, FastAPI, and modern NLP techniques, this project streamlines legal workflows and enhances access to legal information.

## Features
- Natural language legal query handling
- FIR (First Information Report) management and database integration
- IPC (Indian Penal Code) section search and analysis
- Web-based chat interface
- Integration with Rasa NLU for intent classification and entity extraction
- Automated legal data scraping and database population
- Modular, extensible codebase

## Tech Stack
- Python 3.8+
- Rasa 3.6.2
- FastAPI
- MySQL
- Selenium (for scraping)
- Jinja2 (templating)
- Websockets, Socket.IO

## Directory Structure
```
chat/
├── actions/                # Custom Rasa actions
├── data/                   # Rasa NLU, stories, rules
├── models/                 # Trained Rasa models
├── rasa/                   # Rasa project files
├── rasa_data/              # Additional Rasa data
├── static/                 # Frontend static files (HTML, SVG, etc.)
├── tests/                  # Test cases and test data
├── results/                # Output and result files
├── *.py                    # Core backend scripts (API, DB, scraping, etc.)
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── LICENSE                 # MIT License
```

## Setup & Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Babureddy009/Legal-AI-Assistant-For-Law-Enforcement.git
   cd Legal-AI-Assistant-For-Law-Enforcement/chat
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Unix/Mac:
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment variables:**
   - Copy `.env.example` to `.env` and update as needed (if applicable).
5. **Set up the database:**
   - Run the provided SQL scripts in your MySQL instance.
   - Update connection details in config files if needed.
6. **Train the Rasa model:**
   ```bash
   rasa train
   ```
7. **Run the backend services:**
   - Start Rasa server:
     ```bash
     rasa run --enable-api
     ```
   - Start FastAPI server:
     ```bash
     uvicorn chat:app --reload
     ```

## Usage
- Access the web chat interface via your browser (see static/about.html or main app entrypoint).
- Use the API endpoints for programmatic access (see api_client.py and FastAPI docs).
- Refer to the data/ and rasa_data/ folders for NLU and story customization.

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## License
MIT License. See [LICENSE](LICENSE) for details.

---
*Developed by Babureddy B N, 2025* 