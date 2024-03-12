from haystack import Pipeline
from haystack.schema import Document
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import BM25Retriever, SentenceTransformersRanker
from haystack.nodes.prompt import PromptNode
from haystack.nodes import PromptModel
from haystack.nodes import AnswerParser
from haystack.nodes.prompt.prompt_template import PromptTemplate
from fastrag.prompters.invocation_layers.llama_cpp import LlamaCPPInvocationLayer
import torch
from typing import List


def baseline(documents: List[Document]) -> Pipeline:
    document_store = InMemoryDocumentStore(use_gpu=False, use_bm25=True)
    document_store.write_documents(documents)
    retriever = BM25Retriever(document_store=document_store, top_k=100)

    reranker = SentenceTransformersRanker(
        model_name_or_path="cross-encoder/ms-marco-MiniLM-L-12-v2", top_k=1
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
    )

    p = Pipeline()
    p.add_node(component=retriever, name="Retriever", inputs=["Query"])
    p.add_node(component=reranker, name="Reranker", inputs=["Retriever"])
    p.add_node(component=prompter, name="prompt_node", inputs=["Reranker"])
    return p


def squad(documents: List[Document]) -> Pipeline:
    document_store = InMemoryDocumentStore(use_gpu=False, use_bm25=True)
    document_store.write_documents(documents)
    retriever = BM25Retriever(document_store=document_store, top_k=100)

    reranker = SentenceTransformersRanker(
        model_name_or_path="cross-encoder/qnli-distilroberta-base", top_k=1
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
    )

    p = Pipeline()
    p.add_node(component=retriever, name="Retriever", inputs=["Query"])
    p.add_node(component=reranker, name="Reranker", inputs=["Retriever"])
    p.add_node(component=prompter, name="prompt_node", inputs=["Reranker"])
    return p


def llama(documents: List[Document]) -> Pipeline:
    document_store = InMemoryDocumentStore(use_gpu=False, use_bm25=True)
    document_store.write_documents(documents)
    retriever = BM25Retriever(document_store=document_store, top_k=100)

    reranker = SentenceTransformersRanker(
        model_name_or_path="cross-encoder/ms-marco-MiniLM-L-12-v2", top_k=1
    )

    answer_parser = AnswerParser()  # pattern=r"\s+(.*)")
    lfqa_prompt = PromptTemplate(
        prompt="""Answer the question using the provided context.
For example:
Question: Who is teaching 11-711 in Spring 2024?

Answer: Neubig.

Now it's your turn.
Context: {join(documents)}

Question: {query}

Please answer as concisely as possible.
Answer: """,
        output_parser=answer_parser,
    )
    prompt_model = PromptModel(
        model_name_or_path="./fastRAG/models/marcoroni-7b-v3.Q4_K_M.gguf",
        invocation_layer_class=LlamaCPPInvocationLayer,
        model_kwargs=dict(max_new_tokens=50),
    )
    prompter = PromptNode(model_name_or_path=prompt_model, default_prompt_template=LFQA)

    p = Pipeline()
    p.add_node(component=retriever, name="Retriever", inputs=["Query"])
    p.add_node(component=reranker, name="Reranker", inputs=["Retriever"])
    p.add_node(component=prompter, name="Prompter", inputs=["Reranker"])
    return p
