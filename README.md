#PDF Chatbot
This application, built with Streamlit, leverages a combination of advanced technologies from the LangChain suite to create an interactive PDF chatbot. Users can upload PDF documents, which are then processed to facilitate natural language interactions. The application extracts content from the uploaded PDFs, enabling users to ask questions about the document through a chatbot interface.

Key Features:
- PDF Upload and Processing: Users can upload PDF files, which are then processed using semantic chunking to segment the text into manageable pieces and stored in a ChromaDB vector database.
- OpenAI LLM: Users can chat with the start of the art gpt-4o model from OpenAI
- Interactive Q&A: Once a PDF is processed, users can engage in a chat with the system, asking questions related to the document contents. Chat history is stored allowing the user to ask follow ups and get all their questions thoroughly answered.

Setup and Configuration
Users need to specify their OpenAI API key in the script to interact with the OpenAI models.
