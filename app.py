import os
from flask import Flask, render_template, request
from loaders.loader_manager import LoaderManager
from loaders.youtube_loader import YoutubeLoader
from processing.chunker import Chunker
from processing.embedder import Embedder
from retrieval.vector_store import VectorStore

app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf','txt','docx','pptx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route("/", methods=["GET", "POST"])
def index():
    message = ""

    if request.method == "POST":

        if "file" not in request.files:
            message = "No file part"
            return render_template("index.html", message=message)

        file = request.files["file"]

        if file.filename == "":
            message = "No selected file"
            return render_template("index.html", message=message)

        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            loader = LoaderManager()
            documents = loader.load(filepath)

            # Chunking
            chunker = Chunker()
            chunks = chunker.split(documents)

            # Extract text from chunks
            texts = [doc.page_content for doc in chunks]

            # Embedding
            embedder = Embedder()
            embeddings = embedder.embed_documents(texts)

            # Vector Store
            vector_store = VectorStore()
            vector_store.add(embeddings, chunks)
            vector_store.save()


            message = f"File uploaded and loaded successfully! Pages loaded: {len(documents)}"
            return render_template("index.html", message=message)

        else:
            message = "Only PDF files allowed."
            return render_template("index.html", message=message)

    return render_template("index.html", message=message)
@app.route("/query", methods=["POST"])
def query():

    from processing.embedder import Embedder
    from retrieval.vector_store import VectorStore
    from llm.generator import Generator

    user_query = request.form["query"]

    # Embed query
    embedder = Embedder()
    query_embedding = embedder.embed_documents([user_query])[0]

    # Retrieve
    vector_store = VectorStore()
    vector_store.load()

    retrieved_docs = vector_store.search(query_embedding, k=3)

    # Generate answer
    generator = Generator()
    answer = generator.generate(retrieved_docs, user_query)

    return render_template("index.html", answer=answer)
@app.route("/youtube", methods=["GET", "POST"])
def youtube():

    message = ""

    if request.method == "POST":
        url = request.form["url"]

        try:
            loader = YoutubeLoader(url)
            documents = loader.load()

            # Chunking
            chunker = Chunker()
            chunks = chunker.split(documents)

            # Extract text
            texts = [doc.page_content for doc in chunks]

            # Embedding
            embedder = Embedder()
            embeddings = embedder.embed_documents(texts)

            # Vector Store
            vector_store = VectorStore()
            vector_store.add(embeddings, chunks)
            vector_store.save()

            message = "YouTube transcript loaded successfully!"

        except Exception as e:
            message = f"Error loading YouTube transcript: {str(e)}"

    # 🔴 ALWAYS return something
    return render_template("index.html", message=message)

        
if __name__ == '__main__':
    app.run(debug=True)
