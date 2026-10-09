# ThreatLens Backend Server

## Overview
This is the backend server for ThreatLens that executes real penetration testing tools.

## Prerequisites

### System Requirements
- Python 3.8 or higher (tested with Python 3.8-3.11)
- Linux/Unix system (recommended)
- Sudo/root access for installing penetration testing tools

### Required Penetration Testing Tools
Install the following tools on your system:

```bash
# Update system
sudo apt-get update

# Install Nmap (Port Scanner)
sudo apt-get install -y nmap

# Install Nikto (Web Vulnerability Scanner)
sudo apt-get install -y nikto

# Optional: Install additional tools
sudo apt-get install -y gobuster sqlmap
```

## Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

1. Activate the virtual environment (if not already activated):
```bash
source venv/bin/activate
```

2. Start the server:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check
```
GET /api/health
```
Returns server health status and available tools.

### Start Scan
```
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

### Get Scan Status
```
GET /api/scan/status/{scan_id}
```

### Get Scan Results
```
GET /api/scan/results/{scan_id}
```

### List All Scans
```
GET /api/scans
```

## Available Scan Modules

- `port_scan` - Nmap port scanning
- `vuln_scan` - Nikto vulnerability scanning
- `sql_injection` - SQL injection testing
- `xss_detection` - Cross-site scripting detection
- `dir_fuzz` - Directory fuzzing
- `tech_stack` - Technology stack analysis
- `full_scan` - Runs all modules

## Security Notice

⚠️ **WARNING**: This tool is for authorized penetration testing only!

- Only scan systems you have explicit permission to test
- Unauthorized scanning may be illegal in your jurisdiction
- Use responsibly and ethically
- This tool is for educational and authorized security testing purposes only

## Configuration

### CORS Settings
The server allows CORS from all origins by default for development. For production, configure CORS properly in `app.py`:

```python
CORS(app, resources={r"/api/*": {"origins": "https://yourdomain.com"}})
```

### Scan Timeouts
Tool timeouts can be adjusted in each `run_*_scan()` function.

## Troubleshooting

### Tools Not Found
If tools are not detected, ensure they are installed and in your system PATH:
```bash
which nmap
which nikto
```

### Permission Errors
Some scans may require elevated privileges:
```bash
sudo python app.py  # Use with caution
```

### Port Already in Use
If port 5000 is already in use, modify the port in `app.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

## Development

### Adding New Scan Modules

1. Create a new function:
```python
def run_custom_scan(target, scan_id):
    scan_status[scan_id]['current_module'] = 'Custom Scan'
    # Your scan logic here
    return vulnerabilities, log_output
```

2. Add to `execute_scan()`:
```python
if 'custom_scan' in modules:
    vulns, log = run_custom_scan(target, scan_id)
    all_vulnerabilities.extend(vulns)
    all_logs.append(f"\n=== Custom Scan ===\n{log}")
```

## Production Deployment

For production deployment:

1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set up proper database (PostgreSQL, MongoDB)
3. Implement authentication and authorization
4. Use environment variables for configuration
5. Set up proper logging
6. Implement rate limiting
7. Use HTTPS/TLS
8. Run behind a reverse proxy (Nginx, Apache)

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## License
This tool is for educational purposes only. Use responsibly and legally.
