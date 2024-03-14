import re
import string
from collections import Counter
from typing import Callable, List, Tuple


# Normalization and score functions from SQuAD evaluation script https://worksheets.codalab.org/rest/bundles/0x6b567e1cf2e041ec80d7098f031c5c9e/contents/blob/
def normalize_answer(s: str) -> str:
    def remove_articles(text):
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def em(prediction: str, ground_truth: str, normalize_fn: Callable[[str], str]) -> float:
    return float(normalize_fn(prediction) == normalize_fn(ground_truth))


def f1(
    prediction: str, ground_truth: str, normalize_fn: Callable[[str], str]
) -> Tuple[float, float]:
    prediction_tokens = normalize_fn(prediction).split()
    ground_truth_tokens = normalize_fn(ground_truth).split()
    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())

    if num_same == 0:
        return 0, 0
    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(ground_truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1, recall


def f1_score(
    prediction: str,
    ground_truths: List[str],
    normalize_fn: Callable[[str], str] = lambda x: x,
) -> Tuple[float, float]:
    score = [f1(prediction, gt, normalize_fn) for gt in ground_truths]
    return max([s[0] for s in score]), max([s[1] for s in score])


def exact_match_score(
    prediction: str,
    ground_truths: List[str],
    normalize_fn: Callable[[str], str] = lambda x: x,
) -> float:
    return max([em(prediction, gt, normalize_fn) for gt in ground_truths])
