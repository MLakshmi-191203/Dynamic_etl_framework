# PROJECT SUMMARY  

## **Dynamic ETL Framework + Schema Drift Detection + AI-powered RAG Assistant**

A system that automatically loads data, tracks schema changes, and allows users to ask questions about data using AI.

---

#  ARCHITECTURE OVERVIEW  

## 🔹 ETL Layer  
**Reads data from:**  
- CSV  
- MySQL  

**Loads into:**  
- PostgreSQL  

---

## 🔹 Metadata + Schema Tracking Layer  
**Captures:**  
- Column names  
- Data types  
- Column order  

**Detects:**  
- ADD  
- REMOVE  
- MODIFY  

---

## 🔹 AI (RAG) Layer  
- Converts metadata → embeddings  
- Stores vectors in FAISS  
- Uses LLM (Ollama) to answer questions  

---

# ⚙️ COMPLETE FLOW (STEP BY STEP)

## **STEP 1: Read Config (Dynamic Control)**  
**File:** `config_reader.py`  

Reads from:  
- `dyn_etl.process_control`  

Defines:  
- Source type (CSV / MySQL)  
- File path / table  
- Target table  
- Primary key  

➡️ Makes the pipeline fully dynamic  

---

## **STEP 2: Load Source Data**  
**File:** `source_loader.py`  

- CSV → `pandas.read_csv()`  
- MySQL → `SELECT *`  

**Output:**  
- DataFrame (`df`)  

---

## **STEP 3: Schema Extraction**  
**File:** `schema_engine.py`  

Extracts:  
- column_name  
- data_type  
- ordinal_position  

---

## **STEP 4: Metadata Validation (CORE LOGIC)**  
**File:** `schema_validation.py`  

**Logic:**  
- First Run → Store schema  
- Next Runs → Compare with metadata  

**Detects:**  
- ADD column  
- REMOVE column  
- MODIFY datatype  

---

## **STEP 5: Store Metadata**  
**Table:** `dyn_etl.metadata`  

Stores:  
- Column details  
- Action type  
- Timestamp  

➡️ Enables **data lineage + schema history**

---

## **STEP 6: Create Target Table**  
**File:** `target_loader.py`  

- Dynamically creates table  
- Uses: `CREATE TABLE IF NOT EXISTS`  

---

## **STEP 7: Load Data (UPSERT)**  

Uses:  
```sql
ON CONFLICT DO UPDATE

➡️ Handles insert + update in one query

STEP 8: Audit Logging

File: audit.py

Stores:

Start time
End time
Insert count
Update count
Status

Table:

dyn_etl.process_control_details
🤖 AI (RAG) FLOW
STEP 9: Convert Metadata → Text

File: embed_metadata.py

Example:

Table: CUSTOMERS  
Column: age  
Type: int  
Action: ADD  
STEP 10: Create Embeddings

File: embedder.py

Uses:

Ollama
Model: nomic-embed-text

➡️ Converts text → vectors

STEP 11: Store in FAISS

File: vector_store.py

Fast similarity search
Finds closest matching data
STEP 12: Retrieve Context

File: retriever.py

Converts query → embedding
Finds similar metadata
STEP 13: Generate Answer

File: rag_pipeline.py

Uses:

Ollama (llama3)

Combines:

User question
Retrieved metadata

➡️ Generates final answer

STEP 14: Chat Interface

File: run_rag.py

💡 AI-powered RAG chatbot inside Streamlit UI

🖥️ UI PREVIEW
🏠 Home
<img width="1622" height="732" src="https://github.com/user-attachments/assets/db05f5d7-473b-45f2-98ab-32eb0855f774" />
⚙️ Config
<img width="1854" height="805" src="https://github.com/user-attachments/assets/e635df2b-60f1-439b-bf7e-39759777b169" />
📅 Scheduler
<img width="1859" height="718" src="https://github.com/user-attachments/assets/ec0d6238-44d3-4724-9286-c49317205bcc" />
🤖 Ask AI
<img width="1919" height="762" src="https://github.com/user-attachments/assets/65b8b496-9bf1-4541-a178-ebc739a7e7a9" />
🧰 TECHNOLOGIES USED
🔹 Data Engineering
Python
Pandas
PostgreSQL
MySQL
🔹 ETL Concepts
Dynamic pipeline
Incremental loading
Upsert logic
Schema drift detection
🔹 AI / ML
Ollama (Local LLM)
Embeddings
FAISS (Vector DB)
RAG (Retrieval-Augmented Generation)
⚡ CORE MECHANISMS
1. Schema Drift Detection

Compare:

Source Schema vs Metadata Table
2. Upsert Logic
ON CONFLICT (PK) DO UPDATE
3. Embeddings
Convert text → vectors
Used for semantic search
4. FAISS Search
Finds nearest vectors
Enables similarity search
5. RAG
Retrieval + LLM
Answers based on your data (not guessing)
🚀 FUTURE ENHANCEMENTS
🔹 Level 1
Auto ALTER TABLE on schema change
Email / Slack alerts
🔹 Level 2
Real-time pipeline (Kafka + Debezium)
API-based pipeline trigger
🔹 Level 3 (Advanced)
Multi-table lineage graph
Data quality checks
AI auto SQL generator
