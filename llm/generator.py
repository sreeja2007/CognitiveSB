import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import PromptTemplate

load_dotenv()

class Generator:

    def __init__(self):

        hf_token = os.environ.get("HUGGINGFACEHUB_API_TOKEN")

        llm = HuggingFaceEndpoint(
            repo_id="meta-llama/Llama-3.1-8B-Instruct",
            task="text-generation",
            huggingfacehub_api_token=hf_token,
            max_new_tokens=512,
            temperature=0.3
        )

        self.model = ChatHuggingFace(llm=llm)

        self.prompt = PromptTemplate(
            template="""You are a helpful study assistant.
Answer strictly using the provided context.
If context is insufficient, say "I don't know based on the knowledge base."

Context:
{context}

Question:
{question}
""",
            input_variables=["context", "question"]
        )

    def generate(self, docs, question):

        context = "\n\n".join(doc.page_content for doc in docs)

        formatted_prompt = self.prompt.format(
            context=context,
            question=question
        )

        response = self.model.invoke(formatted_prompt)
        # print("----- CONTEXT SENT TO LLM -----")
        # print(context[:1500])
        # print("--------------------------------")

        return response.content
