# DUTVulnScanner - Cross-platform Vulnerability Scanner

🔍 A comprehensive, modular vulnerability scanning framework with support for multiple scanning tools and execution environments.

## Features

- **Multiple Scanning Tools**: 
  - **Recon**: subfinder, naabu, httpx, nmap, whatweb, whois - Information gathering & discovery
  - **Scanners**: nuclei, testssl, sslscan, nikto - Vulnerability detection & SSL/TLS testing
  - **Validators**: dalfox, sqlmap, hydra - Vulnerability verification (opt-in)
- **Local Execution**: Execute scans directly on your local machine
- **Smart Correlation**: Automatically correlates findings from multiple tools
- ** AI-Powered Analysis**: Generate intelligent summaries using Google Gemini
- ** Professional PDF Reports**: Export comprehensive reports with color-coded findings
- **Multiple Report Formats**: Generate reports in HTML, JSON, PDF, and SARIF
- **Customizable Profiles**: Pre-configured scanning profiles for different scenarios
- **Modern CLI**: Beautiful command-line interface built with Typer and Rich

## Installation

### 🚀 Quick Install (Recommended for Kali Linux)

**One-command installation:**
```bash
# Install globally using pipx (recommended)
pipx install git+https://github.com/DinhManhAVG/CLI-Cross-Platform.git

# Or using pip
pip install git+https://github.com/DinhManhAVG/CLI-Cross-Platform.git
```

**Note**: If `pipx` is not installed:
```bash
sudo apt install pipx
pipx ensurepath
source ~/.bashrc
```

**Install from PyPI (Stable Release)**

```bash
pip install dutVulnScanner
```

### From Source (Development)

```bash
# Clone and install
git clone https://github.com/DinhManhAVG/CLI-Cross-Platform.git
cd CLI-Cross-Platform
pip install -e .
```

### Verify Installation

```bash
dutVulnScanner --version
dutVulnScanner --help
```

📖 **For detailed installation instructions, see [INSTALL.md](INSTALL.md)**

## Quick Start

### Interactive Shell Mode (Recommended for beginners)

Start an interactive session where you can configure and run scans without typing `dutVulnScanner` every time:

```bash
dutVulnScanner shell
```

Inside the shell:
```
dutVulnScanner: help                           # Show all commands
dutVulnScanner: set target example.com         # Set your target
dutVulnScanner: set profile web                # Choose a profile
dutVulnScanner: show options                   # Review settings
dutVulnScanner: scan                           # Run the scan
dutVulnScanner: exit                           # Exit shell
```

### Command-Line Mode

### Choose Your Profile

List all available profiles to see which one fits your needs:

```bash
dutVulnScanner profile list
```

### Common Usage Scenarios

#### Quick Security Check (~10 min)
```bash
dutVulnScanner scan run example.com --profile quick
```

#### Basic Reconnaissance (~30 min)
```bash
dutVulnScanner scan run example.com --profile recon
```

#### Complete Discovery Pipeline (~2 hours)
Subdomain enumeration → Port scanning → HTTP probing → Service detection
```bash
dutVulnScanner scan run example.com --profile discovery_full
```

#### Web Application Testing (~1 hour)
```bash
dutVulnScanner scan run https://example.com --profile web
```

#### Vulnerability Scanning (~3 hours)
```bash
dutVulnScanner scan run example.com --profile vuln_scan
```

#### Full Security Assessment (~6 hours)
```bash
dutVulnScanner scan run target.com --profile full_scan --output full_results.json
```

#### ⚠️ Deep Testing (Authorization Required!)
```bash
# XSS, SQLi, brute-force testing - Only with written permission!
dutVulnScanner scan run target.com --profile deep_test
```

### AI-Powered PDF Reports (NEW)

Generate professional PDF reports with AI-powered analysis:

#### Setup
1. Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create `.env` file in project root:
```bash
GEMINI_API_KEY=your_api_key_here
```

#### Generate AI Report
```bash
dutVulnScanner scan run example.com \
  --profile quick \
  --output-dir ./scan_results \
  --generate-report
```

This creates:
- **JSON results**: `scan_results/scan_*/scan_manifest.json`
- **PDF report**: `scan_results/scan_*/report.pdf` with:
  - Executive summary with AI insights
  - Vulnerability statistics dashboard  
  - Prioritized remediation recommendations
  - Detailed findings organized by severity
  - Technical scan details

**Short flag:** Use `-r` instead of `--generate-report`

### Generate Reports

```bash
dutVulnScanner report generate results.json report.html --format html
```

### View Profile Details

```bash
dutVulnScanner profile show recon
dutVulnScanner profile show discovery_full
```

### List Available Profiles

```bash
dutVulnScanner profile list
```

## Architecture

```
dutVulnScanner/
├── cli/                # Command-line interface (Typer)
├── core/               # Core logic (orchestrator, config, schema, correlation)
├── runners/            # Local execution environment
├── plugins/            # Security scanning plugins
│   ├── recon/         # subfinder, naabu, httpx, nmap, whatweb, whois
│   ├── scanners/      # nuclei, testssl, sslscan, nikto
│   └── validators/    # dalfox, sqlmap, hydra
├── reporting/          # Report generation (builder, templates)
└── profiles/           # Scan profiles (recon, discovery_full, vuln_scan, deep_test)
```

## Security Warning

**Important**: Always ensure you have authorization before scanning any target. Unauthorized scanning may be illegal.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes and version history.

## ⚠️ Disclaimer

This tool (`dutVulnScanner`) is developed for **educational and research purposes only**. The author does not condone or support any illegal activities. 

- Only use this tool on systems you own or have explicit permission to test.
- The author is not responsible for any damage caused by the misuse of this tool.
- Misuse of this software may violate local and international laws.

**By using this software, you agree to take full responsibility for your actions.**