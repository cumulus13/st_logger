# ST Logger

Professional Sublime Text plugin for capturing console output and forwarding to remote syslog servers with file export capabilities.

## Features

- **Console Output Capture**: Automatically intercepts all console output from Ctrl+` (Sublime Text console)
- **Remote Syslog Forwarding**: Sends logs to remote syslog servers (RFC 5424 compatible) via UDP port 514
- **Severity-Based Filtering**: Automatically parses and categorizes logs by severity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **File Export**: Saves logs to rotating files with configurable size limits
- **Production-Ready**: Thread-safe, robust error handling, designed for high-volume environments
- **Fully Configurable**: All settings customizable via settings file
- **Performance Optimized**: Asynchronous processing, buffered I/O, minimal overhead

## Installation

### Manual Installation

1. Download or clone this repository
2. Copy the `st_logger` folder to your Sublime Text Packages directory:
   - **Windows**: `%APPDATA%\Sublime Text\Packages\`
   - **macOS**: `~/Library/Application Support/Sublime Text/Packages/`
   - **Linux**: `~/.config/sublime-text/Packages/`
3. Restart Sublime Text

### Package Control (Coming Soon)

1. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Select "Package Control: Install Package"
3. Search for "ST Logger"

## Configuration

### Quick Start

1. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Type "Preferences: ST Logger Settings"
3. Configure your settings

### Settings Reference

Access settings via: `Preferences > Package Settings > ST Logger > Settings`

```json
{
    // Enable/disable the plugin
    "enabled": true,
    
    // File Logging
    "file_logging_enabled": true,
    "log_directory": "~/.sublime_text_logs",
    "log_filename_pattern": "sublime_{date}.log",
    "max_file_size_mb": 10,
    "backup_count": 5,
    
    // Syslog Configuration
    "syslog_enabled": false,
    "syslog_host": "localhost",
    "syslog_port": 514,
    "syslog_facility": "LOG_USER",
    
    // Filtering
    "min_severity_level": "DEBUG"
}
```

### Severity Levels

The plugin automatically detects severity levels from log messages:

- **CRITICAL**: Fatal errors, system crashes
- **ERROR**: Error messages, exceptions, tracebacks
- **WARNING**: Warning messages
- **INFO**: Informational messages (default for unclassified logs)
- **DEBUG**: Debug output

### Syslog Facilities

Available syslog facilities:
- `LOG_USER` (default) - User-level messages
- `LOG_LOCAL0` through `LOG_LOCAL7` - Local use facilities

## Usage

### Command Palette Commands

- **ST Logger: Toggle Plugin** - Enable/disable the plugin
- **ST Logger: Show Status** - Display current configuration status
- **ST Logger: Reload Settings** - Reload configuration without restart
- **ST Logger: Open Log Directory** - Open the log directory in file browser

### Menu Access

Access via: `Tools > ST Logger`

### Automatic Operation

Once enabled, ST Logger automatically:
1. Captures all console output (from Ctrl+`)
2. Parses severity levels
3. Forwards to configured syslog server(s)
4. Exports to log files with rotation
5. Handles errors gracefully without disrupting Sublime Text

## Remote Syslog Setup

### Example: Forwarding to Papertrail

```json
{
    "syslog_enabled": true,
    "syslog_host": "logs.papertrailapp.com",
    "syslog_port": 12345,
    "syslog_facility": "LOG_USER"
}
```

### Example: Forwarding to Local Rsyslog

```json
{
    "syslog_enabled": true,
    "syslog_host": "localhost",
    "syslog_port": 514,
    "syslog_facility": "LOG_LOCAL0"
}
```

### Example: Multiple Destinations

For multiple syslog destinations, configure your syslog server to relay messages, or run multiple instances with different settings profiles.

## Log File Management

### File Rotation

Logs automatically rotate when they reach the configured size limit:

```json
{
    "max_file_size_mb": 10,      // 10 MB per file
    "backup_count": 5             // Keep 5 backup files
}
```

This creates files like:
- `sublime_20250207.log` (current)
- `sublime_20250207.log.1` (1st backup)
- `sublime_20250207.log.2` (2nd backup)
- etc.

### Custom Log Formats

Customize log output format using Python logging format strings:

