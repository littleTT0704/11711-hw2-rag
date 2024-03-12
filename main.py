from haystack import Pipeline
from haystack.schema import Document
from typing import List, Tuple
from transformers import GPT2TokenizerFast
import os
import tqdm

from models import *
from evaluation import normalize_answer, f1_score, exact_match_score


def load_documents(data_dir: str) -> List[str]:
    # Faculty @ LTI
    papers = []
    for root, dirs, files in os.walk(os.path.join(data_dir, "papers")):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    # Read the content of the chunk and add it to the list
                    papers.append(f.read())

    # Courses @ CMU
    courses = []
    for root, dirs, files in os.walk(os.path.join(data_dir, "Courses")):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                print(file_path)
                with open(file_path, "r") as f:
                    courses += f.read().split("\n\n\n")

    # Academics @ LTI
    program = []
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    max_tokens = 512
    for root, dirs, files in os.walk(os.path.join(data_dir, "program")):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as file:
                    text = file.read()

                tokens = tokenizer.encode(text)
                chunks = [
                    tokens[i : i + max_tokens]
                    for i in range(0, len(tokens), max_tokens)
                ]

            for chunk in chunks:
                chunk_text = tokenizer.decode(chunk)
                program.append(chunk_text)

    # Events @ CMU
    events = []
    for root, dirs, files in os.walk(os.path.join(data_dir, "Events")):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                print(file_path)
                with open(file_path, "r") as f:
                    events += f.read().split("\n\n\n")

    # History @ SCS and CMU
    history = []
    for root, dirs, files in os.walk(os.path.join(data_dir, "history")):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, "r") as f:
                history += f.read().split("\n\n\n")

    res = papers + courses + program + events + history
    return [Document(content=s) for s in res]


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
    docs = load_documents("data")
    p = squad(docs)

    if False:
        questions, answers = load_qa("dev/questions.txt", "dev/reference_answers.txt")
        prediction = predict(p, questions, "dev/prediction.txt")

        f1, recall, em = evaluate(prediction, answers)
        print(f"F1: {f1}, Recall: {recall}, EM: {em}")

    else:
        questions = []
        with open("test/questions.txt", "r") as fq:
            for lineq in fq:
                q = lineq.strip()
                if q != "":
                    questions.append(q)
        prediction = predict(p, questions, "test/prediction.txt")