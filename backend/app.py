#!/usr/bin/env python3
"""
ThreatLens Backend Server
Real-time penetration testing tool integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import uuid
import time
import threading
import os
from datetime import datetime
import re
import shutil
from urllib.parse import urlparse, urljoin

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Store scan results in memory (in production, use a database)
scans = {}
scan_status = {}

def sanitize_target(target):
    """Validate and sanitize target input using whitelist approach"""
    target = target.strip()
    
    # Whitelist approach: Only allow valid URLs and IP addresses
    # URL pattern (http/https with domain)
    url_pattern = r'^https?://[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*(/.*)?$'
    # IP address pattern
    ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    # Domain pattern (without http/https)
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    
    if re.match(url_pattern, target) or re.match(ip_pattern, target) or re.match(domain_pattern, target):
        # Additional validation for IP addresses
        if re.match(ip_pattern, target):
            octets = target.split('.')
            if any(int(octet) > 255 for octet in octets):
                raise ValueError("Invalid IP address: octets must be 0-255")
        return target
    else:
        raise ValueError("Invalid target format: must be a valid URL, domain, or IP address")

def normalize_target(target):
    """Return normalized URL and host from a validated target"""
    sanitized_target = sanitize_target(target)
    normalized_url = sanitized_target if sanitized_target.startswith(('http://', 'https://')) else f'http://{sanitized_target}'
    parsed = urlparse(normalized_url)
    host = parsed.hostname or sanitized_target
    return normalized_url, host

def run_nmap_scan(target, scan_id):
    """Execute Nmap port scan"""
    try:
        target = sanitize_target(target)
        scan_status[scan_id]['current_module'] = 'Port Scanning (Nmap)'
        scan_status[scan_id]['progress'] = 20
        
        # Double-check target doesn't contain shell metacharacters before passing to subprocess
        if any(char in target for char in ['&', '|', ';', '`', '$', '(', ')', '<', '>', '\n', '\r']):
            return [], "Target validation failed: contains invalid characters"
        
        # Run basic nmap scan with explicit argument list (no shell interpretation)
        cmd = ['nmap', '-sV', '-T4', '--top-ports', '1000', target]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        # Parse nmap output
        vulnerabilities = []
        if 'open' in result.stdout.lower():
            lines = result.stdout.split('\n')
            for line in lines:
                if 'open' in line.lower():
                    vulnerabilities.append({
                        'name': f'Open Port Detected: {line.strip()}',
                        'risk': 'Medium',
                        'recommendation': 'Review if this port should be exposed and ensure the service is properly secured.'
                    })
        
        return vulnerabilities, result.stdout
    except subprocess.TimeoutExpired:
        return [], "Scan timeout exceeded"
    except Exception as e:
        return [], f"Error: {str(e)}"

def run_nikto_scan(target, scan_id):
    """Execute Nikto vulnerability scan"""
    try:
        target = sanitize_target(target)
        scan_status[scan_id]['current_module'] = 'Vulnerability Scan (Nikto)'
        scan_status[scan_id]['progress'] = 40
        
        # Check if nikto is available
        if subprocess.run(['which', 'nikto'], capture_output=True).returncode != 0:
            return [], "Nikto not installed"
        
        # Run nikto scan
        cmd = ['nikto', '-h', target, '-Tuning', '1,2,3', '-maxtime', '180']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=200)
        
        vulnerabilities = []
        lines = result.stdout.split('\n')
        for line in lines:
            if '+' in line and any(keyword in line.lower() for keyword in ['osvdb', 'cve', 'vulnerability', 'risk']):
                vulnerabilities.append({
                    'name': f'Nikto Finding: {line.strip()}',
                    'risk': 'High' if 'high' in line.lower() else 'Medium',
                    'recommendation': 'Review and patch identified vulnerabilities.'
                })
        
        return vulnerabilities, result.stdout
    except subprocess.TimeoutExpired:
        return [], "Scan timeout exceeded"
    except Exception as e:
        return [], f"Nikto not available: {str(e)}"

def run_sql_injection_test(target, scan_id):
    """Execute basic SQL injection tests"""
    try:
        target_url, _ = normalize_target(target)
        scan_status[scan_id]['current_module'] = 'SQL Injection Testing'
        scan_status[scan_id]['progress'] = 60
        
        vulnerabilities = []
        if not shutil.which('sqlmap'):
            return [], "SQLMap not installed (install with: sudo apt-get install -y sqlmap)"

        cmd = [
            'sqlmap',
            '-u', target_url,
            '--batch',
            '--crawl=1',
            '--level=1',
            '--risk=1',
            '--smart',
            '--random-agent',
            '--timeout=15',
            '--retries=1'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
        output = f"{result.stdout}\n{result.stderr}"
        output_lower = output.lower()

        if any(keyword in output_lower for keyword in ['is vulnerable', 'sql injection vulnerability', 'injectable']):
            vulnerabilities.append({
                'name': 'Potential SQL Injection Vulnerability Detected',
                'risk': 'High',
                'recommendation': 'Review injectable parameters, apply parameterized queries, and add strict server-side input validation.'
            })

        return vulnerabilities, output if output.strip() else "SQLMap completed with no output"
    except Exception as e:
        return [], f"Error: {str(e)}"

def run_xss_detection(target, scan_id):
    """Execute XSS detection"""
    try:
        target_url, _ = normalize_target(target)
        scan_status[scan_id]['current_module'] = 'XSS Detection'
        scan_status[scan_id]['progress'] = 70
        
        import requests

        vulnerabilities = []
        logs = []

        reflection_payload = "threatlens_xss_probe_12345"
        for param in ['q', 'search', 'query', 'id', 'page']:
            try:
                response = requests.get(target_url, params={param: reflection_payload}, timeout=10)
                logs.append(f"Checked reflected payload in param '{param}' (status {response.status_code})")
                if reflection_payload in response.text:
                    vulnerabilities.append({
                        'name': f'Potential Reflected XSS via parameter: {param}',
                        'risk': 'High',
                        'recommendation': 'Encode untrusted output, validate input, and deploy context-aware escaping in templates.'
                    })
                    break
            except requests.RequestException as req_error:
                logs.append(f"XSS check failed for param '{param}': {str(req_error)}")

        try:
            baseline_response = requests.get(target_url, timeout=10)
            csp = baseline_response.headers.get('Content-Security-Policy')
            xcto = baseline_response.headers.get('X-Content-Type-Options')
            if not csp:
                vulnerabilities.append({
                    'name': 'Missing Content-Security-Policy Header',
                    'risk': 'Medium',
                    'recommendation': 'Configure a restrictive Content-Security-Policy to reduce XSS exploitation impact.'
                })
            if not xcto:
                vulnerabilities.append({
                    'name': 'Missing X-Content-Type-Options Header',
                    'risk': 'Low',
                    'recommendation': 'Set X-Content-Type-Options: nosniff to mitigate MIME-type confusion issues.'
                })
        except requests.RequestException as req_error:
            logs.append(f"Baseline header analysis failed: {str(req_error)}")

        return vulnerabilities, '\n'.join(logs) if logs else "XSS detection completed"
    except Exception as e:
        return [], f"Error: {str(e)}"

def run_directory_fuzzing(target, scan_id):
    """Execute directory fuzzing"""
    try:
        target_url, _ = normalize_target(target)
        scan_status[scan_id]['current_module'] = 'Directory Fuzzing'
        scan_status[scan_id]['progress'] = 80
        
        import requests

        vulnerabilities = []
        logs = []
        common_paths = [
            'admin', 'login', 'dashboard', 'api', 'backup', 'backup.zip',
            '.env', '.git/config', 'robots.txt', 'sitemap.xml', 'config.php'
        ]

        for path in common_paths:
            url = urljoin(target_url.rstrip('/') + '/', path)
            try:
                response = requests.get(url, timeout=6, allow_redirects=False)
                if response.status_code in [200, 301, 302, 401, 403]:
                    risk = 'Medium' if path in ['.env', '.git/config', 'backup', 'backup.zip', 'config.php'] else 'Low'
                    vulnerabilities.append({
                        'name': f'Exposed Resource Found: /{path} (HTTP {response.status_code})',
                        'risk': risk,
                        'recommendation': 'Restrict access to sensitive resources and disable public exposure of administrative or backup endpoints.'
                    })
                logs.append(f"/{path} -> HTTP {response.status_code}")
            except requests.RequestException as req_error:
                logs.append(f"/{path} -> request failed: {str(req_error)}")

        return vulnerabilities, '\n'.join(logs) if logs else "Directory fuzzing completed"
    except Exception as e:
        return [], f"Error: {str(e)}"

def run_tech_stack_analysis(target, scan_id):
    """Analyze technology stack"""
    try:
        target_url, _ = normalize_target(target)
        scan_status[scan_id]['current_module'] = 'Tech Stack Analysis'
        scan_status[scan_id]['progress'] = 90
        
        vulnerabilities = []
        # Basic header analysis
        import requests
        try:
            response = requests.get(target_url, timeout=10)
            headers = response.headers
            
            tech_found = []
            if 'Server' in headers:
                tech_found.append(f"Server: {headers['Server']}")
            if 'X-Powered-By' in headers:
                tech_found.append(f"Powered by: {headers['X-Powered-By']}")
            
            if tech_found:
                vulnerabilities.append({
                    'name': f'Technology Stack Identified: {", ".join(tech_found)}',
                    'risk': 'Low',
                    'recommendation': 'Consider hiding server version information to reduce attack surface.'
                })
        except requests.RequestException as e:
            # Specific exception for network/request errors
            return [], f"Request error: {str(e)}"
        
        return vulnerabilities, "Tech stack analysis completed"
    except Exception as e:
        return [], f"Error: {str(e)}"

def execute_scan(scan_id, target, modules, options):
    """Execute scan modules in background thread"""
    try:
        scan_status[scan_id] = {
            'status': 'running',
            'progress': 0,
            'current_module': 'Initializing...',
            'start_time': datetime.now().isoformat()
        }
        
        all_vulnerabilities = []
        all_logs = []
        
        # Execute requested modules
        if 'port_scan' in modules or 'full_scan' in modules:
            vulns, log = run_nmap_scan(target, scan_id)
            all_vulnerabilities.extend(vulns)
            all_logs.append(f"\n=== Port Scanning (Nmap) ===\n{log}")
        
        if 'vuln_scan' in modules or 'full_scan' in modules:
            vulns, log = run_nikto_scan(target, scan_id)
            all_vulnerabilities.extend(vulns)
            all_logs.append(f"\n=== Vulnerability Scan (Nikto) ===\n{log}")
        
        if 'sql_injection' in modules or 'full_scan' in modules:
            vulns, log = run_sql_injection_test(target, scan_id)
            all_vulnerabilities.extend(vulns)
            all_logs.append(f"\n=== SQL Injection Testing ===\n{log}")
        
        if 'xss_detection' in modules or 'full_scan' in modules:
            vulns, log = run_xss_detection(target, scan_id)
            all_vulnerabilities.extend(vulns)
            all_logs.append(f"\n=== XSS Detection ===\n{log}")
        
        if 'dir_fuzz' in modules or 'full_scan' in modules:
            vulns, log = run_directory_fuzzing(target, scan_id)
            all_vulnerabilities.extend(vulns)
            all_logs.append(f"\n=== Directory Fuzzing ===\n{log}")
        
        if 'tech_stack' in modules or 'full_scan' in modules:
            vulns, log = run_tech_stack_analysis(target, scan_id)
            all_vulnerabilities.extend(vulns)
            all_logs.append(f"\n=== Tech Stack Analysis ===\n{log}")
        
        # Mark as completed
        scan_status[scan_id]['status'] = 'completed'
        scan_status[scan_id]['progress'] = 100
        scan_status[scan_id]['current_module'] = 'Scan Complete'
        scan_status[scan_id]['end_time'] = datetime.now().isoformat()
        
        # Store results
        scans[scan_id]['results'] = all_vulnerabilities
        scans[scan_id]['logs'] = '\n'.join(all_logs)
        scans[scan_id]['status'] = 'completed'
        
    except Exception as e:
        scan_status[scan_id]['status'] = 'failed'
        scan_status[scan_id]['error'] = str(e)
        scans[scan_id]['status'] = 'failed'
        scans[scan_id]['error'] = str(e)

@app.route('/api/scan/start', methods=['POST'])
def start_scan():
    """Start a new security scan"""
    try:
        data = request.get_json()
        target = data.get('target')
        modules = data.get('modules', [])
        options = data.get('options', {})
        
        if not target:
            return jsonify({'error': 'Target is required'}), 400
        
        # Validate target
        target = sanitize_target(target)
        
        # Generate scan ID
        scan_id = str(uuid.uuid4())[:8]
        
        # Store scan info
        scans[scan_id] = {
            'id': scan_id,
            'target': target,
            'modules': modules,
            'options': options,
            'status': 'queued',
            'created_at': datetime.now().isoformat()
        }
        
        # Start scan in background thread
        thread = threading.Thread(target=execute_scan, args=(scan_id, target, modules, options))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'scanId': scan_id,
            'status': 'queued',
            'message': 'Scan initiated successfully'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to start scan: {str(e)}'}), 500

@app.route('/api/scan/status/<scan_id>', methods=['GET'])
def get_scan_status(scan_id):
    """Get scan status and progress"""
    if scan_id not in scan_status:
        return jsonify({'error': 'Scan not found'}), 404
    
    status_data = scan_status[scan_id].copy()
    if scan_id in scans:
        status_data['target'] = scans[scan_id]['target']
    
    return jsonify(status_data)

@app.route('/api/scan/results/<scan_id>', methods=['GET'])
def get_scan_results(scan_id):
    """Get scan results"""
    if scan_id not in scans:
        return jsonify({'error': 'Scan not found'}), 404
    
    scan_data = scans[scan_id].copy()
    if scan_id in scan_status:
        scan_data['progress'] = scan_status[scan_id].get('progress', 0)
        scan_data['current_module'] = scan_status[scan_id].get('current_module', '')
    
    return jsonify(scan_data)

@app.route('/api/scans', methods=['GET'])
def list_scans():
    """List all scans"""
    scan_list = []
    for scan_id, scan in scans.items():
        scan_info = {
            'id': scan_id,
            'target': scan['target'],
            'status': scan['status'],
            'created_at': scan['created_at']
        }
        if scan_id in scan_status:
            scan_info['progress'] = scan_status[scan_id].get('progress', 0)
        scan_list.append(scan_info)
    
    return jsonify(scan_list)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'tools_available': {
            'nmap': subprocess.run(['which', 'nmap'], capture_output=True).returncode == 0,
            'nikto': subprocess.run(['which', 'nikto'], capture_output=True).returncode == 0,
            'sqlmap': subprocess.run(['which', 'sqlmap'], capture_output=True).returncode == 0,
            'python': True
        }
    })

if __name__ == '__main__':
    import os
    print("🚀 ThreatLens Backend Server Starting...")
    print("⚠️  WARNING: Only use on systems you have permission to test!")
    print("📡 Server will run on http://localhost:5000")
    
    # Use environment variable for debug mode (default: False for security)
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    if debug_mode:
        print("⚠️  DEBUG MODE ENABLED - DO NOT USE IN PRODUCTION!")
    
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
