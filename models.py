from haystack import Pipeline
from haystack.schema import Document
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import BM25Retriever, SentenceTransformersRanker
from haystack.nodes.prompt import PromptNode
from haystack.nodes import PromptModel
from haystack.nodes import AnswerParser
from haystack.nodes.prompt.prompt_template import PromptTemplate
import torch
from typing import List


def baseline(documents: List[Document]) -> Pipeline:
    document_store = InMemoryDocumentStore(use_gpu=False, use_bm25=True)
    document_store.write_documents(documents)
    retriever = BM25Retriever(document_store=document_store, top_k=100)

    reranker = SentenceTransformersRanker(
        model_name_or_path="cross-encoder/ms-marco-MiniLM-L-12-v2", top_k=1
    )

    answer_parser = AnswerParser()#pattern=r"\s+(.*)")
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
