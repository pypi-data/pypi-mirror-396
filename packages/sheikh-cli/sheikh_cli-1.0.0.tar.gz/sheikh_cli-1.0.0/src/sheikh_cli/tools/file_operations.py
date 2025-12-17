"""
File Operations Tool Plugin
Handles safe file reading, writing, and directory operations.
"""

import os
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import mimetypes
from datetime import datetime

class FileOperations:
    """Safe file operations with security checks"""
    
    def __init__(self, allowed_directories: List[str]):
        self.allowed_directories = [Path(d).resolve() for d in allowed_directories]
    
    def _is_path_allowed(self, file_path: str) -> bool:
        """Check if file path is within allowed directories"""
        try:
            resolved_path = Path(file_path).resolve()
            return any(
                resolved_path.is_relative_to(allowed_dir) 
                for allowed_dir in self.allowed_directories
            )
        except (ValueError, OSError):
            return False
    
    def read_file(self, file_path: str, encoding: str = 'utf-8') -> str:
        """Read file contents safely"""
        if not self._is_path_allowed(file_path):
            return f"❌ Access denied: {file_path} is outside allowed directories"
        
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return f"❌ File not found: {file_path}"
            
            if file_path.is_file():
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                return f"📄 File: {file_path}\n\n```\n{content}\n```"
            else:
                return f"❌ Not a file: {file_path}"
                
        except Exception as e:
            return f"❌ Error reading file {file_path}: {str(e)}"
    
    def write_file(self, file_path: str, content: str, encoding: str = 'utf-8') -> str:
        """Write content to file safely"""
        if not self._is_path_allowed(file_path):
            return f"❌ Access denied: {file_path} is outside allowed directories"
        
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return f"✅ Successfully wrote {len(content)} characters to {file_path}"
            
        except Exception as e:
            return f"❌ Error writing file {file_path}: {str(e)}"
    
    def list_files(self, directory: str = None, recursive: bool = False) -> str:
        """List files in directory"""
        if directory is None:
            directory = str(self.allowed_directories[0])
        
        if not self._is_path_allowed(directory):
            return f"❌ Access denied: {directory} is outside allowed directories"
        
        try:
            directory = Path(directory)
            if not directory.exists():
                return f"❌ Directory not found: {directory}"
            
            if not directory.is_dir():
                return f"❌ Not a directory: {directory}"
            
            files = []
            if recursive:
                for file_path in directory.rglob('*'):
                    if file_path.is_file():
                        size = file_path.stat().st_size
                        files.append(f"{file_path.relative_to(directory)} ({size} bytes)")
            else:
                for item in directory.iterdir():
                    if item.is_file():
                        size = item.stat().st_size
                        files.append(f"{item.name} ({size} bytes)")
                    elif item.is_dir():
                        files.append(f"{item.name}/ (directory)")
            
            if not files:
                return f"📁 Directory is empty: {directory}"
            
            return f"📁 Contents of {directory}:\n\n" + "\n".join(files)
            
        except Exception as e:
            return f"❌ Error listing directory {directory}: {str(e)}"
    
    def find_files(self, directory: str = None, pattern: str = "*", recursive: bool = True) -> str:
        """Find files by pattern"""
        if directory is None:
            directory = str(self.allowed_directories[0])
        
        if not self._is_path_allowed(directory):
            return f"❌ Access denied: {directory} is outside allowed directories"
        
        try:
            directory = Path(directory)
            if not directory.exists():
                return f"❌ Directory not found: {directory}"
            
            found_files = []
            if recursive:
                for file_path in directory.rglob(pattern):
                    if file_path.is_file():
                        found_files.append(str(file_path.relative_to(directory)))
            else:
                for file_path in directory.glob(pattern):
                    if file_path.is_file():
                        found_files.append(str(file_path.relative_to(directory)))
            
            if not found_files:
                return f"🔍 No files found matching pattern '{pattern}' in {directory}"
            
            return f"🔍 Found {len(found_files)} files matching '{pattern}' in {directory}:\n\n" + "\n".join(found_files)
            
        except Exception as e:
            return f"❌ Error finding files in {directory}: {str(e)}"
    
    def get_file_info(self, file_path: str) -> str:
        """Get detailed file information"""
        if not self._is_path_allowed(file_path):
            return f"❌ Access denied: {file_path} is outside allowed directories"
        
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return f"❌ File not found: {file_path}"
            
            stat = file_path.stat()
            file_type = mimetypes.guess_type(str(file_path))[0] or "unknown"
            
            info = {
                "path": str(file_path),
                "size": f"{stat.st_size} bytes",
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "type": file_type,
                "readable": os.access(file_path, os.R_OK),
                "writable": os.access(file_path, os.W_OK),
            }
            
            return f"📊 File Information:\n\n{json.dumps(info, indent=2)}"
            
        except Exception as e:
            return f"❌ Error getting file info for {file_path}: {str(e)}"
