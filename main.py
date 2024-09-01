import streamlit as st
from langchain import hub
from langchain_chroma import Chroma 
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.prompts import ChatPromptTemplate
import tempfile
import os

# Streamlit interface
st.title("PDF Chatbot")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'pdf_processed' not in st.session_state:
    st.session_state.pdf_processed = False
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'current_file' not in st.session_state:
    st.session_state.current_file = None

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# Check if a new file is uploaded
if uploaded_file and uploaded_file != st.session_state.current_file:
    st.session_state.pdf_processed = False
    st.session_state.current_file = uploaded_file
    st.session_state.chat_history = []

# Function to process the PDF
def process_pdf(file):
    openai_api_key = "" ##  MUST ENTER OPENAI API KEY HERE
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file.getvalue())
        tmp_file_path = tmp_file.name

    loader = PyPDFLoader(tmp_file_path)
    documents = loader.load()

    text_splitter = SemanticChunker(OpenAIEmbeddings(openai_api_key=openai_api_key))
    texts = text_splitter.split_documents(documents)

    if st.session_state.vectorstore:
        st.session_state.vectorstore.delete_collection()
    st.session_state.vectorstore = Chroma.from_documents(documents=texts, embedding=OpenAIEmbeddings(openai_api_key=openai_api_key))
    
    os.unlink(tmp_file_path)
    st.session_state.pdf_processed = True

# Process PDF when uploaded
if uploaded_file and not st.session_state.pdf_processed:
    with st.spinner("Processing PDF..."):
        process_pdf(uploaded_file)
    st.success("PDF processed successfully!")

# Function to generate response
def generate_response(question):
    openai_api_key = "" ##  MUST ENTER OPENAI API KEY HERE
    llm = ChatOpenAI(openai_api_key=openai_api_key, model="gpt-4o")
    retriever = st.session_state.vectorstore.as_retriever()

    prompt = ChatPromptTemplate.from_messages([
        ("human", "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Question: {question} Context: {context} Answer:"),
    ])

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain.invoke(question)

# Chat interface
st.subheader("Chat")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about the PDF"):
    if not st.session_state.pdf_processed:
        st.warning("Please upload a PDF file first.")
    else:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_response(prompt)
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})

# Clear chat history button
if st.button("Clear Chat History"):
    st.session_state.chat_history = []
    st.session_state.pdf_processed = False
    st.session_state.current_file = None
    if st.session_state.vectorstore:
        st.session_state.vectorstore.delete_collection()
    st.session_state.vectorstore = None
    st.experimental_rerun()
