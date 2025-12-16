# Scanning Profiles Guide

This directory contains pre-configured scanning profiles for different security testing scenarios.

## Quick Reference

| Profile | Use Case | Tools | Duration | Authorization |
|---------|----------|-------|----------|---------------|
| `quick` | Fast initial scan | Basic tools | ~5-10 min | ✅ Safe |
| `recon` | Basic reconnaissance | whois, nmap, whatweb | ~15-30 min | ✅ Safe |
| `discovery_full` | Complete discovery phase | subfinder, naabu, httpx, nmap | ~1-2 hours | ✅ Safe |
| `web` | Web application testing | whatweb, nuclei, nikto | ~30-60 min | ✅ Safe |
| `vuln_scan` | Vulnerability detection | nuclei, testssl, sslscan, nikto | ~2-3 hours | ✅ Safe |
| `infra` | Infrastructure assessment | nmap, nuclei | ~1-2 hours | ✅ Safe |
| `full_scan` | Comprehensive scan | All discovery + scanning | ~4-6 hours | ✅ Safe |
| `validators` | Vulnerability validation | sqlmap, hydra | ~2-4 hours | ⚠️ Authorization Required |
| `deep_test` | Deep exploitation testing | dalfox, sqlmap, hydra | ~4-8 hours | ⚠️ Authorization Required |

## Profile Details

### 🟢 Safe Profiles (No Authorization Needed)

#### `quick`
- **Purpose**: Quick security assessment
- **Tools**: Basic scanning tools
- **Best for**: Initial triage, time-constrained scans
- **Duration**: 5-10 minutes

```bash
dutVulnScanner scan run example.com --profile quick
```

#### `recon`
- **Purpose**: Basic reconnaissance and information gathering
- **Tools**: whois, nmap, whatweb
- **Best for**: Understanding target infrastructure
- **Duration**: 15-30 minutes

```bash
dutVulnScanner scan run example.com --profile recon
```

#### `discovery_full`
- **Purpose**: Comprehensive discovery pipeline
- **Tools**: subfinder → naabu → httpx → nmap (sequential)
- **Best for**: Complete asset discovery, subdomain enumeration
- **Duration**: 1-2 hours
- **Pipeline**:
  1. subfinder: Find all subdomains
  2. naabu: Fast port scanning
  3. httpx: HTTP service probing
  4. nmap: Detailed service detection

```bash
dutVulnScanner scan run example.com --profile discovery_full
```

#### `web`
- **Purpose**: Web application security testing
- **Tools**: whatweb, nuclei, nikto
- **Best for**: Web apps, HTTP services
- **Duration**: 30-60 minutes

```bash
dutVulnScanner scan run https://example.com --profile web
```

#### `vuln_scan`
- **Purpose**: Automated vulnerability scanning
- **Tools**: nuclei, testssl, sslscan, nikto
- **Best for**: Finding known CVEs, SSL/TLS issues, web server misconfigurations
- **Duration**: 2-3 hours

```bash
dutVulnScanner scan run example.com --profile vuln_scan
```

#### `infra`
- **Purpose**: Infrastructure and network assessment
- **Tools**: nmap, nuclei
- **Best for**: Network services, infrastructure
- **Duration**: 1-2 hours

```bash
dutVulnScanner scan run 192.168.1.0/24 --profile infra
```

#### `full_scan`
- **Purpose**: Complete security assessment (discovery + scanning)
- **Tools**: All discovery and scanning tools
- **Best for**: Comprehensive audits
- **Duration**: 4-6 hours

```bash
dutVulnScanner scan run example.com --profile full_scan --output full_report.json
```

### 🔴 Authorization-Required Profiles

> ⚠️ **WARNING**: These profiles perform active exploitation attempts. Only use with explicit written authorization!

#### `validators`
- **Purpose**: Validate discovered vulnerabilities
- **Tools**: sqlmap, hydra
- **Best for**: Confirming SQLi, weak authentication
- **Duration**: 2-4 hours
- **Risk**: Active exploitation, may trigger alerts

```bash
dutVulnScanner scan run target.com --profile validators
```

#### `deep_test`
- **Purpose**: Deep vulnerability testing and exploitation
- **Tools**: dalfox (XSS), sqlmap (SQLi), hydra (brute-force)
- **Best for**: Penetration testing, security audits
- **Duration**: 4-8 hours
- **Risk**: High - active attacks, may cause service disruption

```bash
dutVulnScanner scan run target.com --profile deep_test
```

## Recommended Workflow

### For Security Assessment:

```bash
# 1. Start with quick scan
dutVulnScanner scan run example.com --profile quick

# 2. If interesting, do full discovery
dutVulnScanner scan run example.com --profile discovery_full

# 3. Run vulnerability scanning
dutVulnScanner scan run example.com --profile vuln_scan

# 4. (With authorization) Validate findings
dutVulnScanner scan run example.com --profile validators
```

### For Bug Bounty:

```bash
# 1. Full discovery to find all assets
dutVulnScanner scan run target.com --profile discovery_full

# 2. Web-focused testing
dutVulnScanner scan run target.com --profile web

# 3. Deep testing on interesting targets
dutVulnScanner scan run app.target.com --profile deep_test
```

### For Penetration Testing:

```bash
# Run complete scan with all tools
dutVulnScanner scan run target.com --profile full_scan
```

## CLI Commands

### List all available profiles:
```bash
dutVulnScanner profile list
```

### View profile details:
```bash
dutVulnScanner profile show recon
dutVulnScanner profile show deep_test
```

### Run scan with specific tools only:
```bash
dutVulnScanner scan run example.com --profile web --tool nuclei --tool nikto
```

## Creating Custom Profiles

You can create custom profiles by copying and modifying existing YAML files:

```yaml
name: my_custom_profile
description: Custom scanning profile

tools:
  - subfinder
  - nuclei

tool_configs:
  subfinder:
    all: true
    timeout: 30
  
  nuclei:
    severity: "critical,high"
    templates_dir: null

parallel: true
timeout: 3600
enable_correlation: true
```

Save as `dutVulnScanner/profiles/my_custom_profile.yaml`

## Legal Notice

⚠️ **Always ensure you have proper authorization before scanning any target!**

- **Safe profiles** (quick, recon, discovery_full, web, vuln_scan, infra, full_scan): Generally safe, passive/non-intrusive
- **Authorization-required profiles** (validators, deep_test): Active exploitation, requires written permission

Unauthorized scanning may be **illegal** and **unethical**. Always follow responsible disclosure practices.
