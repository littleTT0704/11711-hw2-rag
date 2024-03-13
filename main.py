from haystack import Pipeline
from haystack.schema import Document
from typing import List, Tuple
import os
import tqdm
import json
import argparse
from haystack.nodes import PreProcessor, PDFToTextConverter


from models import *
from evaluation import normalize_answer, f1_score, exact_match_score


def load_documents(data_dir: str) -> List[str]:
    with open(os.path.join(data_dir, "metadata.json"), "r") as f:
        metadata_raw = json.load(f)
    metadatas = dict()
    for metadata in metadata_raw:
        m = metadata.copy()
        filename = m.pop("filename")
        metadatas[filename] = m

    txts = []
    pdfs = []
    pdf = PDFToTextConverter()
    pre = PreProcessor()
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".txt") or file.endswith(".pdf"):
                if file not in metadatas:
                    print(f"File {os.path.join(root, file)} not in metadata")
                else:
                    metadata = metadatas[file]
                    if file.endswith(".txt"):
                        with open(os.path.join(root, file), "r") as f:
                            raw = f.read().strip()
                        txts.append(Document(content=raw, meta=metadata))
                    else:
                        doc = pdf.convert(
                            os.path.join(root, file),
                            meta=metadata,
                            remove_numeric_tables=False,
                            valid_languages=["en"],
                        )
                        pdfs += doc
    res = pdfs
    res += pre.process(
        txts,
        split_by="passage",
        split_length=1,
        split_respect_sentence_boundary=False,
    )
    res = pre.process(
        res, split_by="word", split_length=200, split_respect_sentence_boundary=True
    )
    return res


def load_qa(question_file: str, answer_file: str) -> Tuple[List[str], List[str]]:
    questions = []
    answers = []
    with open(question_file, "r") as fq, open(answer_file, "r") as fa:
        for lineq, linea in zip(fq, fa):
            if lineq[0] == "#":
                continue
            q, a = lineq.strip(), linea.strip()
            questions.append(q)
            answers.append(a)
    return questions, answers


def predict(p: Pipeline, queries: List[str], output_file: str) -> List[str]:
    res = []
    with open(output_file, "w") as f:
        for query in tqdm.tqdm(queries):
            answer = p.run(query=query)
            ans = answer["answers"][0].answer
            res.append(ans)
            f.write(ans + "\n")
            f.flush()
    return res


def evaluate(output: List[str], truth: List[str]) -> Tuple[float, float, float]:
    assert len(output) == len(truth)

    f1 = 0
    recall = 0
    em = 0
    for o, t in zip(output, truth):
        if "|" in t:
            l = t.split("|")
        else:
            l = [t]

        f1_, recall_ = f1_score(o, l, normalize_fn=normalize_answer)
        em_ = exact_match_score(o, l, normalize_fn=normalize_answer)
        f1 += f1_
        recall += recall_
        em += em_

        print(f"Prediction: {o}")
        print(f"Truth: {t}")
        print(f"F1: {f1_}, Recall: {recall_}, EM: {em_}")

    return f1 / len(output), recall / len(output), em / len(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, choices={"dev", "test"}, default="test")
    parser.add_argument("--data_dir", type=str, default="data")
    parser.add_argument("--output", type=str, default="prediction.txt")
    parser.add_argument("--model", type=str, default="baseline")
    parser.add_argument("--use_gpu", action="store_true")
    parser.add_argument(
        "--dev",
        type=str,
        nargs=2,
        default=("dev/questions.txt", "dev/reference_answers.txt"),
    )
    parser.add_argument("--test", type=str, default="test/questions.txt")
    args = parser.parse_args()

    docs = load_documents(args.data_dir)
    p = eval(args.model)(docs, use_gpu=args.use_gpu)

    if args.mode == "dev":
        questions, answers = load_qa(*args.dev)
        prediction = predict(p, questions, args.output)

        f1, recall, em = evaluate(prediction, answers)
        print(f"F1: {f1}, Recall: {recall}, EM: {em}")
    else:
        questions = []
        with open(args.test, "r") as fq:
            for lineq in fq:
                q = lineq.strip()
                if q != "":
                    questions.append(q)
        prediction = predict(p, questions, args.output)
