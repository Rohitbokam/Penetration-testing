# ThreatLens - Real-Time Penetration Testing Platform

A fully functional web-based penetration testing platform with real-time integration of professional security tools.

![Landing Page](https://github.com/user-attachments/assets/9705d1c2-ec01-4930-92a5-ca93471b43b4)
![Dashboard](https://github.com/user-attachments/assets/306fdb39-35b3-4658-9897-54ce8ffe1a93)

## 🚀 Features

### Real-Time Tool Integration
- **Nmap** - Port scanning and service detection
- **Nikto** - Web vulnerability scanning
- **SQL Injection Testing** - Database security analysis
- **XSS Detection** - Cross-site scripting vulnerability identification
- **Directory Fuzzing** - Hidden resource discovery
- **Tech Stack Analysis** - Technology fingerprinting

### Platform Features
- Live scan progress tracking with real-time updates
- Comprehensive vulnerability reporting
- Downloadable security reports
- Dashboard with scan history and statistics
- Multi-language support (EN/ES)
- Dark theme cyberpunk UI

## ⚠️ Security Warning

**IMPORTANT**: This tool is designed for **authorized security testing only**.

- ✅ Only scan systems you own or have explicit written permission to test
- ❌ Unauthorized scanning may be illegal in your jurisdiction
- 📝 Always obtain proper authorization before conducting security assessments
- 🎓 This tool is for educational and professional security testing purposes only

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux/Unix (Ubuntu 20.04+ recommended)
- **Python**: 3.8 or higher
- **Node.js**: 14+ (for development)
- **RAM**: 2GB minimum, 4GB recommended
- **Disk Space**: 1GB for tools and dependencies

### Required Tools
- Nmap
- Nikto
- Python 3
- pip (Python package manager)

## 🛠️ Installation

### Quick Start (Ubuntu/Debian)

```bash
# Clone the repository
git clone https://github.com/Rohitbokam/Penetration-testing.git
cd Penetration-testing

# Run the installation script
chmod +x install.sh
./install.sh
```

### Manual Installation

#### 1. Install System Tools

```bash
# Update package lists
sudo apt-get update

# Install Nmap
sudo apt-get install -y nmap

# Install Nikto
sudo apt-get install -y nikto

# Install Python and pip
sudo apt-get install -y python3 python3-pip python3-venv
```

#### 2. Set Up Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

#### 3. Start the Backend Server

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run the server
python app.py
```

The backend server will start on `http://localhost:5000`

#### 4. Start the Frontend

Open a new terminal window:

```bash
# Navigate to project root
cd /path/to/Penetration-testing

# Start a simple HTTP server
python3 -m http.server 8080
```

Access the application at `http://localhost:8080/tool.html`

## 🖥️ Usage

### Starting a Scan

1. **Navigate** to the application in your web browser
2. **Click** "Get Started" on the landing page
3. **Click** "New Scan" from the dashboard
4. **Enter** the target URL or IP address
5. **Select** the scan modules you want to run:
   - Port Scanning (Nmap)
   - Vulnerability Scan (Nikto)
   - SQL Injection Testing
   - XSS Detection
   - Directory Fuzzing
   - Tech Stack Analysis
   - Full Assessment (all modules)
6. **Configure** scan options (depth, stealth mode)
7. **Click** "Start Scan"

### Viewing Results

1. Monitor the scan progress in real-time
2. View live terminal output
3. Once complete, navigate to the "Reports" section
4. View detailed vulnerability findings
5. Download the scan report

## 📖 API Documentation

### Backend API Endpoints

#### Health Check
```http
GET /api/health
```
Returns server health status and available tools.

#### Start Scan
```http
POST /api/scan/start
Content-Type: application/json

{
  "target": "example.com",
  "modules": ["port_scan", "vuln_scan"],
  "options": {
    "scanDepth": "quick",
    "stealth": false
  }
}
```

#### Get Scan Status
```http
GET /api/scan/status/{scan_id}
```

#### Get Scan Results
```http
GET /api/scan/results/{scan_id}
```

#### List All Scans
```http
GET /api/scans
```

### Available Scan Modules

- `port_scan` - Nmap port scanning
- `vuln_scan` - Nikto vulnerability scanning
- `sql_injection` - SQL injection testing
- `xss_detection` - Cross-site scripting detection
- `dir_fuzz` - Directory fuzzing
- `tech_stack` - Technology stack analysis
- `full_scan` - Runs all available modules

## 🔧 Configuration

### Backend Configuration

Edit `backend/app.py` to configure:

- **Port**: Change the port number (default: 5000)
- **CORS**: Configure allowed origins for production
- **Timeouts**: Adjust tool timeout values
- **Storage**: Switch from in-memory to database storage

### Frontend Configuration

Edit `tool.html` to configure:

- **Backend URL**: Update API endpoint URLs (search for `localhost:5000`)
- **Theme**: Customize CSS variables in the `:root` section
- **Features**: Enable/disable specific modules

## 🚀 Production Deployment

### Using Gunicorn (Recommended)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

### Using Docker (Coming Soon)

```bash
# Build the image
docker build -t threatlens .

# Run the container
docker run -p 5000:5000 -p 8080:8080 threatlens
```

### Security Considerations for Production

1. **Authentication**: Implement user authentication and authorization
2. **HTTPS**: Use SSL/TLS certificates
3. **Rate Limiting**: Prevent abuse with rate limiting
4. **Input Validation**: Additional validation and sanitization
5. **Database**: Use proper database (PostgreSQL, MongoDB)
6. **Logging**: Implement comprehensive logging
7. **Monitoring**: Set up monitoring and alerting
8. **Reverse Proxy**: Run behind Nginx or Apache

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Nmap Project** - Network scanning tool
- **Nikto** - Web server scanner
- **Bootstrap** - Frontend framework
- **Flask** - Python web framework

## 📞 Support

For issues, questions, or suggestions:

- **GitHub Issues**: [Create an issue](https://github.com/Rohitbokam/Penetration-testing/issues)
- **Email**: Contact the maintainer

## ⚖️ Legal Disclaimer

This tool is provided "as is" without warranty of any kind. The authors and contributors are not responsible for any misuse or damage caused by this tool. Users are solely responsible for ensuring they have proper authorization before conducting any security assessments.

Always comply with:
- Local and international laws
- Terms of Service of tested systems
- Ethical hacking guidelines
- Professional security standards

## 🔮 Future Enhancements

- [ ] WebSocket support for real-time streaming
- [ ] Additional tool integrations (Metasploit, Burp Suite, etc.)
- [ ] Advanced reporting with PDF generation
- [ ] Scheduled scans with cron-like functionality
- [ ] Email notifications
- [ ] User authentication and multi-tenancy
- [ ] Historical scan comparison
- [ ] REST API for programmatic access
- [ ] Docker containerization
- [ ] Cloud deployment guides (AWS, Azure, GCP)

---

**Made with ❤️ for the security community**
