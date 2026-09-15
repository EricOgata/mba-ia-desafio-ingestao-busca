from langchain_postgres import PGVector
from langchain_google_genai import ChatGoogleGenerativeAI
from load import load_vector

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def get_reelevant_context(question, store: PGVector, k: int = 10) -> str:
  docs = store.similarity_search(question, k=k)
  return "\n\n".join([doc.page_content for doc in docs])


def search_prompt(question=None):
    # Load PGVector context
    store = load_vector()  # Ensure the vector store is loaded before proceeding
    if not store:
        raise RuntimeError("Failed to load PGVector store. Check your database connection and collection name.")

    # Retorna contexto reelevante à pergunta:
    context = get_reelevant_context(question, store)

    llm_prompt = PROMPT_TEMPLATE.format(contexto=context, pergunta=question)

    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5);
    message = model.invoke(llm_prompt)

    if message :
      return message.content
    
    pass