
# Content Plan

## Sprint 1 (Week of 8.4)

### sqlite-sync
- **Quickstart Repo**: 
  - Run 1 command to download the appropriate extension, install, setup dbs, and spin up docker containers. 
  - Write to one db via cli and see the change reflected in the other terminal.
  - Simple SyncClient implementation
  - Conceptual overview and tutorial

### sqlite-ai
- **Fix Current Issues**
  - README Error: Line 45 says "SQLite Sync" instead of "SQLite-AI"
  - Missing Model Source: No guidance on where to get GGUF models
  - No Error Handling: Examples don't show what happens when things fail
- **Quickstart**:
  - Run 1 command and download/install appropriate extensions, demo model, and start CLI chatbot
  - Model acquisition guide
  - Conceptual overview and tutorial

### sqlite-vector
- **Quickstart Repo**:
  - Run 1 command to download/setup and spin up cli to run semantic queries against demo database
  - Hybrid FTS/metadata/semantic search implementation
  - Conceptual overview and tutorial

## Sprint 2 (Week of 8.11)
- **Local-first Chatbot Tutorial**: "Build a local-first AI chatbot in 10 minutes"
  - Architecture overview - Expand on quickstarts and show how components can work together
  - Core implementations: SyncClient, VectorMemory, and AIService
    - Embedding generation + Vector Preprocessing
    - "Memory" implementation patterns
    - Offline-first patterns
    - File ingestion
    - Sync using RLS
    - CLI and Streamlit (Web) interfaces
  - Performance tuning guide - Memory optimization, quantization decisions

