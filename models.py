from haystack import Pipeline
from haystack.schema import Document
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import BM25Retriever, SentenceTransformersRanker, EmbeddingRetriever
from haystack.nodes.prompt import PromptNode
from haystack.nodes.prompt.prompt_model import PromptModel
from fastrag.prompters.invocation_layers.llama_cpp import LlamaCPPInvocationLayer

import torch
from typing import List

default_prompt = """Answer the question using the provided context. Please answer as concisely as possible.
{meta['few_shot_example']}


Context: {join(documents, delimiter=new_line)}

Question: {query}

Answer: """


def baseline(
    documents: List[Document], use_gpu: bool = False, top_k: int = 1
) -> Pipeline:
    document_store = InMemoryDocumentStore(use_gpu=use_gpu, use_bm25=True)
    document_store.write_documents(documents)
    retriever = BM25Retriever(document_store=document_store, top_k=100)

    reranker = SentenceTransformersRanker(
        model_name_or_path="cross-encoder/ms-marco-MiniLM-L-12-v2",
        top_k=top_k,
        use_gpu=use_gpu,
    )

    prompter = PromptNode(
        model_name_or_path="MBZUAI/LaMini-Flan-T5-783M",
        default_prompt_template=default_prompt,
        model_kwargs={"model_max_length": 2048, "torch_dtype": torch.bfloat16},
        use_gpu=use_gpu,
    )

    p = Pipeline()
    p.add_node(component=retriever, name="Retriever", inputs=["Query"])
    p.add_node(component=reranker, name="Reranker", inputs=["Retriever"])
    p.add_node(component=prompter, name="prompt_node", inputs=["Reranker"])
    return p


def embed_meta(
    documents: List[Document], use_gpu: bool = False, top_k: int = 1
) -> Pipeline:
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
        top_k=top_k,
        use_gpu=use_gpu,
    )

    prompter = PromptNode(
        model_name_or_path="MBZUAI/LaMini-Flan-T5-783M",
        default_prompt_template=default_prompt,
        model_kwargs={"model_max_length": 2048, "torch_dtype": torch.bfloat16},
        use_gpu=use_gpu,
    )

    p = Pipeline()
    p.add_node(component=retriever, name="Retriever", inputs=["Query"])
    p.add_node(component=reranker, name="Reranker", inputs=["Retriever"])
    p.add_node(component=prompter, name="prompt_node", inputs=["Reranker"])
    return p


def squad(documents: List[Document], use_gpu: bool = False, top_k: int = 1) -> Pipeline:
    document_store = InMemoryDocumentStore(use_gpu=use_gpu, use_bm25=True)
    document_store.write_documents(documents)
    retriever = BM25Retriever(document_store=document_store, top_k=100)

    reranker = SentenceTransformersRanker(
        model_name_or_path="cross-encoder/qnli-distilroberta-base",
        top_k=top_k,
        use_gpu=use_gpu,
    )

    prompter = PromptNode(
        model_name_or_path="MBZUAI/LaMini-Flan-T5-783M",
        default_prompt_template=default_prompt,
        model_kwargs={"model_max_length": 2048, "torch_dtype": torch.bfloat16},
        use_gpu=use_gpu,
    )

    p = Pipeline()
    p.add_node(component=retriever, name="Retriever", inputs=["Query"])
    p.add_node(component=reranker, name="Reranker", inputs=["Retriever"])
    p.add_node(component=prompter, name="prompt_node", inputs=["Reranker"])
    return p


def few_shot_pipeline(
    questions: List[str],
    answers: List[str],
    n_examples: int = 1,
    use_gpu: bool = False,
) -> Pipeline:
    docs = []
    for q, a in zip(questions, answers):
        docs.append(Document(content=q, meta={"answer": a}))

    document_store = InMemoryDocumentStore(use_gpu=use_gpu, use_bm25=True)
    document_store.write_documents(docs)
    retriever = BM25Retriever(document_store=document_store, top_k=n_examples)

    p = Pipeline()
    p.add_node(component=retriever, name="Retriever", inputs=["Query"])
    return p


def llama(documents: List[Document], use_gpu=False, top_k: int = 1) -> Pipeline:
    document_store = InMemoryDocumentStore(use_gpu=use_gpu, use_bm25=True)
    document_store.write_documents(documents)
    retriever = BM25Retriever(document_store=document_store, top_k=100)

    reranker = SentenceTransformersRanker(
        model_name_or_path="cross-encoder/ms-marco-MiniLM-L-12-v2",
        top_k=top_k,
        use_gpu=use_gpu,
    )

    prompt_model = PromptModel(
        model_name_or_path="marcoroni-7b-v3.Q4_K_M.gguf",
        invocation_layer_class=LlamaCPPInvocationLayer,
        model_kwargs=dict(max_new_tokens=50, model_max_length=1024),
        use_gpu=True,
    )
    prompter = PromptNode(
        model_name_or_path=prompt_model,
        default_prompt_template=default_prompt,
        use_gpu=True,
    )

    p = Pipeline()
    p.add_node(component=retriever, name="Retriever", inputs=["Query"])
    p.add_node(component=reranker, name="Reranker", inputs=["Retriever"])
    p.add_node(component=prompter, name="Prompter", inputs=["Reranker"])
    return p
