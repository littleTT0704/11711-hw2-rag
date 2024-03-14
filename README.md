# End-to-End NLP System Building Project README

## Overview

This project aims to build a comprehensive NLP system capable of extracting, processing, and querying text data from various sources to answer specific questions accurately. It utilizes state-of-the-art models and methods to handle a wide range of data types and query formats. Our pipeline is designed to tackle challenges in data extraction, annotation, and question answering, emphasizing accuracy and efficiency.

## Installation and Dependencies

To run this project, you will need Python 3.8 or later. Key dependencies include:

- Beautiful Soup for HTML data extraction.
- Doccano for data annotation.
- The Semantic Scholar API for retrieving scholarly articles.
- Sentence Transformers and Cross-Encoders for information retrieval and ranking.
- Flan-T5 and Llama 2 models for generating answers.

## Data

Our data comprises:

- Historical and event information from various websites.
- Faculty information, including publication records from the Semantic Scholar API.
- Course metadata from Carnegie Mellon University (CMU) schedules and academic calendars.
- Academic program details from the Language Technology Institute (LTI) website and handbooks.

All raw data are available in the `data` directory in our GitHub repository.

## Usage

### Data Extraction

Use the `faculty_info_extraction.py` and `download_paper_metadata.py` script to scrape and process HTML documents, faculty papers. 
Use `Scrape.py` for scrape and process academic and history.

### Data Annotation

We use Doccano for initial sentence composition annotation. Post-annotation processing scripts are provided to refine and convert annotations into a question-answer format suitable for training.

### Question Answering

Run the `main.py` script to query the system. The script utilizes our end-to-end pipeline to retrieve information, re-rank relevant documents, and generate concise answers.

## Models

Our system incorporates several models across its pipeline:

- **Retriever:** Uses BM25 and Sentence Transformers to fetch relevant documents.
- **Re-ranker:** Applies Cross-Encoders for finer-grained relevance scoring.
- **Prompter:** Utilizes Flan-T5 and Llama 2 models for generating answers, including zero-shot and few-shot prompting techniques.

We experimented with various configurations to optimize performance, details of which are documented in our project report.

## Evaluation

We rigorously evaluate our system using F1, recall, and exact match scores across different pipeline configurations and question types. Our evaluation demonstrates the effectiveness of few-shot prompting with Llama 2 and the retrieve-and-augment strategy for question answering.

## Contact

For queries or contributions, please contact Jiatai Li, Rui Xi, and Evelyn Zhu at {jiatail, rxi2, junyizh2}@andrew.cmu.edu.

## References

Please refer to our project report for a detailed list of references, including publications related to the models and methods we have employed in this project.

