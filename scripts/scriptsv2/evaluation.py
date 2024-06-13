import pandas as pd

def evaluate_model(gold_standard_file, extract_information):
    gold_standard = pd.read_csv(gold_standard_file)
    
    results = []
    for _, row in gold_standard.iterrows():
        filename = row['filename']
        expected_interest_rate = row['interest_rate']
        
        interest_rate, subdir, file = extract_information(filename)
        
        result = {
            'filename': filename,
            'expected_interest_rate': expected_interest_rate,
            'extracted_interest_rate': interest_rate,
            'subdir': subdir,
            'file': file,
        }
        results.append(result)
    
    results_df = pd.DataFrame(results)
    results_df.to_csv('evaluation_results.csv', index=False)
    return results_df