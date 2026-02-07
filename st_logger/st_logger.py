#!/usr/bin/env python3

# File: st_logger/st_logger.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2026-02-07
# Description: ST Logger - Professional Sublime Text Console Log Forwarder
#              Captures console output and forwards to remote syslog server with file export
# License: MIT

"""
ST Logger - Professional Sublime Text Console Log Forwarder
Captures console output and forwards to remote syslog server with file export
"""

import sublime
import sublime_plugin
import logging
import logging.handlers
import socket
import threading
import queue
import os
import sys
import io
from datetime import datetime
import re


class SyslogUDPHandler(logging.handlers.SysLogHandler):
    """Enhanced SysLog handler with better error handling"""
    
    def __init__(self, address, facility=logging.handlers.SysLogHandler.LOG_USER):
        super().__init__(address=address, facility=facility, socktype=socket.SOCK_DGRAM)
        self.socket.settimeout(5.0)
    
    def emit(self, record):
        """Override emit to handle connection errors gracefully"""
        try:
            super().emit(record)
        except (socket.error, OSError) as e:
            # Silently handle network errors to prevent plugin crashes
            pass


class LogBuffer:
    """Thread-safe buffer for console output"""
    
    def __init__(self, max_size=10000):
        self.buffer = queue.Queue(maxsize=max_size)
        self.lock = threading.Lock()
    
    def write(self, message):
        """Add message to buffer"""
        if message and message.strip():
            try:
                self.buffer.put_nowait(message)
            except queue.Full:
                # Drop oldest message if buffer is full
                try:
                    self.buffer.get_nowait()
                    self.buffer.put_nowait(message)
                except queue.Empty:
                    pass
    
    def get_all(self):
        """Get all messages from buffer"""
        messages = []
        while not self.buffer.empty():
            try:
                messages.append(self.buffer.get_nowait())
            except queue.Empty:
                break
        return messages


class ConsoleInterceptor(io.TextIOBase):
    """Intercepts console output and forwards to logger"""
    
    def __init__(self, original_stream, log_buffer, stream_name='stdout'):
        self.original_stream = original_stream
        self.log_buffer = log_buffer
        self.stream_name = stream_name
        self._lock = threading.Lock()
    
    def write(self, message):
        """Write to both original stream and log buffer"""
        with self._lock:
            # Write to original stream
            if self.original_stream:
                try:
                    self.original_stream.write(message)
                except Exception:
                    pass
            
            # Add to log buffer
            if message and message.strip():
                self.log_buffer.write(message)
        
        return len(message)
    
    def flush(self):
        """Flush the original stream"""
        if self.original_stream:
            try:
                self.original_stream.flush()
            except Exception:
                pass
    
    def isatty(self):
        """Check if stream is a TTY"""
        if self.original_stream:
            try:
                return self.original_stream.isatty()
            except Exception:
                pass
        return False


