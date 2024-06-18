import os
import sys
import multiprocessing as mp
from haystack.schema import Document
from scripts.data_processing import read_txt_files
from scripts.section_extraction import extract_sections
from scripts.embedding import EmbeddingModel
from scripts.retrieval import Retriever
from scripts.qa import QAModel
from scripts.gliner import GLiNERModel
from scripts.evaluation import evaluate_model

def process_file(file_info):
    subdir = file_info["subdir"]
    filename = file_info["filename"]
    content = file_info["content"]
    
    # Extract sections based on clues
    clues = [
        "Death benefits", "Death benefit", "Lump sum",
        "Interest rate", "Rate of interest", "Lump sum payment interest",
        "Lump sum interest rate", "Death benefit interest", "Interest accrued",
        "Interest on death benefit"
    ]
    sections = extract_sections(content, clues)
    
    return [(subdir, filename, sec) for sec in sections]

def main(method):
    root_dir = 'data/raw'
    gold_standard_file = 'data/gold_standard.csv'
    
    # Read and process documents
    documents = read_txt_files(root_dir)
    
    # Use multiprocessing to process files in parallel
    with mp.Pool(mp.cpu_count()) as pool:
        sections = pool.map(process_file, documents)
    
    sections = [item for sublist in sections for item in sublist]  # Flatten the list
    
    if method == "baseline":
        # Generate embeddings and create FAISS index
        embedding_model = EmbeddingModel()
        embeddings = embedding_model.generate_embeddings([sec[2] for sec in sections])
        index = embedding_model.initialize_faiss_index(embeddings.shape[1])
        embedding_model.add_to_index(index, embeddings)
        
        # Initialize Haystack components
        retriever = Retriever()
        retriever.write_documents([{"content": sec[2], "meta": {"subdir": sec[0], "filename": sec[1]}} for sec in sections])
        retriever.update_embeddings()
        
        qa_model = QAModel()
        qa_model.set_pipeline(retriever.retriever)
        
        def extract_information(filename):
            # Find relevant sections based on filename
            relevant_sections = [sec for sec in sections if sec[1] == filename]
            
            # Prepare context for QA model
            contexts = [Document(content=sec[2], meta={"subdir": sec[0], "filename": sec[1]}) for sec in relevant_sections]
            
            # Get answers using the QA model
            answers = []
            interest_rate, ir_score = qa_model.get_answer("What is the interest rate on the lump sum?", contexts)
            answers.append((interest_rate, ir_score, contexts[0].meta["subdir"], contexts[0].meta["filename"]))
            
            # Rank answers by score and return the best ones
            answers = sorted(answers, key=lambda x: x[1], reverse=True)  # Sort by interest rate score
            if answers:
                best_answer = answers[0]
                return best_answer[0], best_answer[2], best_answer[3]
            return "none", "none", "none"
        
        # Evaluate the model
        evaluation_results = evaluate_model(gold_standard_file, extract_information)
        print(evaluation_results)
    
    elif method == "gliner_oie":
        gliner_model = GLiNERModel()
        
        def extract_info_gliner(filename):
            # Find relevant sections based on filename
            relevant_sections = [sec for sec in sections if sec[1] == filename]
            
            # Prepare context for GLiNER model
            contexts = [sec[2] for sec in relevant_sections]
            
            prompt = "Extract the interest rate paid on the lump sum amounts paid to the payee on death of the insured person"
            answers = []
            for context in contexts:
                interest_rate = gliner_model.extract_info(prompt, context)
                answers.append((interest_rate, context))
            
            # Rank answers and return the best one
            answers = sorted(answers, key=lambda x: len(x[0]), reverse=True)  # Sort by length of interest rate extracted
            if answers:
                best_answer = answers[0]
                return best_answer[0], "N/A", filename  # Metadata is not used here
            return "none", "none", filename
        
        # Evaluate the model
        evaluation_results_oie = evaluate_model(gold_standard_file, extract_info_gliner)
        print(evaluation_results_oie)
    
    elif method == "gliner_qa":
        gliner_model = GLiNERModel()
        
        def answer_question_gliner(filename):
            # Find relevant sections based on filename
            relevant_sections = [sec for sec in sections if sec[1] == filename]
            
            # Prepare context for GLiNER model
            contexts = [sec[2] for sec in relevant_sections]
            
            question = "What is the interest rate on the lump sum paid to the payee on the death of the insured person?"
            answers = []
            for context in contexts:
                interest_rate = gliner_model.answer_question(question, context)
                answers.append((interest_rate, context))
            
            # Rank answers and return the best one
            answers = sorted(answers, key=lambda x: len(x[0]), reverse=True)  # Sort by length of interest rate extracted
            if answers:
                best_answer = answers[0]
                return best_answer[0], "N/A", filename  # Metadata is not used here
            return "none", "none", filename
        
        # Evaluate the model
        evaluation_results_qa = evaluate_model(gold_standard_file, answer_question_gliner)
        print(evaluation_results_qa)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <method>")
        print("Methods: baseline, gliner_oie, gliner_qa")
        sys.exit(1)
    
    method = sys.argv[1]
    main(method)