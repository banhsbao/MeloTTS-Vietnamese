import re
import unicodedata
from typing import List, Tuple

import numpy as np
import torch

from .vietnamese_bert import get_bert_feature as _get_bert_feature

# Bảng chữ cái tiếng Việt
vietnamese_alphabet = "aăâbcdđeêghiklmnoôơpqrstuưvxy"

# Nguyên âm tiếng Việt
vietnamese_vowels = "aăâeêioôơuưy"

# Phụ âm tiếng Việt
vietnamese_consonants = "bcdđghklmnpqrstvx"

# Dấu thanh tiếng Việt (0: không dấu, 1: sắc, 2: huyền, 3: hỏi, 4: ngã, 5: nặng)
vietnamese_tones = {
    0: ["a", "ă", "â", "e", "ê", "i", "o", "ô", "ơ", "u", "ư", "y"],
    1: ["á", "ắ", "ấ", "é", "ế", "í", "ó", "ố", "ớ", "ú", "ứ", "ý"],
    2: ["à", "ằ", "ầ", "è", "ề", "ì", "ò", "ồ", "ờ", "ù", "ừ", "ỳ"],
    3: ["ả", "ẳ", "ẩ", "ẻ", "ể", "ỉ", "ỏ", "ổ", "ở", "ủ", "ử", "ỷ"],
    4: ["ã", "ẵ", "ẫ", "ẽ", "ễ", "ĩ", "õ", "ỗ", "ỡ", "ũ", "ữ", "ỹ"],
    5: ["ạ", "ặ", "ậ", "ẹ", "ệ", "ị", "ọ", "ộ", "ợ", "ụ", "ự", "ỵ"]
}

# Bảng ánh xạ nguyên âm có dấu về không dấu
vowel_to_base = {}
for tone_idx, vowels in vietnamese_tones.items():
    for i, vowel in enumerate(vowels):
        vowel_to_base[vowel] = vietnamese_tones[0][i]

# Bảng ánh xạ nguyên âm không dấu về dấu
base_to_tones = {}
for i, base_vowel in enumerate(vietnamese_tones[0]):
    base_to_tones[base_vowel] = [vietnamese_tones[tone][i] for tone in range(6)]

# Nguyên âm đôi tiếng Việt
vietnamese_diphthongs = [
    "ai", "ao", "au", "ay", "âu", "ây", "eo", "êu", "ia", "iê", "iu", 
    "oa", "oă", "oe", "oi", "ôi", "ơi", "ua", "uâ", "uê", "ui", "uo", 
    "uô", "uơ", "ưa", "ưi", "ưu", "uy", "ươ", "ưa"
]

# Nguyên âm ba tiếng Việt
vietnamese_triphthongs = [
    "iêu", "oai", "oao", "oeo", "uai", "uây", "uôi", "ươi", "ươu", "uya", "uyê"
]

# Phụ âm đầu tiếng Việt
vietnamese_initial_consonants = [
    "b", "c", "ch", "d", "đ", "g", "gh", "gi", "h", "k", "kh", "l", "m", 
    "n", "ng", "ngh", "nh", "p", "ph", "q", "qu", "r", "s", "t", "th", "tr", "v", "x"
]

# Phụ âm cuối tiếng Việt
vietnamese_final_consonants = [
    "c", "ch", "m", "n", "ng", "nh", "p", "t"
]

# Bảng âm vị tiếng Việt
vietnamese_phonemes = [
    # Nguyên âm đơn
    "a", "ă", "â", "e", "ê", "i", "o", "ô", "ơ", "u", "ư", "y",
    # Nguyên âm đôi
    "ai", "ao", "au", "ay", "âu", "ây", "eo", "êu", "ia", "iê", "iu", "oa", "oă", "oe", "oi", "ôi", "ơi", "ua", "uâ", "uê", "ui", "uo", "uô", "uơ", "ưa", "ưi", "ưu", "uy", "ươ", "ưa",
    # Nguyên âm ba
    "iêu", "oai", "oao", "oeo", "uai", "uây", "uôi", "ươi", "ươu", "uya", "uyê",
    # Phụ âm đơn
    "b", "c", "ch", "d", "đ", "g", "gh", "gi", "h", "k", "kh", "l", "m", "n", "ng", "ngh", "nh", "p", "ph", "q", "qu", "r", "s", "t", "th", "tr", "v", "x",
    # Phụ âm cuối
    "c", "ch", "m", "n", "ng", "nh", "p", "t"
]

def normalize_text(text: str) -> str:
    """
    Chuẩn hóa văn bản tiếng Việt
    """
    # Chuyển về chữ thường
    text = text.lower()
    
    # Chuẩn hóa Unicode
    text = unicodedata.normalize('NFC', text)
    
    # Loại bỏ các ký tự không phải chữ cái, số, dấu câu cơ bản
    # Sửa lỗi bad escape \p bằng cách sử dụng phương pháp khác
    allowed_chars = set(vietnamese_alphabet + "0123456789.,!?;:'\"-_ ")
    text = ''.join(c for c in text if c in allowed_chars or c.isspace())
    
    # Thay thế nhiều khoảng trắng bằng một khoảng trắng
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# Tạo alias cho hàm normalize_text để tương thích với cách gọi trong cleaner.py
text_normalize = normalize_text

