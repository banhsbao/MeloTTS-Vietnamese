#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script để xử lý và sửa lỗi trong dữ liệu tiếng Việt cho MeloTTS
"""

import os
import re
import unicodedata
import argparse
from tqdm import tqdm

def normalize_vietnamese_text(text):
    """
    Chuẩn hóa văn bản tiếng Việt, loại bỏ các ký tự không hợp lệ
    """
    # Chuẩn hóa Unicode
    text = unicodedata.normalize('NFC', text)
    
    # Chuyển về chữ thường
    text = text.lower()
    
    # Loại bỏ các ký tự đặc biệt không cần thiết
    vietnamese_chars = "aăâbcdđeêghiklmnoôơpqrstuưvxyáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ"
    allowed_chars = vietnamese_chars + "0123456789.,!?;:'\"-_ "
    
    # Giữ lại các ký tự hợp lệ
    text = ''.join(c for c in text if c in allowed_chars or c.isspace())
    
    # Thay thế nhiều khoảng trắng bằng một khoảng trắng
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def clean_metadata_file(input_file, output_file):
    """
    Làm sạch file metadata, loại bỏ các dòng có lỗi
    """
    print(f"Đang xử lý file {input_file}...")
    
    valid_lines = []
    error_lines = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in tqdm(lines, desc="Xử lý dữ liệu"):
        try:
            parts = line.strip().split('|')
            if len(parts) < 4:
                error_lines.append((line, "Không đủ trường dữ liệu"))
                continue
                
            wav_path, speaker, language, text = parts[:4]
            
            # Kiểm tra file âm thanh tồn tại
            if not os.path.exists(wav_path):
                error_lines.append((line, f"File âm thanh không tồn tại: {wav_path}"))
                continue
                
            # Chuẩn hóa văn bản
            normalized_text = normalize_vietnamese_text(text)
            
            # Kiểm tra văn bản sau khi chuẩn hóa
            if not normalized_text or len(normalized_text) < 2:
                error_lines.append((line, "Văn bản quá ngắn sau khi chuẩn hóa"))
                continue
                
            # Tạo dòng mới với văn bản đã chuẩn hóa
            new_line = f"{wav_path}|{speaker}|{language}|{normalized_text}\n"
            valid_lines.append(new_line)
            
        except Exception as e:
            error_lines.append((line, str(e)))
    
    # Ghi các dòng hợp lệ vào file đầu ra
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(valid_lines)
    
    # Ghi các dòng lỗi vào file log
    error_log_file = output_file + ".error.log"
    with open(error_log_file, 'w', encoding='utf-8') as f:
        for line, error in error_lines:
            f.write(f"ERROR: {error}\nLINE: {line}\n\n")
    
    print(f"Đã xử lý xong {len(lines)} dòng:")
    print(f"- Số dòng hợp lệ: {len(valid_lines)}")
    print(f"- Số dòng lỗi: {len(error_lines)}")
    print(f"Kết quả đã được lưu vào {output_file}")
    print(f"Các dòng lỗi đã được lưu vào {error_log_file}")

def main():
    parser = argparse.ArgumentParser(description="Xử lý và sửa lỗi trong dữ liệu tiếng Việt cho MeloTTS")
    parser.add_argument("--input", default="dataset/metadata.list", help="Đường dẫn đến file metadata gốc")
    parser.add_argument("--output", default="dataset/metadata.cleaned.list", help="Đường dẫn đến file metadata đã làm sạch")
    
    args = parser.parse_args()
    
    clean_metadata_file(args.input, args.output)

if __name__ == "__main__":
    main() 