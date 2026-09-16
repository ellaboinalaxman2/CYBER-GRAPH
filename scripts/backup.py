import sys
import os
import json
import subprocess
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mongodb.config.connection import mongodb_connection
from neo4j.config.connection import neo4j_connection

def backup_databases(backup_dir: str = "backups"):
    """Backup MongoDB and Neo4j databases"""
    
    print("=" * 60)
    print("Backing up databases")
    print("=" * 60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, timestamp)
    os.makedirs(backup_path, exist_ok=True)
    
    # Backup MongoDB
    try:
        settings = mongodb_connection.settings
        mongodb_backup_path = os.path.join(backup_path, "mongodb")
        os.makedirs(mongodb_backup_path, exist_ok=True)
        
        # Export MongoDB data
        cmd = [
            "mongodump",
            "--host", settings.host,
            "--port", str(settings.port),
            "--db", settings.database,
            "--out", mongodb_backup_path
        ]
        
        if settings.username and settings.password:
            cmd.extend(["--username", settings.username])
            cmd.extend(["--password", settings.password])
            cmd.extend(["--authenticationDatabase", "admin"])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ MongoDB backup saved to: {mongodb_backup_path}")
        else:
            print(f"❌ MongoDB backup failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ MongoDB backup error: {e}")
    
    # Backup Neo4j (using dump)
    try:
        settings = neo4j_connection.settings
        neo4j_backup_path = os.path.join(backup_path, "neo4j")
        os.makedirs(neo4j_backup_path, exist_ok=True)
        
        # Export Neo4j data using cypher-shell
        dump_query = """
        CALL apoc.export.json.all($path, {})
        """
        # Note: Requires APOC plugin installed
        
        print("ℹ️ Neo4j backup requires APOC plugin or using neo4j-admin dump")
        
        # Alternative: Use neo4j-admin
        cmd = [
            "neo4j-admin", "dump",
            "--database", settings.database,
            "--to", os.path.join(neo4j_backup_path, f"{settings.database}.dump")
        ]
        
        # result = subprocess.run(cmd, capture_output=True, text=True)
        # if result.returncode == 0:
        #     print(f"✅ Neo4j backup saved to: {neo4j_backup_path}")
        # else:
        #     print(f"❌ Neo4j backup failed: {result.stderr}")
        
        print(f"ℹ️ Neo4j backup not implemented in this script.")
        print(f"   Please use: neo4j-admin dump --database={settings.database} --to={neo4j_backup_path}")
        
    except Exception as e:
        print(f"❌ Neo4j backup error: {e}")
    
    # Save backup metadata
    metadata = {
        "timestamp": timestamp,
        "backup_path": backup_path,
        "mongodb": {
            "host": mongodb_connection.settings.host,
            "port": mongodb_connection.settings.port,
            "database": mongodb_connection.settings.database
        },
        "neo4j": {
            "host": neo4j_connection.settings.host,
            "port": neo4j_connection.settings.port,
            "database": neo4j_connection.settings.database
        }
    }
    
    with open(os.path.join(backup_path, "metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✅ Backup complete. Metadata saved to: {os.path.join(backup_path, 'metadata.json')}")
    return backup_path

def restore_database(backup_path: str):
    """Restore database from backup"""
    
    print("=" * 60)
    print("Restoring databases")
    print("=" * 60)
    
    metadata_file = os.path.join(backup_path, "metadata.json")
    if not os.path.exists(metadata_file):
        print(f"❌ Metadata file not found: {metadata_file}")
        return False
    
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    # Restore MongoDB
    mongodb_backup = os.path.join(backup_path, "mongodb")
    if os.path.exists(mongodb_backup):
        try:
            settings = mongodb_connection.settings
            cmd = [
                "mongorestore",
                "--host", settings.host,
                "--port", str(settings.port),
                "--db", settings.database,
                mongodb_backup
            ]
            
            if settings.username and settings.password:
                cmd.extend(["--username", settings.username])
                cmd.extend(["--password", settings.password])
                cmd.extend(["--authenticationDatabase", "admin"])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ MongoDB restored from: {mongodb_backup}")
            else:
                print(f"❌ MongoDB restore failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ MongoDB restore error: {e}")
    
    # Restore Neo4j (using load)
    neo4j_backup = os.path.join(backup_path, "neo4j")
    if os.path.exists(neo4j_backup):
        try:
            settings = neo4j_connection.settings
            dump_file = os.path.join(neo4j_backup, f"{settings.database}.dump")
            
            if os.path.exists(dump_file):
                cmd = [
                    "neo4j-admin", "load",
                    "--database", settings.database,
                    "--from", dump_file
                ]
                
                # result = subprocess.run(cmd, capture_output=True, text=True)
                # if result.returncode == 0:
                #     print(f"✅ Neo4j restored from: {dump_file}")
                # else:
                #     print(f"❌ Neo4j restore failed: {result.stderr}")
                
                print(f"ℹ️ Neo4j restore not implemented in this script.")
                print(f"   Please use: neo4j-admin load --database={settings.database} --from={dump_file}")
            else:
                print(f"⚠️ Neo4j dump file not found: {dump_file}")
                
        except Exception as e:
            print(f"❌ Neo4j restore error: {e}")
    
    print("\n✅ Restore complete")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "backup":
            backup_dir = sys.argv[2] if len(sys.argv) > 2 else "backups"
            backup_databases(backup_dir)
        elif action == "restore":
            if len(sys.argv) > 2:
                restore_database(sys.argv[2])
            else:
                print("Usage: python backup.py restore <backup_path>")
        else:
            print("Usage: python backup.py [backup|restore]")
    else:
        print("Usage: python backup.py [backup|restore]")