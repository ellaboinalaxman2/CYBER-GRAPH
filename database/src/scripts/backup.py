"""Backup script for MongoDB and Neo4j."""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
import shutil

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import BackupError


class BackupManager:
    """
    Manages database backups.
    
    Features:
    - MongoDB backup using mongodump
    - Neo4j backup (JSON export)
    - Restore from backup
    - Backup rotation
    """
    
    def __init__(self, backup_dir: Optional[str] = None):
        """
        Initialize the backup manager.
        
        Args:
            backup_dir: Directory to store backups
        """
        self.logger = get_logger("scripts.backup")
        self.backup_dir = Path(backup_dir or settings.backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def backup_mongodb(self) -> Dict[str, Any]:
        """
        Backup MongoDB database.
        
        Returns:
            Dict[str, Any]: Backup results
        """
        self.logger.info("Starting MongoDB backup...")
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"mongodb_{timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Use mongodump for backup
            cmd = [
                "mongodump",
                "--uri", settings.mongodb_uri,
                "--db", settings.mongodb_db,
                "--out", str(backup_path),
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Create metadata
                metadata = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "database": settings.mongodb_db,
                    "type": "mongodb",
                    "size_bytes": self._get_dir_size(backup_path),
                }
                
                with open(backup_path / "metadata.json", "w") as f:
                    json.dump(metadata, f, indent=2)
                
                self.logger.info(f"MongoDB backup completed: {backup_path}")
                return {
                    "status": "success",
                    "path": str(backup_path),
                    "metadata": metadata,
                }
            else:
                self.logger.error(f"MongoDB backup failed: {result.stderr}")
                return {
                    "status": "failed",
                    "error": result.stderr,
                }
                
        except FileNotFoundError:
            error = "mongodump not found. Please install MongoDB tools."
            self.logger.error(error)
            return {"status": "failed", "error": error}
        except Exception as e:
            self.logger.error(f"MongoDB backup failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def backup_neo4j(self) -> Dict[str, Any]:
        """
        Backup Neo4j graph (export to JSON).
        
        Returns:
            Dict[str, Any]: Backup results
        """
        self.logger.info("Starting Neo4j backup...")
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"neo4j_{timestamp}.json"
        
        try:
            from src.neo4j.connection import neo4j
            
            # Export all nodes
            nodes_query = "MATCH (n) RETURN n"
            nodes_result = neo4j.execute_query(nodes_query)
            nodes = [r.get("n", {}) for r in nodes_result]
            
            # Export all relationships
            rels_query = "MATCH ()-[r]->() RETURN r"
            rels_result = neo4j.execute_query(rels_query)
            relationships = [r.get("r", {}) for r in rels_result]
            
            # Create backup data
            backup_data = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "type": "neo4j",
                "nodes": nodes,
                "relationships": relationships,
                "node_count": len(nodes),
                "relationship_count": len(relationships),
            }
            
            with open(backup_path, "w") as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            self.logger.info(f"Neo4j backup completed: {backup_path}")
            return {
                "status": "success",
                "path": str(backup_path),
                "metadata": {
                    "timestamp": backup_data["timestamp"],
                    "type": "neo4j",
                    "node_count": backup_data["node_count"],
                    "relationship_count": backup_data["relationship_count"],
                },
            }
            
        except Exception as e:
            self.logger.error(f"Neo4j backup failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def restore_mongodb(self, backup_path: str) -> Dict[str, Any]:
        """
        Restore MongoDB from backup.
        
        Args:
            backup_path: Path to backup directory
            
        Returns:
            Dict[str, Any]: Restore results
        """
        self.logger.info(f"Restoring MongoDB from {backup_path}...")
        
        try:
            cmd = [
                "mongorestore",
                "--uri", settings.mongodb_uri,
                "--db", settings.mongodb_db,
                str(backup_path),
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("MongoDB restore completed")
                return {"status": "success"}
            else:
                self.logger.error(f"MongoDB restore failed: {result.stderr}")
                return {"status": "failed", "error": result.stderr}
                
        except Exception as e:
            self.logger.error(f"MongoDB restore failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def restore_neo4j(self, backup_path: str) -> Dict[str, Any]:
        """
        Restore Neo4j from JSON backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            Dict[str, Any]: Restore results
        """
        self.logger.info(f"Restoring Neo4j from {backup_path}...")
        
        try:
            from src.neo4j.connection import neo4j
            from src.neo4j.repositories.node_repository import NodeRepository
            from src.neo4j.repositories.graph_repository import GraphRepository
            
            with open(backup_path, "r") as f:
                backup_data = json.load(f)
            
            # Clear existing graph
            neo4j.execute_query("MATCH (n) DETACH DELETE n")
            
            node_repo = NodeRepository()
            graph_repo = GraphRepository()
            
            # Restore nodes
            for node in backup_data.get("nodes", []):
                node_id = node.get("id")
                node_type = node.get("type", "UNKNOWN")
                properties = {k: v for k, v in node.items() if k not in ["id", "type"]}
                node_repo.create_node(node_id, node_type, properties)
            
            # Restore relationships
            for rel in backup_data.get("relationships", []):
                source = rel.get("id")
                target = rel.get("id")
                rel_type = rel.get("type", "CONNECTS_TO")
                properties = {k: v for k, v in rel.items() if k not in ["id", "type"]}
                graph_repo.create_relationship(source, target, rel_type, properties)
            
            self.logger.info("Neo4j restore completed")
            return {"status": "success"}
            
        except Exception as e:
            self.logger.error(f"Neo4j restore failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def _get_dir_size(self, path: Path) -> int:
        """Calculate directory size in bytes."""
        total = 0
        for entry in path.rglob("*"):
            if entry.is_file():
                total += entry.stat().st_size
        return total
    
    def cleanup_old_backups(self, keep_days: int = 7) -> Dict[str, Any]:
        """
        Remove backups older than specified days.
        
        Args:
            keep_days: Number of days to keep
            
        Returns:
            Dict[str, Any]: Cleanup results
        """
        self.logger.info(f"Cleaning backups older than {keep_days} days...")
        
        deleted = []
        current_time = datetime.utcnow().timestamp()
        
        for item in self.backup_dir.iterdir():
            if item.is_dir():
                # Check modification time
                mtime = item.stat().st_mtime
                age_days = (current_time - mtime) / (24 * 60 * 60)
                
                if age_days > keep_days:
                    try:
                        shutil.rmtree(item)
                        deleted.append(str(item))
                        self.logger.info(f"Deleted old backup: {item}")
                    except Exception as e:
                        self.logger.error(f"Failed to delete {item}: {e}")
        
        return {
            "status": "success",
            "deleted_count": len(deleted),
            "deleted": deleted,
        }


if __name__ == "__main__":
    # Run backup
    manager = BackupManager()
    
    print("Starting backup...")
    mongodb_result = manager.backup_mongodb()
    neo4j_result = manager.backup_neo4j()
    
    print(f"MongoDB: {mongodb_result['status']}")
    print(f"Neo4j: {neo4j_result['status']}")