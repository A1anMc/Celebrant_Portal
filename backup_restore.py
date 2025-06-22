#!/usr/bin/env python3
"""
Backup and restore system for the Celebrant Portal.
This script handles database backups, file backups, and restoration.
"""

import os
import sys
import shutil
import sqlite3
import logging
import json
import tarfile
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from app import app, db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

class BackupManager:
    """Manages backup and restore operations."""
    
    def __init__(self, backup_dir: str = 'backups'):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self, include_files: bool = True) -> Dict[str, Any]:
        """Create a complete backup of the system."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"celebrant_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        try:
            logger.info(f"Creating backup: {backup_name}")
            
            # Backup database
            db_backup_path = self.backup_database(backup_path)
            
            # Backup important files
            files_backup_path = None
            if include_files:
                files_backup_path = self.backup_files(backup_path)
            
            # Create metadata
            metadata = {
                'backup_name': backup_name,
                'timestamp': timestamp,
                'created_at': datetime.now().isoformat(),
                'database_backup': str(db_backup_path.name) if db_backup_path else None,
                'files_backup': str(files_backup_path.name) if files_backup_path else None,
                'app_version': '1.0.0',  # You can make this dynamic
                'python_version': sys.version,
                'backup_size': self.get_directory_size(backup_path)
            }
            
            # Save metadata
            metadata_path = backup_path / 'metadata.json'
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Create compressed archive
            archive_path = self.backup_dir / f"{backup_name}.tar.gz"
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(backup_path, arcname=backup_name)
            
            # Remove uncompressed backup directory
            shutil.rmtree(backup_path)
            
            logger.info(f"Backup created successfully: {archive_path}")
            
            return {
                'success': True,
                'backup_path': str(archive_path),
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            # Cleanup on failure
            if backup_path.exists():
                shutil.rmtree(backup_path)
            return {
                'success': False,
                'error': str(e)
            }
    
    def backup_database(self, backup_path: Path) -> Optional[Path]:
        """Backup the SQLite database."""
        try:
            # Get database path
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            if not db_uri.startswith('sqlite:///'):
                raise ValueError("Only SQLite databases are supported for backup")
            
            source_db_path = db_uri.replace('sqlite:///', '')
            if not os.path.exists(source_db_path):
                raise FileNotFoundError(f"Database file not found: {source_db_path}")
            
            # Create backup
            backup_db_path = backup_path / 'database.db'
            
            # Use SQLite's backup API for consistency
            source_conn = sqlite3.connect(source_db_path)
            backup_conn = sqlite3.connect(str(backup_db_path))
            
            source_conn.backup(backup_conn)
            
            source_conn.close()
            backup_conn.close()
            
            logger.info(f"Database backed up to: {backup_db_path}")
            return backup_db_path
            
        except Exception as e:
            logger.error(f"Database backup failed: {str(e)}")
            raise
    
    def backup_files(self, backup_path: Path) -> Optional[Path]:
        """Backup important files and directories."""
        try:
            files_backup_path = backup_path / 'files'
            files_backup_path.mkdir(exist_ok=True)
            
            # Files and directories to backup
            important_paths = [
                'credentials.json',
                'token.pickle',
                'templates/email/',
                'static/',
                'instance/',
                'celebrant_portal.log'
            ]
            
            backed_up_files = []
            
            for path_str in important_paths:
                source_path = Path(path_str)
                if source_path.exists():
                    dest_path = files_backup_path / path_str
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if source_path.is_file():
                        shutil.copy2(source_path, dest_path)
                    elif source_path.is_dir():
                        shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                    
                    backed_up_files.append(path_str)
                    logger.info(f"Backed up: {path_str}")
            
            # Save list of backed up files
            file_list_path = files_backup_path / 'file_list.json'
            with open(file_list_path, 'w') as f:
                json.dump(backed_up_files, f, indent=2)
            
            logger.info(f"Files backed up to: {files_backup_path}")
            return files_backup_path
            
        except Exception as e:
            logger.error(f"Files backup failed: {str(e)}")
            raise
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups."""
        backups = []
        
        for backup_file in self.backup_dir.glob('celebrant_backup_*.tar.gz'):
            try:
                # Extract metadata without extracting the whole archive
                with tarfile.open(backup_file, 'r:gz') as tar:
                    metadata_member = None
                    for member in tar.getmembers():
                        if member.name.endswith('metadata.json'):
                            metadata_member = member
                            break
                    
                    if metadata_member:
                        metadata_file = tar.extractfile(metadata_member)
                        if metadata_file:
                            metadata = json.load(metadata_file)
                            metadata['backup_file'] = str(backup_file)
                            metadata['file_size'] = backup_file.stat().st_size
                            backups.append(metadata)
            except Exception as e:
                logger.warning(f"Could not read metadata from {backup_file}: {str(e)}")
                # Add basic info even if metadata is corrupted
                stat = backup_file.stat()
                backups.append({
                    'backup_name': backup_file.stem,
                    'backup_file': str(backup_file),
                    'file_size': stat.st_size,
                    'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'metadata_error': str(e)
                })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return backups
    
    def restore_backup(self, backup_path: str, restore_database: bool = True, restore_files: bool = True) -> Dict[str, Any]:
        """Restore from a backup."""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            logger.info(f"Restoring from backup: {backup_file}")
            
            # Create temporary extraction directory
            temp_dir = self.backup_dir / 'temp_restore'
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            temp_dir.mkdir()
            
            try:
                # Extract backup
                with tarfile.open(backup_file, 'r:gz') as tar:
                    tar.extractall(temp_dir)
                
                # Find the extracted directory
                extracted_dirs = [d for d in temp_dir.iterdir() if d.is_dir()]
                if not extracted_dirs:
                    raise ValueError("No directory found in backup archive")
                
                backup_content_dir = extracted_dirs[0]
                
                # Load metadata
                metadata_path = backup_content_dir / 'metadata.json'
                metadata = {}
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                
                restored_items = []
                
                # Restore database
                if restore_database:
                    db_backup_path = backup_content_dir / 'database.db'
                    if db_backup_path.exists():
                        self.restore_database(db_backup_path)
                        restored_items.append('database')
                        logger.info("Database restored successfully")
                
                # Restore files
                if restore_files:
                    files_backup_path = backup_content_dir / 'files'
                    if files_backup_path.exists():
                        self.restore_files(files_backup_path)
                        restored_items.append('files')
                        logger.info("Files restored successfully")
                
                return {
                    'success': True,
                    'restored_items': restored_items,
                    'metadata': metadata
                }
                
            finally:
                # Cleanup temporary directory
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def restore_database(self, backup_db_path: Path):
        """Restore the database from backup."""
        try:
            # Get current database path
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            current_db_path = db_uri.replace('sqlite:///', '')
            
            # Create backup of current database
            if os.path.exists(current_db_path):
                backup_current_path = f"{current_db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(current_db_path, backup_current_path)
                logger.info(f"Current database backed up to: {backup_current_path}")
            
            # Restore from backup
            shutil.copy2(backup_db_path, current_db_path)
            logger.info("Database restored from backup")
            
        except Exception as e:
            logger.error(f"Database restore failed: {str(e)}")
            raise
    
    def restore_files(self, files_backup_path: Path):
        """Restore files from backup."""
        try:
            # Read file list if available
            file_list_path = files_backup_path / 'file_list.json'
            if file_list_path.exists():
                with open(file_list_path, 'r') as f:
                    file_list = json.load(f)
            else:
                # If no file list, restore everything
                file_list = []
                for item in files_backup_path.rglob('*'):
                    if item.is_file() and item.name != 'file_list.json':
                        rel_path = item.relative_to(files_backup_path)
                        file_list.append(str(rel_path))
            
            # Restore each file/directory
            for file_path in file_list:
                source_path = files_backup_path / file_path
                dest_path = Path(file_path)
                
                if source_path.exists():
                    # Create parent directories if needed
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if source_path.is_file():
                        shutil.copy2(source_path, dest_path)
                    elif source_path.is_dir():
                        if dest_path.exists():
                            shutil.rmtree(dest_path)
                        shutil.copytree(source_path, dest_path)
                    
                    logger.info(f"Restored: {file_path}")
            
        except Exception as e:
            logger.error(f"Files restore failed: {str(e)}")
            raise
    
    def cleanup_old_backups(self, keep_count: int = 10):
        """Remove old backups, keeping only the most recent ones."""
        try:
            backups = self.list_backups()
            
            if len(backups) <= keep_count:
                logger.info(f"Only {len(backups)} backups found, no cleanup needed")
                return
            
            # Remove old backups
            backups_to_remove = backups[keep_count:]
            removed_count = 0
            
            for backup in backups_to_remove:
                backup_file = Path(backup['backup_file'])
                if backup_file.exists():
                    backup_file.unlink()
                    removed_count += 1
                    logger.info(f"Removed old backup: {backup_file.name}")
            
            logger.info(f"Cleanup completed. Removed {removed_count} old backups")
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {str(e)}")
    
    @staticmethod
    def get_directory_size(directory: Path) -> int:
        """Get the total size of a directory in bytes."""
        total_size = 0
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Backup and restore system for Celebrant Portal')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create backup command
    backup_parser = subparsers.add_parser('backup', help='Create a backup')
    backup_parser.add_argument('--no-files', action='store_true', help='Skip file backup')
    backup_parser.add_argument('--backup-dir', default='backups', help='Backup directory')
    
    # List backups command
    list_parser = subparsers.add_parser('list', help='List available backups')
    list_parser.add_argument('--backup-dir', default='backups', help='Backup directory')
    
    # Restore backup command
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('backup_file', help='Path to backup file')
    restore_parser.add_argument('--no-database', action='store_true', help='Skip database restore')
    restore_parser.add_argument('--no-files', action='store_true', help='Skip files restore')
    restore_parser.add_argument('--backup-dir', default='backups', help='Backup directory')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old backups')
    cleanup_parser.add_argument('--keep', type=int, default=10, help='Number of backups to keep')
    cleanup_parser.add_argument('--backup-dir', default='backups', help='Backup directory')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    backup_manager = BackupManager(args.backup_dir)
    
    if args.command == 'backup':
        result = backup_manager.create_backup(include_files=not args.no_files)
        if result['success']:
            print(f"Backup created successfully: {result['backup_path']}")
            print(f"Size: {BackupManager.format_size(result['metadata']['backup_size'])}")
        else:
            print(f"Backup failed: {result['error']}")
            sys.exit(1)
    
    elif args.command == 'list':
        backups = backup_manager.list_backups()
        if not backups:
            print("No backups found")
        else:
            print(f"{'Backup Name':<30} {'Created':<20} {'Size':<10}")
            print("-" * 60)
            for backup in backups:
                size = BackupManager.format_size(backup.get('file_size', 0))
                created = backup.get('created_at', 'Unknown')[:19]  # Truncate timestamp
                print(f"{backup['backup_name']:<30} {created:<20} {size:<10}")
    
    elif args.command == 'restore':
        result = backup_manager.restore_backup(
            args.backup_file,
            restore_database=not args.no_database,
            restore_files=not args.no_files
        )
        if result['success']:
            print(f"Restore completed successfully")
            print(f"Restored items: {', '.join(result['restored_items'])}")
        else:
            print(f"Restore failed: {result['error']}")
            sys.exit(1)
    
    elif args.command == 'cleanup':
        backup_manager.cleanup_old_backups(args.keep)
        print(f"Cleanup completed, keeping {args.keep} most recent backups")

if __name__ == '__main__':
    main() 