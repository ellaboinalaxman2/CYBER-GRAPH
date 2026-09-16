┌─────────────────────────────────────────────────────────────────────────┐
│                         Neo4j Scaling Options                          │
│                                                                         │
│  1. Causal Clustering: Multi-master                                    │
│     - Core Servers: 3+                                                 │
│     - Read Replicas: Multiple                                          │
│     - Automatic failover                                               │
│                                                                         │
│  2. Fabric: Distributed Graph                                          │
│     - Shard by domain                                                  │
│     - Cross-database queries                                           │
│                                                                         │
│  3. Memory Optimization                                                │
│     - Page cache size                                                  │
│     - Heap size                                                        │
│     - Query cache                                                      │
└─────────────────────────────────────────────────────────────────────────┘