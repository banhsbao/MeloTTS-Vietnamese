input_tsv = "dataset/meta_data.tsv"
output_txt = "dataset/metadata.list"

import csv

encodings_to_try = ["utf-8-sig", "utf-8", "latin-1"]
success = False

for encoding in encodings_to_try:
    try:
        with open(input_tsv, "r", encoding=encoding) as infile, open(output_txt, "w", encoding="utf-8") as outfile:
            reader = csv.reader(infile, delimiter="\t")
            
            for row in reader:
                if len(row) != 2:
                    continue
                    
                wav_path = f"dataset/{row[0]}"
                language = "VN"
                script = row[1]
                
                formatted_line = f"{wav_path}|{language}-default|{language}|{script}\n"
                outfile.write(formatted_line)
        
        success = True
        break 
        
    except UnicodeDecodeError:
        continue

if not success:
    print("Failed to process the file with any of the attempted encodings.")