class StLoggerManager:
    """Main logger manager for the plugin"""
    
    def __init__(self):
        self.logger = None
        self.file_handler = None
        self.syslog_handler = None
        self.log_buffer = LogBuffer()
        self.processing_thread = None
        self.stop_event = threading.Event()
        self.settings = None
        self.original_stdout = None
        self.original_stderr = None
        self.interceptor_stdout = None
        self.interceptor_stderr = None
        self.enabled = False
        self.severity_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
    
    def load_settings(self):
        """Load plugin settings"""
        self.settings = sublime.load_settings('STLogger.sublime-settings')
        return self.settings
    
    def get_log_directory(self):
        """Get and create log directory"""
        log_dir = self.settings.get('log_directory', '~/.sublime_text_logs')
        log_dir = os.path.expanduser(log_dir)
        
        # Create directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        return log_dir
    
    def get_log_filename(self):
        """Generate log filename with timestamp"""
        filename_pattern = self.settings.get('log_filename_pattern', 'sublime_{date}.log')
        date_str = datetime.now().strftime('%Y%m%d')
        filename = filename_pattern.replace('{date}', date_str)
        return filename
    
    def parse_severity(self, message):
        """Parse severity level from log message"""
        # Look for severity indicators in message
        message_upper = message.upper()
        
        if any(x in message_upper for x in ['CRITICAL', 'FATAL']):
            return logging.CRITICAL
        elif any(x in message_upper for x in ['ERROR', 'EXCEPTION', 'TRACEBACK']):
            return logging.ERROR
        elif any(x in message_upper for x in ['WARNING', 'WARN']):
            return logging.WARNING
        elif 'DEBUG' in message_upper:
            return logging.DEBUG
        else:
            return logging.INFO
    
    def setup_logger(self):
        """Setup logging handlers"""
        if not self.settings.get('enabled', True):
            return
        
        # Create logger
        self.logger = logging.getLogger('st_logger')
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        
        # Setup file handler
        if self.settings.get('file_logging_enabled', True):
            try:
                log_dir = self.get_log_directory()
                log_file = os.path.join(log_dir, self.get_log_filename())
                
                max_bytes = self.settings.get('max_file_size_mb', 10) * 1024 * 1024
                backup_count = self.settings.get('backup_count', 5)
                
                self.file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                
                file_format = self.settings.get('file_log_format', 
                    '%(asctime)s - %(levelname)s - %(message)s')
                file_formatter = logging.Formatter(file_format)
                self.file_handler.setFormatter(file_formatter)
                self.logger.addHandler(self.file_handler)
                
            except Exception as e:
                print("ST Logger: Failed to setup file handler: {}".format(e))
        
        # Setup syslog handler
        if self.settings.get('syslog_enabled', False):
            try:
                syslog_host = self.settings.get('syslog_host', 'localhost')
                syslog_port = self.settings.get('syslog_port', 514)
                facility = self.settings.get('syslog_facility', 'LOG_USER')
                
                # Convert facility string to constant
                facility_value = getattr(
                    logging.handlers.SysLogHandler,
                    facility,
                    logging.handlers.SysLogHandler.LOG_USER
                )
                
                self.syslog_handler = SyslogUDPHandler(
                    address=(syslog_host, syslog_port),
                    facility=facility_value
                )
                
                syslog_format = self.settings.get('syslog_format',
                    'SublimeText[%(process)d]: %(levelname)s - %(message)s')
                syslog_formatter = logging.Formatter(syslog_format)
                self.syslog_handler.setFormatter(syslog_formatter)
                self.logger.addHandler(self.syslog_handler)
                
            except Exception as e:
                print("ST Logger: Failed to setup syslog handler: {}".format(e))
    
    def start_interception(self):
        """Start intercepting console output"""
        if self.enabled:
            return
        
        # Store original streams
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        # Create interceptors
        self.interceptor_stdout = ConsoleInterceptor(
            self.original_stdout, self.log_buffer, 'stdout')
        self.interceptor_stderr = ConsoleInterceptor(
            self.original_stderr, self.log_buffer, 'stderr')
        
        # Replace sys streams
        sys.stdout = self.interceptor_stdout
        sys.stderr = self.interceptor_stderr
        
        self.enabled = True
    
    def stop_interception(self):
        """Stop intercepting console output"""
        if not self.enabled:
            return
        
        # Restore original streams
        if self.original_stdout:
            sys.stdout = self.original_stdout
        if self.original_stderr:
            sys.stderr = self.original_stderr
        
        self.enabled = False
    
    def process_logs(self):
        """Process buffered logs in background thread"""
        while not self.stop_event.is_set():
            try:
                messages = self.log_buffer.get_all()
                
                for message in messages:
                    if not message.strip():
                        continue
                    
                    # Parse severity
                    severity = self.parse_severity(message)
                    
                    # Check if severity should be logged
                    min_severity = self.settings.get('min_severity_level', 'DEBUG')
                    min_level = self.severity_map.get(min_severity, logging.DEBUG)
                    
                    if severity >= min_level:
                        # Log to handlers
                        if self.logger:
                            self.logger.log(severity, message.strip())
                
                # Sleep to prevent CPU hogging
                self.stop_event.wait(0.1)
                
            except Exception as e:
                # Silently handle errors to prevent crashes
                pass
    
    def start(self):
        """Start the logger manager"""
        self.load_settings()
        
        if not self.settings.get('enabled', True):
            print("ST Logger: Plugin disabled in settings")
            return
        
        self.setup_logger()
        self.start_interception()
        
        # Start processing thread
        self.stop_event.clear()
        self.processing_thread = threading.Thread(
            target=self.process_logs,
            daemon=True,
            name='STLoggerProcessor'
        )
        self.processing_thread.start()
        
        print("ST Logger: Started successfully")
    
    def stop(self):
        """Stop the logger manager"""
        # Signal thread to stop
        self.stop_event.set()
        
        # Stop interception
        self.stop_interception()
        
        # Wait for thread to finish
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)
        
        # Process remaining logs
        if self.logger:
            messages = self.log_buffer.get_all()
            for message in messages:
                if message.strip():
                    severity = self.parse_severity(message)
                    self.logger.log(severity, message.strip())
        
        # Close handlers
        if self.file_handler:
            self.file_handler.close()
            self.logger.removeHandler(self.file_handler)
        
        if self.syslog_handler:
            self.syslog_handler.close()
            self.logger.removeHandler(self.syslog_handler)
        
        print("ST Logger: Stopped")
    
    def reload(self):
        """Reload the logger with new settings"""
        self.stop()
        self.start()


