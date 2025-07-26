# embed.py
import chunk
import chromadb
import google.generativeai as genai
import os

# 设置代理 - 根据你的Clash配置调整端口
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'


google_client = genai
EMBEDDING_MODEL = "gemini-embedding-exp-03-07"
LLM_MODEL = "gemini-2.5-flash-preview-05-20"

chromadb_client = chromadb.PersistentClient("./chroma.db")
chromadb_collection = chromadb_client.get_or_create_collection("linghuchong")

def embed(text: str, store: bool) -> list[float]:
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        task_type="retrieval_document" if store else "retrieval_query"
    )
    
    # 直接返回嵌入向量
    return result['embedding']

def create_db() -> None:
    for idx, c in enumerate(chunk.get_chunks()):
        print(f"Process: {c}")
        embedding = embed(c, store=True)
        chromadb_collection.upsert(
            ids=str(idx),
            documents=c,
            embeddings=embedding
        )

def query_db(question: str) -> list[str]:
    question_embedding = embed(question, store=False)
    result = chromadb_collection.query(
        query_embeddings=question_embedding,
        n_results=5
    )
    assert result["documents"]
    return result["documents"][0]


if __name__ == '__main__':
    question = "令狐冲领悟了什么魔法？"
    # create_db()
    chunks = query_db(question)
    prompt = "Please answer user's question according to context\n"
    prompt += f"Question: {question}\n"
    prompt += "Context:\n"
    for c in chunks:
        prompt += f"{c}\n"
        prompt += "-------------\n"
    print(prompt)
    
    result = genai.GenerativeModel(LLM_MODEL).generate_content(prompt)
    print(result.text)