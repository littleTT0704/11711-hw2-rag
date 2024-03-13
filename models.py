from haystack import Pipeline
from haystack.schema import Document
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import (
    BM25Retriever,
    SentenceTransformersRanker,
    EmbeddingRetriever,
    PromptModel,
    AnswerParser,
)
from haystack.nodes.prompt import PromptNode
from haystack.nodes.prompt.prompt_template import PromptTemplate
from fastrag.prompters.invocation_layers.llama_cpp import LlamaCPPInvocationLayer
import torch
import os
from typing import List


def baseline(documents: List[Document], use_gpu: bool = False) -> Pipeline:
    document_store = InMemoryDocumentStore(use_gpu=use_gpu, use_bm25=True)
    document_store.write_documents(documents)
    retriever = BM25Retriever(document_store=document_store, top_k=100)

    reranker = SentenceTransformersRanker(
        model_name_or_path="cross-encoder/ms-marco-MiniLM-L-12-v2",
        top_k=1,
        use_gpu=use_gpu,
    )

    answer_parser = AnswerParser()  # pattern=r"\s+(.*)")
    lfqa_prompt = PromptTemplate(
        prompt="Answer the question using the provided context.\n\nContext: {join(documents)}\n\nQuestion: {query}\n\nAnswer (a few words or a phrase):",
        output_parser=answer_parser,
    )
    prompter = PromptNode(
        model_name_or_path="MBZUAI/LaMini-Flan-T5-783M",
        default_prompt_template=lfqa_prompt,
        model_kwargs={"model_max_length": 2048, "torch_dtype": torch.bfloat16},
        use_gpu=use_gpu,
    )

    p = Pipeline()
    p.add_node(component=retriever, name="Retriever", inputs=["Query"])
    p.add_node(component=reranker, name="Reranker", inputs=["Retriever"])
    p.add_node(component=prompter, name="prompt_node", inputs=["Reranker"])
    return p


def embed_meta(documents: List[Document], use_gpu: bool = False) -> Pipeline:
    document_store = InMemoryDocumentStore(use_gpu=use_gpu)
    document_store.write_documents(documents)

    retriever = EmbeddingRetriever(
        document_store=document_store,
        embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1",
        model_format="sentence_transformers",
        top_k=20,
        embed_meta_fields=["title"],
        use_gpu=use_gpu,
    )
    document_store.update_embeddings(retriever=retriever)

    reranker = SentenceTransformersRanker(
        model_name_or_path="cross-encoder/qnli-distilroberta-base",
        top_k=1,
        use_gpu=use_gpu,
    )

    answer_parser = AnswerParser()  # pattern=r"\s+(.*)")
    lfqa_prompt = PromptTemplate(
        prompt="Answer the question using the provided context.\n\nContext: {join(documents)}\n\nQuestion: {query}\n\nAnswer (a few words or a phrase):",
        output_parser=answer_parser,
    )
    prompter = PromptNode(
        model_name_or_path="MBZUAI/LaMini-Flan-T5-783M",
        default_prompt_template=lfqa_prompt,
        model_kwargs={"model_max_length": 2048, "torch_dtype": torch.bfloat16},
        use_gpu=use_gpu,
    )

    p = Pipeline()
    p.add_node(component=retriever, name="Retriever", inputs=["Query"])
    p.add_node(component=reranker, name="Reranker", inputs=["Retriever"])
    p.add_node(component=prompter, name="prompt_node", inputs=["Reranker"])
    return p


def squad(documents: List[Document], use_gpu: bool = False) -> Pipeline:
    document_store = InMemoryDocumentStore(use_gpu=use_gpu, use_bm25=True)
    document_store.write_documents(documents)
    retriever = BM25Retriever(document_store=document_store, top_k=100)

    reranker = SentenceTransformersRanker(
        model_name_or_path="cross-encoder/qnli-distilroberta-base",
        top_k=1,
        use_gpu=use_gpu,
    )

    answer_parser = AnswerParser()  # pattern=r"\s+(.*)")
    lfqa_prompt = PromptTemplate(
        prompt="Answer the question using the provided context.\n\nContext: {join(documents)}\n\nQuestion: {query}\n\nAnswer (a few words or a phrase):",
        output_parser=answer_parser,
    )
    prompter = PromptNode(
        model_name_or_path="MBZUAI/LaMini-Flan-T5-783M",
        default_prompt_template=lfqa_prompt,
        model_kwargs={"model_max_length": 2048, "torch_dtype": torch.bfloat16},
        use_gpu=use_gpu,
    )

    p = Pipeline()
    p.add_node(component=retriever, name="Retriever", inputs=["Query"])
    p.add_node(component=reranker, name="Reranker", inputs=["Retriever"])
    p.add_node(component=prompter, name="prompt_node", inputs=["Reranker"])
    return p


