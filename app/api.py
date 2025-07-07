from dotenv import load_dotenv

load_dotenv()
import re
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from groq import Client
from fastapi.encoders import jsonable_encoder
import json
from langchain_community.llms import Ollama


router = APIRouter()


class QueryRequest(BaseModel):
    question: str


# Fonction de nettoyage du texte
def clean_text(text):
    text = re.sub(
        r"\s+", " ", text
    )  # Suppression des espaces et sauts de ligne excessifs
    return text.strip()  # Suppression des espaces en début/fin


# Liste des documents juridiques à indexer
documents = [
    {
        "path": "app\documents\Article-TAYAA 16oct19.pdf",
        "title": "Diagnostic et prise en charge de la dépression chez lesujet âgé",
    },
    {
        "path": "app\documents\BAT-Depression-check_21.02.22.pdf",
        "title": "Mieux vivre avec la dépression",
    },
    {
        "path": "app\documents\digno.pdf",
        "title": "Diagnostic en psychiatrie adulte Mieux comprendre et être accompagné",
    },
    {
        "path": "app\documents\map_enfants_2008.pdf",
        "title": "Le bon usage des antidépresseurs chez l’enfant et l’adolescent",
    },
    {
        "path": "app\documents\PSYCOM_Brochures-A5_TP_Troubles-depressifs_2025_WEB.pdf",
        "title": "Troubles dépressifs TROUBLES PSYCHIQUES",
    },
    
    # Ajouter d'autres documents ici...
]


# Initialisation de la liste des documents traités
all_docs = []


# Chargement et traitement des documents
for doc in documents:
    pdf_path = doc["path"]
    title = doc["title"]

    if not os.path.exists(pdf_path):
        print(f"⚠️ Attention : {pdf_path} non trouvé, il sera ignoré.")
        continue

    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    for page_num, page in enumerate(pages):
        cleaned_text = clean_text(page.page_content)
        all_docs.append(
            {
                "text": cleaned_text,
                "metadata": {"source": pdf_path, "title": title, "page": page_num + 1},
            }
        )


# Découpage du texte en chunks avec inclusion des métadonnées
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = [
    (chunk, doc["metadata"])
    for doc in all_docs
    for chunk in text_splitter.split_text(doc["text"])
]


# Création d'objets Documents avec métadonnées
from langchain.schema import Document

final_docs = [
    Document(page_content=chunk, metadata=metadata) for chunk, metadata in docs
]


# Chargement du modèle d'embeddings
persist_directory = "MyVectorDB1.0"
embedding_function = HuggingFaceEmbeddings(
    model_name="sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
)


# Création ou chargement de la base Chroma avec métadonnées
vectorstore = Chroma.from_documents(
    final_docs, embedding_function, persist_directory=persist_directory
)


# Configuration de la clé API Groq
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("La clé API GROQ_API_KEY n'est pas définie.")


client = Client(api_key=api_key)


# Initialisation du modèle Groq
groq_llm = ChatGroq(model_name="llama-3.3-70b-versatile")
# ollama_llm = Ollama(model="mistral")


# Définition du prompt personnalisé
template =  """
Tu es un **Psychiatre spécialisé en troubles de l’humeur**.  
Ton rôle :  
1. **Recueillir** : Âge, sexe, antécédents médicaux/familiaux.  
2. **Évaluer** : Symptômes (critères DSM-5/ICD-10), durée, impact sur la vie quotidienne.  
3. **Diagnostiquer** : Dépression légère/moderée/sévère, trouble bipolaire, etc.  
4. **Orienter** : Vers un psychiatre en présentiel si risque suicidaire ou cas complexe.  

### **Contexte Scientifique** :  
{context}  

### **Historique Conversationnel** :  
{chat_history}  

### **Patient** : {question}  

### **Réponse Structurée** (en Markdown) :  
1. **Évaluation** :  
   - Symptômes clés : [liste]  
   - Échelle PHQ-9/GAD-7 (si applicable) : [score estimé]  
2. **Hypothèse Diagnostique** :  
   - [Diagnostic préliminaire + critères]  
3. **Recommandations** :  
   - Consultation en présentiel : [Oui/Non]  
   - Ressources : [Lignes d’écoute, centres spécialisés]  
4. **Disclaimer** : *"Ceci n’est pas un avis médical définitif. Consultez un professionnel."*  
"""


prompt_template = PromptTemplate(
    input_variables=["history", "context", "question"],
    template=template,
)


# Initialisation de la mémoire de conversation
memory = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True, input_key="question"
)


# Création de la chaîne QA avec mémoire et récupération des sources
qa_chain = RetrievalQA.from_chain_type(
    llm=groq_llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),  # Récupération des 5 documents les plus pertinents
    return_source_documents=True,
    verbose=True,
    chain_type_kwargs={"prompt": prompt_template, "memory": memory, "verbose": True}
)


@router.post("/chatPsy")
def chat(request: QueryRequest):
    try:
        response = qa_chain({"query": request.question})  # Exécute la requête
        answer = response["result"]

        # 🔍 Debugging: Afficher les sources
        print("🔍 Raw source documents:", response["source_documents"])

        # Extraction des sources avec métadonnées
        sources = []
        for doc in response["source_documents"]:
            print(
                "📝 Metadata:", doc.metadata
            )  # Debugging : voir les métadonnées réelles
            sources.append(
                {
                    "source": doc.metadata.get("source", "Inconnu"),
                    "title": doc.metadata.get("title", "Inconnu"),
                    "page": doc.metadata.get("page", "Inconnue"),
                }
            )

        # 🔍 Debugging: Afficher la structure des sources avant retour
        print(
            "✅ Formatted sources:", json.dumps(sources, indent=2, ensure_ascii=False)
        )

        return jsonable_encoder({"response": answer, "sources": sources})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
