import re

def parse_cisi_documents(filepath):
    documents = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by .I 
    docs_raw = re.split(r'\.I \d+\n', content)
    
    # We need the IDs too, so let's find them
    ids = re.findall(r'\.I (\d+)', content)
    
    # The first split element is empty before the first .I
    docs_raw = docs_raw[1:]
    
    for doc_id, doc_text in zip(ids, docs_raw):
        doc_id = int(doc_id)
        
        # Extract title
        title_match = re.search(r'\.T\n(.*?)(?=\.[AWX]|\Z)', doc_text, re.DOTALL)
        title = title_match.group(1).replace('\n', ' ').strip() if title_match else ""
        
        # Extract abstract
        abstract_match = re.search(r'\.W\n(.*?)(?=\.[TXA]|\Z)', doc_text, re.DOTALL)
        abstract = abstract_match.group(1).replace('\n', ' ').strip() if abstract_match else ""
        
        # Extract author just in case
        author_match = re.search(r'\.A\n(.*?)(?=\.[TWX]|\Z)', doc_text, re.DOTALL)
        author = author_match.group(1).replace('\n', ' ').strip() if author_match else ""
        
        # Combine title and abstract as the document content
        full_text = f"{title} {abstract}".strip()
        
        documents[doc_id] = {
            "title": title,
            "abstract": abstract,
            "author": author,
            "content": full_text
        }
        
    return documents

def parse_queries(filepath):
    queries = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    docs_raw = re.split(r'\.I \d+\n', content)
    ids = re.findall(r'\.I (\d+)', content)
    docs_raw = docs_raw[1:]
    
    for q_id, q_text in zip(ids, docs_raw):
        q_id = int(q_id)
        
        # Extract text (.W)
        text_match = re.search(r'\.W\n(.*?)(?=\.[ITAWXB]|\Z)', q_text, re.DOTALL)
        text = text_match.group(1).replace('\n', ' ').strip() if text_match else ""
        
        queries[q_id] = text
        
    return queries

def parse_qrels(filepath):
    qrels = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                q_id = int(parts[0])
                doc_id = int(parts[1])
                
                if q_id not in qrels:
                    qrels[q_id] = set()
                qrels[q_id].add(doc_id)
                
    return qrels
