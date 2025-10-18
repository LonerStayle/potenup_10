


from dotenv import load_dotenv
load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

FAISS_INDEX_PATH = "/Users/seobi/PythonProjects/potenup_10/homework/faiss_index"
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings=embeddings, allow_dangerous_deserialization= True)
dense_retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.4})

fianl_docs_list = vectorstore.docstore._dict.values()
len(fianl_docs_list)
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
bm25_retriever = BM25Retriever.from_documents(fianl_docs_list)
hybrid_retriever = EnsembleRetriever(
    retrievers=[dense_retriever, bm25_retriever],
     weights=[0.6, 0.4]
)



question_list = [
    "타이어 펑크 시 타이어 응급 처치 키트(TMK) 사용법을 단계별로 알려줘.",
    "스마트 크루즈 컨트롤(SCC)의 주요 기능과 사용 시 주의사항을 요약해줘.",
    "주행 중 엔진이 과열되었을 때 어떻게 조치해야 하는지 순서대로 설명해줘.",
    "차량의 'N 모드'는 무엇이고, 다른 드라이브 모드(ECO, NORMAL, SPORT)와 어떻게 다른지 정리해줘.",
    "엔진 오일은 어떤 규격의 제품을 사용해야 하고, 언제 교체해야 하나요?",
]

from prompts import system_prompt

from openai import OpenAI

client = OpenAI()

for i, question in enumerate(question_list):
    menual_list = hybrid_retriever.get_relevant_documents(question)
    menual_texts = [
        f"""
        {i+1}번째 문서
        Title: {d.metadata.get('title', 'N/A')}\n
        Pages: {d.metadata.get('pages', 'N/A')}\n
        Content:\n{d.page_content.strip()}\n\n
        """
        for d in menual_list
    ]
    system_prompt.format(menual = menual_texts, question = question)
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role":"system","content":system_prompt},
            {"role":"user","content":question}
        ],
        temperature=0,
        max_tokens=500,
        top_p=1,
    )
    answer = response.choices[0].message.content.strip()
    print(f"{i+1}번째 질문: {question}")
    print(f"답변: ",answer)
    print("*"*100 + "\n")




