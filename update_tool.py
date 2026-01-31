import os

with open('tool.html', 'r') as f:
    lines = f.readlines()

new_populate_report = """    // 3) Modified populateReportSection to always render dynamic content
    function populateReportSection() {
        const reportHeader = document.getElementById('current-scan-report');

        // Get scan data
        const scanData = JSON.parse(localStorage.getItem('threatlens_currentViewScan') || localStorage.getItem('threatlens_currentScan') || 'null');

        if (!scanData) {
            reportHeader.innerHTML = '<div class="text-center p-4">No report data available</div>';
            return;
        }

        // clear old header and inject fresh dynamic data only
        reportHeader.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4">
              <div>
                <h4>${scanData.target}</h4>
                <p class="text-muted mb-0">Status: ${scanData.status}</p>
              </div>
              <div>
                <span class="badge bg-primary p-2">Scan Date: ${new Date(scanData.date).toLocaleDateString()}</span>
                <span class="badge ${scanData.status==='completed'?'bg-success':'bg-warning'} p-2 ms-2">${scanData.status}</span>
              </div>
            </div>`;

        // Use results from scanData
        const vulnerabilities = scanData.results || [];

        const vulnContainer = document.getElementById('vulnerability-container');
        const summaryContainer = document.getElementById('security-summary-container');

        // clear and render vulnerabilities or show empty message
        vulnContainer.innerHTML = '';
        if (vulnerabilities.length === 0) {
            vulnContainer.innerHTML = `<p class="text-center text-muted">No vulnerabilities found.</p>`;
        } else {
            vulnerabilities.forEach(vuln => {
                const severityClass = getSeverityClass(vuln.risk);
                const card = document.createElement('div');
                card.className = `vuln-card p-3 mb-3`;
                if (vuln.risk) {
                    card.classList.add(`vuln-${vuln.risk.toLowerCase()}`);
                }

                card.innerHTML = `
                    <div class="d-flex justify-content-between">
                      <h5>${vuln.name}</h5>
                      <span class="badge ${severityClass}">${vuln.risk}</span>
                    </div>
                    <p>${vuln.recommendation}</p>`;
                vulnContainer.appendChild(card);
            });
        }

        // summary
        summaryContainer.innerHTML = '';
        const counts = {Critical:0, High:0, Medium:0, Low:0};
        vulnerabilities.forEach(v=> {
            let risk = v.risk || 'Low';
            risk = risk.charAt(0).toUpperCase() + risk.slice(1).toLowerCase();
            if (counts.hasOwnProperty(risk)) {
                counts[risk]++;
            }
        });

        const total = vulnerabilities.length || 1;
        const pct = key => Math.round((counts[key]/total)*100);
        summaryContainer.innerHTML = `
            <h6>Risk Distribution</h6>
            <div class="progress" style="height:20px;">
              <div class="progress-bar bg-danger" style="width:${pct('Critical')}%" title="Critical: ${counts['Critical']}"></div>
              <div class="progress-bar bg-warning" style="width:${pct('High')}%" title="High: ${counts['High']}"></div>
              <div class="progress-bar bg-info" style="width:${pct('Medium')}%" title="Medium: ${counts['Medium']}"></div>
              <div class="progress-bar bg-success" style="width:${pct('Low')}%" title="Low: ${counts['Low']}"></div>
            </div>
            <div class="mt-3">
                <ul class="list-unstyled">
                    <li><span class="badge bg-danger me-2">${counts['Critical']}</span> Critical</li>
                    <li><span class="badge bg-warning me-2">${counts['High']}</span> High</li>
                    <li><span class="badge bg-info me-2">${counts['Medium']}</span> Medium</li>
                    <li><span class="badge bg-success me-2">${counts['Low']}</span> Low</li>
                </ul>
            </div>
            `;

        // Setup PDF export button logic here or ensure it works globally
        const exportBtn = document.getElementById('export-pdf-link');
        if (exportBtn) {
            exportBtn.onclick = (e) => {
                e.preventDefault();
                generatePDFReport(scanData.id);
            };
        }
    }
"""

