#!/home/sudharsan/myenv/bin/python3
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
import faiss

embeddings = OllamaEmbeddings()

def create_vector_db(url):
    try:
        loader = WebBaseLoader(url)
        transcript = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = text_splitter.split_documents(transcript)

        db = FAISS.from_documents(docs, embeddings)
        return db
    
    except Exception as e:
        raise RuntimeError(f"Failed to create vector DB: {str(e)}")

def get_response(db, query, k=8):
    try:
        docs = db.similarity_search(query, k=k)
        docs_page_content = " ".join([d.page_content for d in docs])

        llm = Ollama(model='llama2')

        prompt = PromptTemplate(
            input_variables=["question", "docs"],
            template="""you are an web assistant that can answer question about that webpage 
            Answer the following question: {question}
            by searching the webpage-content: {docs}

            give only the keypoint
            """
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run(question=query, docs=docs_page_content)
        response = response.replace("\n", "")
        return response
    
    except Exception as e:
        raise RuntimeError(f"Failed to get response: {str(e)}")

if __name__ == "__main__":
    # Example usage
    video_url = "https://www.youtube.com/watch?v=_j7JEDWuqLE"
    db = create_vector_db(video_url)
    response = get_response(db, "Title of the webpage")
    print(response)
