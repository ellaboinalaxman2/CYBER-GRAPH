# Verify MongoDB backup
mongorestore --dryRun --nsInclude=cyber_graph.* /backups/mongodb/

# Verify Neo4j backup
neo4j-admin load --database=neo4j --from=/backups/neo4j/neo4j.dump --dry-runs