new_generate_pdf = """    // 5) Modified generatePDFReport: no SweetAlert prompt, immediate download + toast
    function generatePDFReport(scanId) {
        // show loader
        document.querySelector('.cyber-loader-text').textContent = 'GENERATING REPORT';
        document.getElementById('cyber-loader-progress').style.width = '50%';
        document.getElementById('cyber-loader').style.display = 'flex';

        // assemble payload
        const scanData = JSON.parse(localStorage.getItem('threatlens_currentScan') || '{}');
        const vulnerabilities = scanData.results || [];
        const payload = { scanId, results:{ vulnerabilities } };

        fetch('https://magicloops.dev/api/loop/ee1cce1e-f44f-4c0e-b8b9-6b83febb3d79/run', {
            method:'POST', body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById('cyber-loader').style.display = 'none';
            if (data.reportUrl) {
                // immediate download
                const a = document.createElement('a');
                a.href = data.reportUrl;
                a.download = `threatlens-report-${scanId}.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);

                // toast
                Swal.mixin({ toast:true, position:'top-end', showConfirmButton:false, timer:3000 })
                    .fire({ icon:'success', title:'PDF downloaded' });

                // record and notify
                localStorage.setItem(`threatlens_report_${scanId}`, data.reportUrl);
                addNotification('system','Scan Report Ready',`Report for ${scanId} downloaded.`,'reports',{ scanId });
            }
        })
        .catch(err=>{
            console.error(err);
            document.getElementById('cyber-loader').style.display = 'none';
            Swal.fire('Error','Unable to generate report','error');
        });
    }
"""

# Replace populateReportSection
start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if "function populateReportSection() {" in line:
        start_idx = i
    if start_idx != -1 and "function populateReportsTable" in line:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    # Look back for the comment line
    if "// 3) Modified populateReportSection" in lines[start_idx-1]:
        start_idx -= 1

    # We need to find the end of the function precisely.
    # The previous code ended before populateReportsTable with a "}"
    # Let's assume the gap is cleaner if we replace until populateReportsTable starts, but we need to keep populateReportsTable.

    # Actually, simpler approach: find the exact block I want to replace based on known start/end markers.
    pass

# Let's construct the file again.
output_lines = []
skip = False
for line in lines:
    if "function populateReportSection() {" in line:
        # Check if we are at the start of the block to replace
        output_lines.append(new_populate_report)
        skip = True

    if skip and "function populateReportsTable" in line:
        skip = False
        # Don't skip this line, it's the next function

    if "function generatePDFReport(scanId) {" in line:
        output_lines.append(new_generate_pdf)
        skip = True

    if skip and "// 6) Removed startSimulatedScan" in line:
        skip = False

    if not skip:
        output_lines.append(line)

# Since I replaced the comment line in my new string, I should handle the case where the comment line is encountered.
# Actually, the logic above is a bit flawed because "skip" logic is naive.

# Better approach: read the file, identify ranges, replace ranges.

def find_function_range(lines, func_name):
    start = -1
    end = -1
    brace_count = 0
    found_start = False

    for i, line in enumerate(lines):
        if f"function {func_name}" in line:
            start = i
            # Check for previous comment line
            if i > 0 and "//" in lines[i-1] and func_name in lines[i-1]:
                start = i - 1
            found_start = True

        if found_start:
            brace_count += line.count('{')
            brace_count -= line.count('}')
            if brace_count == 0:
                end = i
                return start, end
    return -1, -1

start_pop, end_pop = find_function_range(lines, "populateReportSection")
start_gen, end_gen = find_function_range(lines, "generatePDFReport")

# Create new content
final_lines = lines[:start_pop] + [new_populate_report + "\n\n"] + lines[end_pop+1:start_gen] + [new_generate_pdf + "\n\n"] + lines[end_gen+1:]

with open('tool.html', 'w') as f:
    f.writelines(final_lines)