def llama_old(documents: List[Document], use_gpu: bool = False) -> Pipeline:
    document_store = InMemoryDocumentStore(use_gpu=use_gpu, use_bm25=True)
    document_store.write_documents(documents)
    retriever = BM25Retriever(document_store=document_store, top_k=100)

    reranker = SentenceTransformersRanker(
        model_name_or_path="cross-encoder/ms-marco-MiniLM-L-12-v2",
        top_k=1,
        use_gpu=use_gpu,
    )

    answer_parser = AnswerParser()  # pattern=r"\s+(.*)")
    lfqa_prompt = PromptTemplate(
        prompt="""Answer the question using the provided context.
Example:
Question: Who is teaching 11-711 in Spring 2024?

Answer: Neubig.

Context: {join(documents)}

Question: {query}

Answer: """,
        output_parser=answer_parser,
    )
    prompter = PromptNode(
        model_name_or_path="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        default_prompt_template=lfqa_prompt,
        model_kwargs={"model_max_length": 2048, "torch_dtype": torch.bfloat16},
        use_gpu=True
    )

    p = Pipeline()
    p.add_node(component=retriever, name="Retriever", inputs=["Query"])
    p.add_node(component=reranker, name="Reranker", inputs=["Retriever"])
    p.add_node(component=prompter, name="prompt_node", inputs=["Reranker"])
    return p


def llama(documents: List[Document], use_gpu=False) -> Pipeline:
    document_store = InMemoryDocumentStore(use_gpu=use_gpu, use_bm25=True)
    document_store.write_documents(documents)
    retriever = BM25Retriever(document_store=document_store, top_k=100)

    reranker = SentenceTransformersRanker(
        model_name_or_path="cross-encoder/ms-marco-MiniLM-L-12-v2", top_k=1, use_gpu=use_gpu
    )

    answer_parser = AnswerParser()  # pattern=r"\s+(.*)")
    lfqa_prompt = PromptTemplate(
        prompt="""Answer the question using the provided context. Please answer as concisely as possible.

Context: {join(documents)}

Question: {query}

Answer: """,
        output_parser=answer_parser,
    )
    prompter = PromptNode(model_name_or_path="gpt-3.5-turbo", default_prompt_template=lfqa_prompt, api_key=os.environ.get("OPENAI_API_KEY"))

    p = Pipeline()
    p.add_node(component=retriever, name="Retriever", inputs=["Query"])
    p.add_node(component=reranker, name="Reranker", inputs=["Retriever"])
    p.add_node(component=prompter, name="Prompter", inputs=["Reranker"])
    return p

def llama_few_k2(documents: List[Document], use_gpu=False) -> Pipeline:
    document_store = InMemoryDocumentStore(use_gpu=use_gpu, use_bm25=True)
    document_store.write_documents(documents)
    retriever = BM25Retriever(document_store=document_store, top_k=100)

    reranker = SentenceTransformersRanker(
        model_name_or_path="cross-encoder/ms-marco-MiniLM-L-12-v2", top_k=2, use_gpu=use_gpu
    )

    answer_parser = AnswerParser()  # pattern=r"\s+(.*)")
    lfqa_prompt = PromptTemplate(
        prompt="""Answer the question using the provided context. Please answer as concisely as possible.
For example:
Question: Who is teaching 11-711 in Spring 2024?
Answer: Neubig.


Context: {join(documents)}
Question: {query}
Answer: """,
        output_parser=answer_parser,
    )
    prompter = PromptNode(model_name_or_path="gpt-3.5-turbo", default_prompt_template=lfqa_prompt, api_key=os.environ.get("OPENAI_API_KEY"))

    p = Pipeline()
    p.add_node(component=retriever, name="Retriever", inputs=["Query"])
    p.add_node(component=reranker, name="Reranker", inputs=["Retriever"])
    p.add_node(component=prompter, name="Prompter", inputs=["Reranker"])
    return p

def llama_few(documents: List[Document], use_gpu=False) -> Pipeline:
    document_store = InMemoryDocumentStore(use_gpu=use_gpu, use_bm25=True)
    document_store.write_documents(documents)
    retriever = BM25Retriever(document_store=document_store, top_k=100)

    reranker = SentenceTransformersRanker(
        model_name_or_path="cross-encoder/ms-marco-MiniLM-L-12-v2", top_k=1, use_gpu=use_gpu
    )

    answer_parser = AnswerParser()  # pattern=r"\s+(.*)")
    lfqa_prompt = PromptTemplate(
        prompt="""Answer the question using the provided context. Please answer as concisely as possible.
For example:
Question: Who is teaching 11-711 in Spring 2024?
Answer: Neubig.


Context: {join(documents)}
Question: {query}
Answer: """,
        output_parser=answer_parser,
    )
    prompter = PromptNode(model_name_or_path="gpt-3.5-turbo", default_prompt_template=lfqa_prompt, api_key=os.environ.get("OPENAI_API_KEY"))

    p = Pipeline()
    p.add_node(component=retriever, name="Retriever", inputs=["Query"])
    p.add_node(component=reranker, name="Reranker", inputs=["Retriever"])
    p.add_node(component=prompter, name="Prompter", inputs=["Reranker"])
    return p