# Global manager instance
logger_manager = StLoggerManager()


def plugin_loaded():
    """Called when plugin is loaded"""
    # Delay startup slightly to ensure Sublime is ready
    sublime.set_timeout_async(logger_manager.start, 100)


def plugin_unloaded():
    """Called when plugin is unloaded"""
    logger_manager.stop()


class StLoggerToggleCommand(sublime_plugin.ApplicationCommand):
    """Command to toggle logger on/off"""
    
    def run(self):
        settings = sublime.load_settings('STLogger.sublime-settings')
        enabled = settings.get('enabled', True)
        settings.set('enabled', not enabled)
        sublime.save_settings('STLogger.sublime-settings')
        
        if not enabled:
            logger_manager.start()
            sublime.status_message("ST Logger: Enabled")
        else:
            logger_manager.stop()
            sublime.status_message("ST Logger: Disabled")
    
    def is_checked(self):
        settings = sublime.load_settings('STLogger.sublime-settings')
        return settings.get('enabled', True)


class StLoggerReloadCommand(sublime_plugin.ApplicationCommand):
    """Command to reload logger settings"""
    
    def run(self):
        logger_manager.reload()
        sublime.status_message("ST Logger: Settings reloaded")


class StLoggerOpenLogDirCommand(sublime_plugin.ApplicationCommand):
    """Command to open log directory"""
    
    def run(self):
        settings = sublime.load_settings('STLogger.sublime-settings')
        log_dir = settings.get('log_directory', '~/.sublime_text_logs')
        log_dir = os.path.expanduser(log_dir)
        
        # Create if doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Open directory
        if sublime.platform() == 'windows':
            os.startfile(log_dir)
        elif sublime.platform() == 'osx':
            os.system('open "{}"'.format(log_dir))
        else:
            os.system('xdg-open "{}"'.format(log_dir))


class StLoggerShowStatusCommand(sublime_plugin.ApplicationCommand):
    """Command to show logger status"""
    
    def run(self):
        settings = sublime.load_settings('STLogger.sublime-settings')
        enabled = settings.get('enabled', True)
        syslog_enabled = settings.get('syslog_enabled', False)
        file_enabled = settings.get('file_logging_enabled', True)
        
        status = "ST Logger Status:\n"
        status += "  Plugin: {}\n".format('Enabled' if enabled else 'Disabled')
        status += "  File Logging: {}\n".format('Enabled' if file_enabled else 'Disabled')
        status += "  Syslog: {}\n".format('Enabled' if syslog_enabled else 'Disabled')
        
        if syslog_enabled:
            host = settings.get('syslog_host', 'localhost')
            port = settings.get('syslog_port', 514)
            status += "  Syslog Server: {}:{}\n".format(host, port)
        
        if file_enabled:
            log_dir = settings.get('log_directory', '~/.sublime_text_logs')
            status += "  Log Directory: {}\n".format(log_dir)
        
        sublime.message_dialog(status)