```json
{
    "file_log_format": "%(asctime)s - %(levelname)s - %(message)s",
    "syslog_format": "SublimeText[%(process)d]: %(levelname)s - %(message)s"
}
```

Available fields:
- `%(asctime)s` - Timestamp
- `%(levelname)s` - Severity level
- `%(message)s` - Log message
- `%(process)d` - Process ID
- `%(name)s` - Logger name

## Performance Considerations

### For High-Volume Environments

The plugin is designed for production use with millions of users:

- **Asynchronous Processing**: Logs processed in background thread
- **Buffered I/O**: Messages queued to prevent blocking
- **Graceful Degradation**: Network failures don't crash the plugin
- **Memory Safety**: Buffer size limits prevent memory exhaustion
- **Thread Safety**: All operations protected with locks

### Tuning Performance

```json
{
    // Increase buffer for high-volume logging
    "buffer_max_size": 50000,
    
    // Adjust processing interval (seconds)
    "processing_interval": 0.05,
    
    // Increase file size before rotation
    "max_file_size_mb": 50
}
```

## Troubleshooting

### Plugin Not Starting

1. Check console (Ctrl+`) for error messages
2. Verify settings file syntax is valid JSON
3. Ensure log directory has write permissions
4. Try: Command Palette > "ST Logger: Reload Settings"

### Syslog Not Receiving Messages

1. Verify syslog server is running and accessible
2. Check firewall rules allow UDP port 514
3. Test connectivity: `nc -u <host> <port>`
4. Enable debug logging: Set `"min_severity_level": "DEBUG"`
5. Check server logs for incoming connections

### Files Not Created

1. Check log directory permissions
2. Verify path is correct (use absolute paths if needed)
3. Ensure disk has available space
4. Check console for write errors

### High CPU Usage

1. Reduce buffer size: `"buffer_max_size": 1000`
2. Increase processing interval: `"processing_interval": 0.5`
3. Increase minimum severity: `"min_severity_level": "WARNING"`

## Security Considerations

### Network Security

- Syslog uses UDP (unencrypted) by default
- For production, use VPN or SSH tunneling for sensitive data
- Consider using syslog-ng or rsyslog with TLS for encryption

### File Permissions

- Log files inherit directory permissions
- Recommended: `chmod 700 ~/.sublime_text_logs`
- Logs may contain sensitive information from console output

### Data Privacy

- Console output may include file paths, code snippets, API keys
- Review log files before sharing
- Configure `.gitignore` to exclude log directories

## Advanced Usage

### Filtering Specific Messages

Edit the plugin to add custom filters:

```python
def should_log_message(self, message):
    # Skip messages containing sensitive data
    if 'API_KEY' in message or 'PASSWORD' in message:
        return False
    return True
```

### Custom Severity Detection

Modify the `parse_severity` method for custom rules:

```python
def parse_severity(self, message):
    if '[CRITICAL]' in message:
        return logging.CRITICAL
    # ... add custom patterns
```

### Integration with CI/CD

```bash
# Enable logging for automated tests
echo '{"enabled": true, "syslog_enabled": true}' > ~/.config/sublime-text/Packages/User/STLogger.sublime-settings
```

## Development

### Requirements

- Python 3.8+ (included with Sublime Text 4)
- No external dependencies

### Testing

1. Enable debug logging: `"min_severity_level": "DEBUG"`
2. Open console: Ctrl+`
3. Run test commands to generate log output
4. Verify logs appear in files and syslog server

### Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## License

MIT License - See [LICENSE](LICENSE) file for details

## 👤 Author
        
[Hadi Cahyadi](mailto:cumulus13@gmail.com)
    

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)
 
[Support me on Patreon](https://www.patreon.com/cumulus13)

## Support

- **Issues**: https://github.com/cumulus13/st_logger/issues
- **Discussions**: https://github.com/cumulus13/st_logger/discussions
- **Email**: support@example.com

## Changelog

### Version 1.0.0 (2025-02-07)
- Initial release
- Console output capture
- Remote syslog forwarding
- File export with rotation
- Severity-based filtering
- Full configuration support

## Acknowledgments

Built with ❤️ for the Sublime Text community

---

**Note**: This plugin intercepts console output using Python's `sys.stdout` and `sys.stderr`. It is designed to be non-intrusive and fail-safe, but if you experience any issues, you can always disable it via the Command Palette.
