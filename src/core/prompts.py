"""Prompts e templates para o sistema de IA."""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .config import settings


# Template para contextualizar pergunta com histórico
contextualize_prompt = ChatPromptTemplate.from_messages([
    ("system", settings.AI_CONTEXTUALIZE_PROMPT),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

# Template para resposta com contexto recuperado
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", settings.AI_SYSTEM_PROMPT),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])