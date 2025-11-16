# Upwork Job Evaluation & Zoho CRM Integration

An automated system that evaluates Upwork job postings against your criteria and integrates suitable opportunities into Zoho CRM, with machine learning to improve matching over time.

## 🎯 Project Overview

This project automates the freelance business development workflow by:
- **Scraping** Upwork job feeds using browser automation
- **Evaluating** jobs against your personalized criteria
- **Storing** opportunities in Zoho CRM
- **Learning** from your feedback to improve matching accuracy
- **Preventing** duplicate reviews using unique job identifiers

## 🏗️ Architecture

```
┌─────────────────┐
│  Claude Desktop │
│    (Interface)  │
└────────┬────────┘
         │
         ├─── MCP Protocol ───┐
         │                    │
    ┌────▼────────┐    ┌─────▼─────────┐
    │   Upwork    │    │     Zoho      │
    │ MCP Server  │    │  MCP Server   │
    └────┬────────┘    └─────┬─────────┘
         │                   │
    ┌────▼────────┐    ┌─────▼─────────┐
    │  Playwright │    │   Zoho REST   │
    │   Browser   │    │      API      │
    └────┬────────┘    └─────┬─────────┘
         │                   │
    ┌────▼────────┐    ┌─────▼─────────┐
    │   Upwork    │    │  Zoho CRM     │
    │   Website   │    │   (Storage)   │
    └─────────────┘    └───────────────┘
```

### Technology Stack

- **Language:** Python 3.8+
- **MCP Framework:** Anthropic MCP SDK
- **Browser Automation:** Playwright
- **CRM Integration:** Zoho REST API
- **Machine Learning:** scikit-learn (future phase)
- **Environment:** Windows 11

## 📁 Project Structure

```
upwork-zoho-automation/
├── README.md                          # This file
├── docs/
│   ├── conversation-01-hello-world.md # Initial setup guide
│   ├── conversation-02-upwork-scraper.md
│   ├── conversation-03-zoho-integration.md
│   └── conversation-04-evaluation-logic.md
├── mcp-servers/
│   ├── hello-world/                   # Test MCP server
│   │   └── server.py
│   ├── upwork-scraper/                # Upwork job scraper
│   │   ├── server.py
│   │   ├── .env                       # Credentials (not in git)
│   │   └── requirements.txt
│   └── zoho-integration/              # Zoho CRM connector
│       ├── server.py
│       ├── .env                       # API tokens (not in git)
│       └── requirements.txt
└── .gitignore

```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Windows 11 (or adjust paths for macOS/Linux)
- Claude Desktop (latest version)
- Active Upwork account
- Zoho CRM account with API access

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd upwork-zoho-automation
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   # For Upwork scraper
   cd mcp-servers/upwork-scraper
   pip install -r requirements.txt
   playwright install chromium
   
   # For Zoho integration
   cd ../zoho-integration
   pip install -r requirements.txt
   ```

4. **Configure credentials:**
   
   Create `.env` files in each MCP server directory:
   
   **upwork-scraper/.env:**
   ```
   UPWORK_USERNAME=your_email@example.com
   UPWORK_PASSWORD=your_password
   ```
   
   **zoho-integration/.env:**
   ```
   ZOHO_CLIENT_ID=your_client_id
   ZOHO_CLIENT_SECRET=your_client_secret
   ZOHO_REFRESH_TOKEN=your_refresh_token
   ZOHO_ORG_ID=your_org_id
   ```

5. **Configure Claude Desktop:**
   
   Edit `%APPDATA%\Claude\claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "upwork-scraper": {
         "command": "python",
         "args": ["C:\\full\\path\\to\\mcp-servers\\upwork-scraper\\server.py"]
       },
       "zoho-crm": {
         "command": "python",
         "args": ["C:\\full\\path\\to\\mcp-servers\\zoho-integration\\server.py"]
       }
     }
   }
   ```

6. **Restart Claude Desktop**

## 💡 Usage

Once configured, interact with Claude Desktop using natural language:

```
"Fetch my latest Upwork jobs"
"Show me jobs matching my criteria"
"Add this job to Zoho CRM"
"Has this job already been reviewed?"
"What jobs need my attention today?"
```

## 🔧 Development Roadmap

### ✅ Phase 1: Foundation (Conversation 1)
- MCP protocol understanding
- Hello-world MCP server
- Claude Desktop integration
- Environment setup

### 🔄 Phase 2: Upwork Integration (Conversation 2)
- Browser automation setup
- Upwork login automation
- Job feed scraping
- Data extraction and parsing

### 📋 Phase 3: Zoho CRM Integration (Conversation 3)
- Zoho API authentication
- CRUD operations for job records
- Duplicate detection by job ID
- Custom field mapping

### 🎯 Phase 4: Evaluation Logic (Conversation 4)
- Criteria definition
- Job scoring algorithm
- Match threshold configuration
- Automated filtering

### 🤖 Phase 5: Machine Learning (Conversation 5)
- Feedback collection system
- Preference learning model
- Continuous improvement loop
- Model retraining workflow

### 🚀 Phase 6: Automation & Scheduling (Conversation 6)
- Periodic job checking
- Automated evaluation pipeline
- Notification system
- Error handling and logging

### 🔍 Phase 7: Reporting & Optimization (Conversation 7)
- Analytics dashboard
- Performance metrics
- Optimization recommendations
- Documentation and deployment

## 🔒 Security Considerations

- **Never commit `.env` files** - Add to `.gitignore`
- **Use environment variables** for all credentials
- **Rotate API tokens** regularly
- **Review browser automation** for Upwork ToS compliance
- **Secure Zoho API access** with appropriate scopes
- **Implement rate limiting** to avoid API throttling

## 🐛 Troubleshooting

### MCP Server Not Appearing in Claude Desktop
1. Check config file JSON syntax
2. Verify full absolute paths
3. Restart Claude Desktop completely
4. Check server logs

### Upwork Login Fails
1. Verify credentials in `.env`
2. Check for 2FA requirements
3. Update selectors if Upwork UI changed
4. Use `headless=False` for debugging

### Zoho API Errors
1. Verify API token validity
2. Check API scope permissions
3. Confirm organization ID
4. Review rate limits

## 📚 Documentation

Detailed step-by-step guides for each phase:
- [Conversation 1: Hello World & Setup](docs/conversation-01-hello-world.md)
- [Conversation 2: Upwork Scraper](docs/conversation-02-upwork-scraper.md)
- [Conversation 3: Zoho Integration](docs/conversation-03-zoho-integration.md)
- [Conversation 4: Evaluation Logic](docs/conversation-04-evaluation-logic.md)

## 🤝 Contributing

This is a personal project, but feel free to fork and adapt for your own use case.

## 📝 License

[Your chosen license]

## 🙏 Acknowledgments

- Anthropic MCP SDK
- Playwright browser automation
- Zoho CRM API
- Claude Desktop integration

## 📧 Contact

[Your contact information]

---

**Note:** This project is for personal automation and learning purposes. Please review Upwork's Terms of Service regarding automated access to their platform.
