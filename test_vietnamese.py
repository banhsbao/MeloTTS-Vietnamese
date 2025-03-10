#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script kiểm tra các module tiếng Việt cho MeloTTS
"""

import os
import sys
import torch
from melo.text.vietnamese import normalize_text, g2p, analyze_vietnamese_word
from melo.text.vietnamese_bert import get_bert_feature, preprocess_text_for_phobert

def test_normalize_text():
    """Kiểm tra hàm chuẩn hóa văn bản"""
    test_texts = [
        "Xin chào thế giới!",
        "TIẾNG VIỆT rất hay.",
        "Học máy  và  trí tuệ nhân tạo.",
        "Xử lý ngôn ngữ tự nhiên (NLP) là một lĩnh vực thú vị."
    ]
    
    print("=== Kiểm tra chuẩn hóa văn bản ===")
    for text in test_texts:
        normalized = normalize_text(text)
        print(f"Gốc: {text}")
        print(f"Chuẩn hóa: {normalized}")
        print("-" * 50)

def test_word_analysis():
    """Kiểm tra phân tích từ tiếng Việt"""
    test_words = [
        "xin", "chào", "thế", "giới", 
        "tiếng", "việt", "học", "máy",
        "trường", "phương", "nghiệp", "khuyến"
    ]
    
    print("=== Kiểm tra phân tích từ ===")
    for word in test_words:
        word_no_tone, tone_pos, phonemes = analyze_vietnamese_word(word)
        print(f"Từ: {word}")
        print(f"Không dấu: {word_no_tone}")
        print(f"Vị trí dấu: {tone_pos}")
        print(f"Âm vị: {phonemes}")
        print("-" * 50)

def test_g2p():
    """Kiểm tra chuyển đổi grapheme-to-phoneme"""
    test_sentences = [
        "Xin chào thế giới!",
        "Tiếng Việt rất hay.",
        "Học máy và trí tuệ nhân tạo."
    ]
    
    print("=== Kiểm tra G2P ===")
    for text in test_sentences:
        phones, tones, word2ph = g2p(text)
        print(f"Văn bản: {text}")
        print(f"Âm vị: {phones}")
        print(f"Dấu thanh: {tones}")
        print(f"Word2ph: {word2ph}")
        print("-" * 50)

def test_bert_feature():
    """Kiểm tra trích xuất đặc trưng BERT"""
    test_text = "Xin chào thế giới!"
    phones, tones, word2ph = g2p(test_text)
    
    print("=== Kiểm tra BERT ===")
    print(f"Văn bản: {test_text}")
    print(f"Word2ph: {word2ph}")
    
    try:
        # Thử sử dụng CPU để tránh lỗi nếu không có GPU
        features = get_bert_feature(test_text, word2ph, device="cpu")
        print(f"Kích thước đặc trưng BERT: {features.shape}")
        print("Trích xuất BERT thành công!")
    except Exception as e:
        print(f"Lỗi khi trích xuất BERT: {str(e)}")
    
    print("-" * 50)

def test_preprocess_for_phobert():
    """Kiểm tra tiền xử lý cho PhoBERT"""
    test_text = "Xin chào thế giới! Tiếng Việt rất hay."
    
    print("=== Kiểm tra tiền xử lý cho PhoBERT ===")
    print(f"Văn bản gốc: {test_text}")
    
    preprocessed = preprocess_text_for_phobert(test_text)
    print(f"Sau khi xử lý: {preprocessed}")
    print("-" * 50)

def main():
    """Hàm chính"""
    print("Bắt đầu kiểm tra các module tiếng Việt cho MeloTTS")
    print("=" * 60)
    
    # Kiểm tra chuẩn hóa văn bản
    test_normalize_text()
    
    # Kiểm tra phân tích từ
    test_word_analysis()
    
    # Kiểm tra G2P
    test_g2p()
    
    # Kiểm tra tiền xử lý cho PhoBERT
    test_preprocess_for_phobert()
    
    # Kiểm tra BERT
    test_bert_feature()
    
    print("Hoàn thành kiểm tra!")

if __name__ == "__main__":
    main() 