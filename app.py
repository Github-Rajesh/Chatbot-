# import os
# from flask import Flask, request, jsonify, send_from_directory
# from googleapiclient.discovery import build

# from langchain.document_loaders import PyPDFLoader
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.vectorstores import Chroma
# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferMemory
# from langchain.llms import OpenAI

# app = Flask(__name__, static_folder='static', static_url_path='')

# class Chatbot:
#     def __init__(self, openai_api_key, youtube_api_key, pdf_paths, persist_directory="."):
#         # Set up API keys
#         os.environ['OPENAI_API_KEY'] = 'sk-proj-qCjFX7O6TDU05Rmdu5e6T3BlbkFJvN6unZxMEeteFRZdF3ty'
#         self.youtube_api_key = 'AIzaSyBPa-kAp-11fob7q7qZdAHCXGN3Tx444XQ'

#         # Load PDF documents
#         self.pages = []
#         for path in pdf_paths:
#             loader = PyPDFLoader(path)
#             self.pages.extend(loader.load_and_split())

#         # Initialize embeddings and create vector database
#         self.embeddings = OpenAIEmbeddings()
#         self.vectordb = Chroma.from_documents(self.pages, embedding=self.embeddings, persist_directory=persist_directory)
#         self.vectordb.persist()

#         # Initialize memory
#         self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

#         # Create conversational retrieval chain
#         self.pdf_qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0.9),
#                                                            self.vectordb.as_retriever(), memory=self.memory)

#     def fetch_videos_from_youtube(self, query):
#         youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
#         request = youtube.search().list(q=query, part='snippet', type='video', maxResults=5)
#         response = request.execute()
#         videos = []
#         for item in response['items']:
#             video = {
#                 'title': item['snippet']['title'],
#                 'description': item['snippet']['description'],
#                 'thumbnail': item['snippet']['thumbnails']['default']['url'],
#                 'video_id': item['id']['videoId'],
#                 'channel_title': item['snippet']['channelTitle']
#             }
#             videos.append(video)
#         return videos

#     def ask_question(self, query):
#         # Get answer from PDF QA model
#         result = self.pdf_qa({'question': query})
        
#         # Fetch recommended videos from YouTube
#         videos = self.fetch_videos_from_youtube(result["answer"])

#         return result['answer'], videos

# @app.route('/')
# def index():
#     return send_from_directory('static', 'chat.html')

# @app.route('/ask', methods=['POST'])
# def ask_question():
#     data = request.json
#     query = data.get('question')
    
#     if not query:
#         return jsonify({'error': 'Question is required'}), 400
    
#     answer, videos = chatbot.ask_question(query)
    
#     return jsonify({'answer': answer, 'videos': videos})

# if __name__ == "__main__":
#     openai_api_key = 'sk-proj-qCjFX7O6TDU05Rmdu5e6T3BlbkFJvN6unZxMEeteFRZdF3ty'
#     youtube_api_key = 'IzaSyC_H_SMC9CMXkjxN--xrscpwciPytsciEQ'
#     pdf_paths = ["Artical2.pdf", "Artical4.pdf", "Artical5.pdf", "Artical6.pdf"]

#     chatbot = Chatbot(openai_api_key, youtube_api_key, pdf_paths)

#     app.run(host='0.0.0.0', port=5000)


import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from googleapiclient.discovery import build

from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, static_folder='static', static_url_path='')

class Chatbot:
    def __init__(self, openai_api_key, youtube_api_key, pdf_paths, persist_directory="."):
        # Set up API keys
        os.environ['OPENAI_API_KEY'] = openai_api_key
        self.youtube_api_key = youtube_api_key

        # Load PDF documents
        self.pages = []
        for path in pdf_paths:
            loader = PyPDFLoader(path)
            self.pages.extend(loader.load_and_split())

        # Initialize embeddings and create vector database
        self.embeddings = OpenAIEmbeddings()
        self.vectordb = Chroma.from_documents(self.pages, embedding=self.embeddings, persist_directory=persist_directory)
        self.vectordb.persist()

        # Initialize memory
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Create conversational retrieval chain
        self.pdf_qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0.9),
                                                           self.vectordb.as_retriever(), memory=self.memory)

    def fetch_videos_from_youtube(self, query):
        youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
        request = youtube.search().list(q=query, part='snippet', type='video', maxResults=5)
        response = request.execute()
        videos = []
        for item in response['items']:
            video = {
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'thumbnail': item['snippet']['thumbnails']['default']['url'],
                'video_id': item['id']['videoId'],
                'channel_title': item['snippet']['channelTitle']
            }
            videos.append(video)
        return videos

    def ask_question(self, query):
        logging.debug(f"Received question: {query}")
        # Get answer from PDF QA model
        result = self.pdf_qa({'question': query})
        
        # Fetch recommended videos from YouTube
        videos = self.fetch_videos_from_youtube(query)

        logging.debug(f"Answer: {result['answer']}")
        logging.debug(f"Videos: {videos}")

        return result['answer'], videos

@app.route('/')
def index():
    return send_from_directory('static', 'chat.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.json
        query = data.get('question')
        
        if not query:
            return jsonify({'error': 'Question is required'}), 400
        
        logging.debug(f"Question received at /ask endpoint: {query}")
        answer, videos = chatbot.ask_question(query)
        
        return jsonify({'answer': answer, 'videos': videos})
    except Exception as e:
        logging.error(f"Error processing question: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    openai_api_key = 'api key'
    youtube_api_key = 'api key'
    pdf_paths = ["0004-24ESE11.pdf", "0099-24ES.pdf", "0100-24JSH.pdf"]

    chatbot = Chatbot(openai_api_key, youtube_api_key, pdf_paths)

    app.run(host='0.0.0.0', port=5000)
