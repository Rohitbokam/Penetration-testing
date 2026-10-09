# Quick Start Guide - ThreatLens

This guide will help you get started with ThreatLens in minutes.

## Prerequisites Check

Before you begin, ensure you have:
- Linux/Unix system (Ubuntu 20.04+ recommended)
- Python 3.8 or higher
- 2GB RAM minimum

## Installation Steps

### Option 1: Automated Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/Rohitbokam/Penetration-testing.git
cd Penetration-testing

# Run the installer
chmod +x install.sh
./install.sh
```

The installer will:
1. Install Nmap and Nikto
2. Set up Python environment
3. Install all dependencies
4. Create start/stop scripts

### Option 2: Manual Installation

See [README.md](README.md) for detailed manual installation instructions.

## Starting the Platform

### Option A: Start Everything at Once

```bash
./start-all.sh
```

This starts both backend and frontend servers.

### Option B: Start Separately (Recommended for Development)

**Terminal 1 - Backend:**
```bash
./start-backend.sh
```

**Terminal 2 - Frontend:**
```bash
./start-frontend.sh
```

## Accessing the Platform

Open your web browser and navigate to:
```
http://localhost:8080/tool.html
```

## Running Your First Scan

1. **Click "Get Started"** on the landing page
2. **Click "New Scan"** from the dashboard
3. **Enter a target:**
   - URL: `https://example.com`
   - IP: `192.168.1.1`
4. **Select scan modules:**
   - Port Scanning (Nmap)
   - Vulnerability Scan (Nikto)
   - SQL Injection Testing
   - XSS Detection
   - Tech Stack Analysis
5. **Configure options:**
   - Quick Scan: 5-10 minutes
   - Standard Scan: 15-30 minutes
   - Deep Scan: 30+ minutes
6. **Click "Start Scan"**

## Viewing Results

After the scan completes:

1. Navigate to **Reports** section
2. View vulnerability details
3. See risk distribution
4. Download report as text file

## Testing the Backend API

You can test the backend directly:

```bash
# Health check
curl http://localhost:5000/api/health

# Start a scan
curl -X POST http://localhost:5000/api/scan/start \
  -H "Content-Type: application/json" \
  -d '{"target": "example.com", "modules": ["tech_stack", "sql_injection"]}'

# Check scan status (replace SCAN_ID with actual ID)
curl http://localhost:5000/api/scan/status/SCAN_ID

# Get scan results
curl http://localhost:5000/api/scan/results/SCAN_ID
```

## Available Scan Modules

| Module | Description | Tool Used |
|--------|-------------|-----------|
| Port Scanning | Detects open ports and services | Nmap |
| Vulnerability Scan | Finds common vulnerabilities | Nikto |
| SQL Injection | Tests for SQL injection flaws | Custom |
| XSS Detection | Identifies XSS vulnerabilities | Custom |
| Directory Fuzzing | Discovers hidden resources | Custom |
| Tech Stack Analysis | Fingerprints technologies | HTTP Headers |

## Stopping the Platform

```bash
./stop-all.sh
```

Or press `Ctrl+C` in each terminal window.

## Troubleshooting

### Backend won't start

```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill process if needed
kill -9 <PID>

# Restart backend
./start-backend.sh
```

### Frontend won't start

```bash
# Check if port 8080 is in use
lsof -i :8080

# Kill process if needed
kill -9 <PID>

# Restart frontend
./start-frontend.sh
```

### Tools not found

```bash
# Verify installations
which nmap
which nikto

# Reinstall if needed
sudo apt-get install -y nmap nikto
```

### Permission errors

Some scans may require elevated privileges:

```bash
# Run backend with sudo (use cautiously)
sudo ./start-backend.sh
```

## Security Best Practices

⚠️ **CRITICAL REMINDERS:**

1. **Authorization Required**: Only scan systems you own or have written permission to test
2. **Legal Compliance**: Unauthorized scanning is illegal in most jurisdictions
3. **Ethical Use**: Follow responsible disclosure practices
4. **Network Safety**: Be cautious on production networks
5. **Rate Limiting**: Don't overwhelm target systems

## Next Steps

- Review the [README.md](README.md) for detailed documentation
- Check [backend/README.md](backend/README.md) for API documentation
- Explore advanced configuration options
- Set up scheduled scans (coming soon)

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/Rohitbokam/Penetration-testing/issues)
- **Documentation**: [README.md](README.md)
- **API Docs**: [backend/README.md](backend/README.md)

## Example Use Cases

### Scenario 1: Quick Web App Scan
```bash
# Target: Your web application
# Modules: Vulnerability Scan, SQL Injection, XSS
# Duration: ~10 minutes
```

### Scenario 2: Complete Infrastructure Assessment
```bash
# Target: Your server
# Modules: Full Assessment (all modules)
# Duration: ~30+ minutes
```

### Scenario 3: Technology Stack Discovery
```bash
# Target: Any website
# Modules: Tech Stack Analysis
# Duration: ~1 minute
```

---

**Happy Testing! Stay Ethical! 🔒**
