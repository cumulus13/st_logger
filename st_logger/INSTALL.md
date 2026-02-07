# ST Logger - Installation & Deployment Guide

## Table of Contents

1. [Installation Methods](#installation-methods)
2. [First-Time Setup](#first-time-setup)
3. [Production Deployment](#production-deployment)
4. [Testing Installation](#testing-installation)
5. [Troubleshooting](#troubleshooting)

---

## Installation Methods

### Method 1: Manual Installation (Recommended for Testing)

1. **Locate Sublime Text Packages Directory**

   Open Sublime Text and go to: `Preferences → Browse Packages...`
   
   Or navigate manually:
   - **Windows**: `%APPDATA%\Sublime Text\Packages\`
   - **macOS**: `~/Library/Application Support/Sublime Text/Packages/`
   - **Linux**: `~/.config/sublime-text/Packages/`

2. **Install Plugin**

   Copy the entire `st_logger` folder to the Packages directory:
   ```bash
   # Linux/macOS
   cp -r st_logger ~/.config/sublime-text/Packages/
   
   # Windows (PowerShell)
   Copy-Item -Recurse st_logger "$env:APPDATA\Sublime Text\Packages\"
   ```

3. **Restart Sublime Text**

   The plugin will automatically load on startup.

### Method 2: Git Clone (For Developers)

```bash
# Navigate to Packages directory
cd ~/.config/sublime-text/Packages/  # Linux
cd ~/Library/Application\ Support/Sublime\ Text/Packages/  # macOS
cd %APPDATA%\Sublime Text\Packages\  # Windows

# Clone repository
git clone https://github.com/cumulus13/st_logger.git
```

### Method 3: Package Control (Coming Soon)

1. Open Command Palette: `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
2. Type: `Package Control: Install Package`
3. Search: `ST Logger`
4. Press Enter

---

## First-Time Setup

### 1. Verify Installation

After restarting Sublime Text:

1. Open console: `Ctrl+`` (backtick)
2. Look for: `ST Logger: Started successfully`
3. If not visible, check for error messages

### 2. Configure Basic Settings

Open settings:
- Menu: `Preferences → Package Settings → ST Logger → Settings`
- Or Command Palette: `Preferences: ST Logger Settings`

Minimal configuration:
```json
{
    "enabled": true,
    "file_logging_enabled": true,
    "log_directory": "~/sublime_logs"
}
```

### 3. Verify File Logging

1. Open Command Palette: `Ctrl+Shift+P`
2. Run: `ST Logger: Open Log Directory`
3. Check for log files with today's date

### 4. Test Console Capture

1. Open Sublime console: `Ctrl+``
2. Type: `print("Test message from console")`
3. Press Enter
4. Check log file for the message

---

## Production Deployment

### Enterprise Syslog Configuration

#### Step 1: Configure Syslog Server

Example for rsyslog server (`/etc/rsyslog.conf`):

```conf
# Listen on UDP 514
$ModLoad imudp
$UDPServerRun 514

# Create template for Sublime Text logs
$template SublimeTextLog,"/var/log/sublime/%HOSTNAME%/%$YEAR%%$MONTH%%$DAY%.log"

# Filter by facility
if $syslogfacility-text == 'local0' then -?SublimeTextLog
& stop
```

Restart rsyslog:
```bash
sudo systemctl restart rsyslog
```

#### Step 2: Configure ST Logger

```json
{
    "enabled": true,
    "file_logging_enabled": true,
    "syslog_enabled": true,
    "syslog_host": "syslog.company.com",
    "syslog_port": 514,
    "syslog_facility": "LOG_LOCAL0",
    "min_severity_level": "INFO",
    "log_directory": "/var/log/sublime_text",
    "max_file_size_mb": 100,
    "backup_count": 30
}
```

#### Step 3: Firewall Configuration

Allow UDP 514:
```bash
# Linux (UFW)
sudo ufw allow 514/udp

# Linux (iptables)
sudo iptables -A INPUT -p udp --dport 514 -j ACCEPT

# Verify
sudo netstat -ulnp | grep 514
```

### Cloud Logging Services

#### Papertrail Setup

1. Sign up at https://papertrailapp.com
2. Get your log destination (e.g., `logs7.papertrailapp.com:12345`)
3. Configure ST Logger:

```json
{
    "syslog_enabled": true,
    "syslog_host": "logs7.papertrailapp.com",
    "syslog_port": 12345,
    "min_severity_level": "WARNING"
}
```

#### Splunk Setup

1. Configure Splunk to receive syslog on UDP 514
2. Create an index for Sublime Text logs
3. Configure ST Logger:

```json
{
    "syslog_enabled": true,
    "syslog_host": "splunk.company.com",
    "syslog_port": 514,
    "syslog_facility": "LOG_LOCAL1"
}
```

### Mass Deployment

#### For Multiple Users (Network Share)

1. **Create Master Configuration**

   `sublime_master_config.json`:
   ```json
   {
       "enabled": true,
       "syslog_enabled": true,
       "syslog_host": "logs.company.com",
       "syslog_port": 514,
       "log_directory": "~/sublime_logs",
       "min_severity_level": "INFO"
   }
   ```

2. **Deployment Script** (Linux/macOS)

   ```bash
   #!/bin/bash
   # deploy_st_logger.sh
   
   PLUGIN_DIR="$HOME/.config/sublime-text/Packages/st_logger"
   CONFIG_DIR="$HOME/.config/sublime-text/Packages/User"
   
   # Install plugin
   mkdir -p "$PLUGIN_DIR"
   cp -r st_logger/* "$PLUGIN_DIR/"
   
   # Deploy configuration
   cp sublime_master_config.json "$CONFIG_DIR/STLogger.sublime-settings"
   
   echo "ST Logger deployed successfully"
   ```

3. **Deployment Script** (Windows PowerShell)

   ```powershell
   # deploy_st_logger.ps1
   
   $PluginDir = "$env:APPDATA\Sublime Text\Packages\st_logger"
   $ConfigDir = "$env:APPDATA\Sublime Text\Packages\User"
   
   # Install plugin
   New-Item -ItemType Directory -Force -Path $PluginDir
   Copy-Item -Recurse st_logger\* $PluginDir
   
   # Deploy configuration
   Copy-Item sublime_master_config.json "$ConfigDir\STLogger.sublime-settings"
   
   Write-Host "ST Logger deployed successfully"
   ```

#### Using Group Policy (Windows)

1. Place plugin in network share: `\\server\share\st_logger`
2. Create GPO to copy files on user login
3. Configure startup script to deploy settings

---

## Testing Installation

### Quick Test

Run in Sublime Text console (`Ctrl+``):

```python
# Import test module
import sys
sys.path.append('/path/to/st_logger')
import test_st_logger

# Run all tests
test_st_logger.run_all_tests()
```

### Manual Verification Checklist

- [ ] Plugin loads without errors (check console)
- [ ] Log directory created
- [ ] Log files generated
- [ ] Console output captured
- [ ] Syslog messages received (if enabled)
- [ ] Severity levels correctly assigned
- [ ] File rotation works at size limit
- [ ] Settings reload without restart
- [ ] Commands appear in Command Palette
- [ ] Menu items present under Tools

### Network Testing

Test syslog connectivity:

```bash
# Linux/macOS
nc -u syslog.company.com 514
# Type message and press Ctrl+D

# Windows (PowerShell)
$udpClient = New-Object System.Net.Sockets.UdpClient
$udpClient.Connect("syslog.company.com", 514)
$bytes = [Text.Encoding]::ASCII.GetBytes("Test message")
$udpClient.Send($bytes, $bytes.Length)
```

---

## Troubleshooting

### Plugin Not Loading

**Symptom**: No startup message in console

**Solutions**:
1. Check plugin directory name is exactly `st_logger`
2. Verify Python syntax: `python3 -m py_compile st_logger.py`
3. Check console for error messages
4. Enable Sublime debug mode: `sublime.log_commands(True)`

### Logs Not Created

**Symptom**: Log directory empty

**Solutions**:
1. Verify directory permissions:
   ```bash
   ls -la ~/.sublime_text_logs
   chmod 755 ~/.sublime_text_logs
   ```
2. Check disk space: `df -h`
3. Test write access:
   ```bash
   touch ~/.sublime_text_logs/test.txt
   ```
4. Review settings file syntax (must be valid JSON)

### Syslog Not Receiving Messages

**Symptom**: No logs in syslog server

**Solutions**:
1. Verify network connectivity:
   ```bash
   ping syslog.company.com
   telnet syslog.company.com 514
   ```
2. Check firewall rules (both client and server)
3. Verify UDP port is open:
   ```bash
   nmap -sU -p 514 syslog.company.com
   ```
4. Enable debug logging:
   ```json
   {
       "min_severity_level": "DEBUG"
   }
   ```
5. Check server logs for incoming connections

### High CPU Usage

**Symptom**: Sublime Text using excessive CPU

**Solutions**:
1. Reduce buffer size:
   ```json
   {
       "buffer_max_size": 1000
   }
   ```
2. Increase processing interval:
   ```json
   {
       "processing_interval": 0.5
   }
   ```
3. Increase minimum severity:
   ```json
   {
       "min_severity_level": "WARNING"
   }
   ```
4. Temporarily disable plugin to confirm cause

### Settings Not Applying

**Symptom**: Changes to settings ignored

**Solutions**:
1. Check JSON syntax with validator
2. Reload settings: `ST Logger: Reload Settings`
3. Restart Sublime Text
4. Verify editing User settings, not Default settings
5. Check for duplicate key names in JSON

### Permission Errors (Linux/macOS)

**Symptom**: Cannot write to log directory

**Solutions**:
```bash
# Fix ownership
sudo chown -R $USER:$USER ~/.sublime_text_logs

# Fix permissions
chmod -R 755 ~/.sublime_text_logs

# For system-wide logs
sudo mkdir -p /var/log/sublime_text
sudo chown $USER:$USER /var/log/sublime_text
```

### SELinux Issues (RHEL/CentOS)

**Symptom**: Permission denied despite correct permissions

**Solutions**:
```bash
# Check SELinux status
sestatus

# Allow Sublime to write logs
sudo semanage fcontext -a -t user_home_t "/home/USER/.sublime_text_logs(/.*)?"
sudo restorecon -Rv ~/.sublime_text_logs

# Or temporarily disable
sudo setenforce 0
```

---

## Performance Optimization

### For Heavy Logging (Development)

```json
{
    "buffer_max_size": 50000,
    "processing_interval": 0.05,
    "max_file_size_mb": 200
}
```

### For Production (Minimal Overhead)

```json
{
    "buffer_max_size": 1000,
    "processing_interval": 0.5,
    "min_severity_level": "WARNING",
    "max_file_size_mb": 20
}
```

---

## Support

### Getting Help

1. Check documentation: `README.md`
2. Review example configurations: `STLogger.sublime-settings.example`
3. Run diagnostic: `ST Logger: Show Status`
4. Check GitHub issues
5. Enable debug mode and collect logs

### Reporting Issues

Include:
- Sublime Text version
- OS and version
- Plugin version
- Settings configuration (remove sensitive data)
- Console error messages
- Log file samples
- Steps to reproduce

---

**Last Updated**: 2025-02-07
**Plugin Version**: 1.0.0
