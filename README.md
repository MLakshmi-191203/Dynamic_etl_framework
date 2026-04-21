**PROJECT SUMMARY**  

**Dynamic ETL Framework + Schema Drift Detection + AI-powered RAG Assistant** 
A system that automatically loads data, tracks schema changes, and allows users to ask questions about data using AI.  

**ARCHITECTURE OVERVIEW** 
ETL Layer Reads data from: <br>
  CSV <br>
  MySQL <br>
Loads into: PostgreSQL<br>
**Metadata + Schema Tracking Layer** <br>
Captures: oColumn names Data types <br>
Order Detects: <br>
ADD / REMOVE / MODIFY <br>
**AI (RAG) Layer** <br>
Converts metadata → embeddings Stores in FAISS Uses LLM (Ollama) to answer questions <br>
**COMPLETE FLOW (STEP BY STEP)** **STEP 1: Read Config (Dynamic Control)** <br>
**File**: config_reader.py<br>
**Reads from:** dyn_etl.process_control <br>
Defines: <br>
Source type (CSV / MySQL) File path /<br>
table Target table Primary key This makes pipeline fully dynamic<br>
**STEP 2: Load Source Data**<br>
File: source_loader.py CSV → pandas.read_csv() <br>
MySQL → SELECT * <br>
**Output**: <br>
DataFrame (df) <br>
**STEP 3: Schema Extraction**<br>
**File**: schema_engine.py <br>
**Extracts**: column_name data_type ordinal_position <br>
**STEP 4: Metadata Validation (CORE LOGIC)** <br>
**File**: schema_validation.py <br>
**Logic**: First Run: No metadata → store schema Next Runs: Compare with existing metadata<br>
**Detect**: ADD column REMOVE column MODIFY datatype <br>
**STEP 5: Store Metadata** **Table**: dyn_etl.metadata <br>
**Stores**: Column details Action type Timestamp This is your data lineage + schema history <br>
**STEP 6: Create Target Table** **File**: target_loader.py <br>
**Creates dynamically**: CREATE TABLE IF NOT EXISTS Based on DataFrame columns <br>
**STEP 7: Load Data (UPSERT)** **Uses**: ON CONFLICT DO UPDATE Insert + Update in one query<br>
**STEP 8: Audit Logging**<br>
**File**: audit.py <br>
**Stores**: Start time End time Insert count Update count Status <br>
**Table**: dyn_etl.process_control_details <br>
**AI (RAG) FLOW** <br>
**STEP 9: Convert Metadata → Text** embed_metadata.py <br>
Example: Table: CUSTOMERS Column: age <br>
Type: int <br>
Action: ADD <br>
**STEP 10: Create Embeddings** embedder.py <br>
Uses: Ollama Model: nomic-embed-text <br>
Converts text → vector (numbers) <br>
**STEP 11: Store in FAISS** vector_store.py FAISS: Fast similarity search Finds closest matching data <br>
**STEP 12: Retrieve Context** retriever.py Converts <br>
query → embedding Finds similar metadata<br>
**STEP 13: Generate Answer** rag_pipeline.py Uses: Ollama (llama3) Combines: oUser question oRetrieved metadata Generates final answer <br>
**STEP 14: Chat Interface** run_rag.py <br>
**AI-powered RAG chatbot (inside a UI)** home.py <br>
<img width="1622" height="732" alt="image" src="https://github.com/user-attachments/assets/db05f5d7-473b-45f2-98ab-32eb0855f774" /> <br>
Config.py <br>
<img width="1854" height="805" alt="image" src="https://github.com/user-attachments/assets/e635df2b-60f1-439b-bf7e-39759777b169" /> <br>
Scheduler.py <br>
<img width="1859" height="718" alt="image" src="https://github.com/user-attachments/assets/ec0d6238-44d3-4724-9286-c49317205bcc" /> <br>
Ask ai.py <img width="1919" height="762" alt="image" src="https://github.com/user-attachments/assets/65b8b496-9bf1-4541-a178-ebc739a7e7a9" /> <br>
**TECHNOLOGIES USED** **Data Engineering** <br>
Python Pandas PostgreSQL MySQL <br>
**ETL Concepts** Dynamic pipeline Incremental loading Upsert logic Schema drift detection <br>
**AI / ML** Ollama (Local LLM) Embeddings FAISS (Vector DB) RAG (Retrieval-Augmented Generation) <br>
**CORE MECHANISMS** <br>
**1. Schema Drift Detection** <br>
**Compare**: Source Schema vs Metadata Table <br>
**2. Upsert Logic** ON CONFLICT (PK) DO UPDATE <br>
**3. Embeddings** Convert text → vectors Used for similarity search <br>
**4. FAISS Search** Finds nearest vectors (semantic search)<br>
**5. RAG** Retrieval + LLM Instead of guessing, model answers based on your data <br>
**FUTURE ENHANCEMENTS** <br>
**Level 1** Auto ALTER TABLE on schema change Email/Slack alerts<br>
**Level 2** Real-time pipeline (Kafka + Debezium) API-based pipeline trigger<br>
**Level 3 (Advanced)** Multi-table lineage graph Data quality checks AI auto SQL generator<br>
