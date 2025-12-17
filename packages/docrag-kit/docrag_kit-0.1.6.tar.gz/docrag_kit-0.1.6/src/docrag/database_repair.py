"""
Database repair utilities for DocRAG Kit.

This module provides utilities to diagnose and fix common database issues,
particularly the "readonly database" error that can occur with SQLite/ChromaDB.
"""

import os
import shutil
import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional


class DatabaseRepair:
    """Utility class for diagnosing and repairing database issues."""
    
    def __init__(self, project_root: Path):
        """
        Initialize database repair utility.
        
        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root
        self.docrag_dir = project_root / ".docrag"
        self.vectordb_path = self.docrag_dir / "vectordb"
    
    def diagnose_issues(self) -> Tuple[List[str], List[str]]:
        """
        Diagnose database issues.
        
        Returns:
            Tuple of (critical_issues, warnings)
        """
        critical_issues = []
        warnings = []
        
        if not self.docrag_dir.exists():
            critical_issues.append("DocRAG not initialized (.docrag directory missing)")
            return critical_issues, warnings
        
        if not self.vectordb_path.exists():
            warnings.append("Vector database not created yet")
            return critical_issues, warnings
        
        # Check directory permissions
        if not os.access(self.vectordb_path, os.W_OK):
            critical_issues.append("Vector database directory not writable")
        
        # Check for lock files
        lock_files = (
            list(self.vectordb_path.rglob("*.db-wal")) +
            list(self.vectordb_path.rglob("*.db-shm")) +
            list(self.vectordb_path.rglob("*.lock"))
        )
        if lock_files:
            warnings.append(f"Database lock files found ({len(lock_files)} files)")
        
        # Check SQLite databases
        db_files = (
            list(self.vectordb_path.rglob("*.sqlite*")) +
            list(self.vectordb_path.rglob("*.db"))
        )
        
        for db_file in db_files:
            try:
                # Try to open in write mode
                conn = sqlite3.connect(str(db_file), timeout=1.0)
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.close()
            except sqlite3.OperationalError as e:
                if "readonly database" in str(e).lower():
                    critical_issues.append(f"Readonly database: {db_file.name}")
                elif "database is locked" in str(e).lower():
                    critical_issues.append(f"Database locked: {db_file.name}")
                else:
                    warnings.append(f"Database issue in {db_file.name}: {e}")
            except Exception as e:
                warnings.append(f"Could not check {db_file.name}: {e}")
        
        # Check disk space
        try:
            statvfs = os.statvfs(str(self.docrag_dir))
            free_bytes = statvfs.f_frsize * statvfs.f_bavail
            free_mb = free_bytes / (1024 * 1024)
            
            if free_mb < 50:  # Less than 50MB
                critical_issues.append(f"Low disk space ({free_mb:.1f} MB available)")
            elif free_mb < 200:  # Less than 200MB
                warnings.append(f"Low disk space ({free_mb:.1f} MB available)")
        except Exception:
            warnings.append("Could not check disk space")
        
        return critical_issues, warnings
    
    def fix_permissions(self) -> bool:
        """
        Fix directory and file permissions.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.vectordb_path.exists():
                return True
            
            # Fix directory permissions
            os.chmod(self.vectordb_path, 0o755)
            
            # Fix file permissions recursively
            for root, dirs, files in os.walk(self.vectordb_path):
                for d in dirs:
                    os.chmod(os.path.join(root, d), 0o755)
                for f in files:
                    os.chmod(os.path.join(root, f), 0o644)
            
            return True
        except Exception:
            return False
    
    def remove_lock_files(self) -> bool:
        """
        Remove database lock files.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.vectordb_path.exists():
                return True
            
            lock_files = (
                list(self.vectordb_path.rglob("*.db-wal")) +
                list(self.vectordb_path.rglob("*.db-shm")) +
                list(self.vectordb_path.rglob("*.lock"))
            )
            
            for lock_file in lock_files:
                lock_file.unlink()
            
            return True
        except Exception:
            return False
    
    def rebuild_database(self) -> bool:
        """
        Remove corrupted database (requires reindexing after).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.vectordb_path.exists():
                shutil.rmtree(self.vectordb_path)
            return True
        except Exception:
            return False
    
    def fix_readonly_database(self) -> bool:
        """
        Fix readonly database issues by resetting permissions and removing locks.
        
        Returns:
            True if successful, False otherwise
        """
        success = True
        
        # Step 1: Fix permissions
        if not self.fix_permissions():
            success = False
        
        # Step 2: Remove lock files
        if not self.remove_lock_files():
            success = False
        
        # Step 3: Try to access database
        if self.vectordb_path.exists():
            db_files = (
                list(self.vectordb_path.rglob("*.sqlite*")) +
                list(self.vectordb_path.rglob("*.db"))
            )
            
            for db_file in db_files:
                try:
                    # Try to open and perform a simple operation
                    conn = sqlite3.connect(str(db_file), timeout=5.0)
                    conn.execute("PRAGMA journal_mode=WAL;")
                    conn.execute("PRAGMA synchronous=NORMAL;")
                    conn.close()
                except sqlite3.OperationalError:
                    # If still readonly, the database is corrupted
                    success = False
                    break
                except Exception:
                    success = False
                    break
        
        return success
    
    def get_repair_recommendations(self, critical_issues: List[str], warnings: List[str]) -> List[str]:
        """
        Get repair recommendations based on diagnosed issues.
        
        Args:
            critical_issues: List of critical issues
            warnings: List of warnings
        
        Returns:
            List of recommended actions
        """
        recommendations = []
        
        if "DocRAG not initialized" in str(critical_issues):
            recommendations.append("Run 'docrag init' to initialize DocRAG")
            return recommendations
        
        if any("readonly database" in issue.lower() for issue in critical_issues):
            recommendations.extend([
                "Run 'docrag fix-database' to repair readonly database",
                "Or manually: rm -rf .docrag/vectordb && docrag index"
            ])
        
        if any("database locked" in issue.lower() for issue in critical_issues):
            recommendations.extend([
                "Close any applications using the database",
                "Run 'docrag fix-database' to remove lock files"
            ])
        
        if any("not writable" in issue.lower() for issue in critical_issues):
            recommendations.extend([
                "Fix permissions: chmod -R 755 .docrag/",
                "Run 'docrag fix-database' to repair permissions"
            ])
        
        if any("low disk space" in issue.lower() for issue in critical_issues):
            recommendations.append("Free up disk space before continuing")
        
        if "Vector database not created" in str(warnings):
            recommendations.append("Run 'docrag index' to create vector database")
        
        if not recommendations:
            recommendations.append("Run 'docrag doctor' for detailed diagnostics")
        
        return recommendations