def extract_tone(word: str) -> Tuple[str, List[int]]:
    """
    Tách dấu thanh từ từ tiếng Việt
    Trả về từ không dấu và danh sách dấu thanh
    """
    result = ""
    tones = []
    
    for char in word:
        # Kiểm tra xem ký tự có phải là nguyên âm có dấu không
        if char in vowel_to_base:
            # Tìm dấu thanh
            for tone_idx, vowels in vietnamese_tones.items():
                if char in vowels:
                    tones.append(tone_idx)
                    result += vowel_to_base[char]
                    break
        else:
            result += char
            tones.append(0)  # Không dấu
    
    return result, tones

def find_vowel_position(word: str) -> int:
    """
    Tìm vị trí nguyên âm đầu tiên trong từ
    """
    for i, char in enumerate(word):
        if char.lower() in vietnamese_vowels:
            return i
    return -1

def analyze_vietnamese_word(word: str) -> Tuple[str, int, List[str]]:
    """
    Phân tích từ tiếng Việt thành các thành phần
    Trả về từ không dấu, vị trí dấu thanh, và danh sách âm vị
    """
    # Tách dấu thanh
    word_no_tone, word_tones = extract_tone(word)
    
    # Tìm vị trí dấu thanh (thường là nguyên âm cuối cùng)
    tone_position = 0
    for i in range(len(word_tones) - 1, -1, -1):
        if word_tones[i] > 0:
            tone_position = i
            break
    
    # Phân tích âm vị
    phonemes = []
    
    # Xử lý phụ âm đầu
    i = 0
    initial_consonant = ""
    
    # Tìm phụ âm đầu dài nhất có thể
    for length in range(4, 0, -1):  # Thử các độ dài từ 4 xuống 1
        if i + length <= len(word_no_tone):
            candidate = word_no_tone[i:i+length]
            if candidate in vietnamese_initial_consonants:
                initial_consonant = candidate
                i += length
                break
    
    if initial_consonant:
        phonemes.append(initial_consonant)
    
    # Xử lý nguyên âm (ưu tiên nguyên âm ba, rồi đến nguyên âm đôi, cuối cùng là nguyên âm đơn)
    vowel = ""
    
    # Thử nguyên âm ba
    for length in range(3, 0, -1):  # Thử các độ dài từ 3 xuống 1
        if i + length <= len(word_no_tone):
            candidate = word_no_tone[i:i+length]
            if (length == 3 and candidate in vietnamese_triphthongs) or \
               (length == 2 and candidate in vietnamese_diphthongs) or \
               (length == 1 and candidate in vietnamese_vowels):
                vowel = candidate
                i += length
                break
    
    if vowel:
        phonemes.append(vowel)
    
    # Xử lý phụ âm cuối
    if i < len(word_no_tone):
        final_consonant = word_no_tone[i:]
        if final_consonant in vietnamese_final_consonants:
            phonemes.append(final_consonant)
    
    return word_no_tone, tone_position, phonemes

def g2p(text: str) -> Tuple[List[str], List[int], List[int]]:
    """
    Chuyển đổi văn bản thành chuỗi âm vị (Grapheme-to-Phoneme)
    Trả về danh sách âm vị, dấu thanh và word-to-phoneme mapping
    """
    # Chuẩn hóa văn bản
    text = normalize_text(text)
    
    # Tách từ
    words = text.split()
    
    phones = []
    tones = []
    word2ph = []
    
    for word in words:
        # Bỏ qua các ký tự đặc biệt
        if not any(c.isalpha() for c in word):
            continue
        
        # Phân tích từ tiếng Việt
        _, tone_position, word_phones = analyze_vietnamese_word(word)
        
        # Thêm vào kết quả
        phones.extend(word_phones)
        
        # Xác định dấu thanh cho từng âm vị
        word_tones = [0] * len(word_phones)
        
        # Nếu có dấu thanh, gán cho nguyên âm (thường là phần tử thứ 2 nếu có phụ âm đầu)
        if len(word_phones) >= 2 and word_phones[0] in vietnamese_initial_consonants:
            vowel_index = 1
        else:
            vowel_index = 0
            
        # Tìm dấu thanh từ từ gốc
        word_no_tone, word_tone_list = extract_tone(word)
        tone_value = 0
        for t in word_tone_list:
            if t > 0:
                tone_value = t
                break
        
        if vowel_index < len(word_tones):
            word_tones[vowel_index] = tone_value
        
        tones.extend(word_tones)
        
        # Mỗi từ có bao nhiêu âm vị
        word2ph.append(len(word_phones))
    
    return phones, tones, word2ph

def get_bert_feature(text: str, word2ph: List[int], device: str = "cuda"):
    """
    Lấy đặc trưng BERT cho văn bản tiếng Việt
    """
    return _get_bert_feature(text, word2ph, device)

if __name__ == "__main__":
    # Test
    test_words = ["xin", "chào", "thế", "giới", "tiếng", "việt", "học", "máy"]
    for word in test_words:
        word_no_tone, tone_pos, phonemes = analyze_vietnamese_word(word)
        print(f"Từ: {word}, Không dấu: {word_no_tone}, Vị trí dấu: {tone_pos}, Âm vị: {phonemes}")
    
    text = "Xin chào thế giới!"
    norm_text = normalize_text(text)
    phones, tones, word2ph = g2p(norm_text)
    print(f"Normalized: {norm_text}")
    print(f"Phones: {phones}")
    print(f"Tones: {tones}")
    print(f"Word2ph: {word2ph}") 