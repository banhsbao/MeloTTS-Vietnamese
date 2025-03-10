import torch
from transformers import AutoTokenizer, AutoModel
import re

# Sử dụng PhoBERT cho tiếng Việt
BERT_MODEL_NAME = "vinai/phobert-base"

_tokenizer = None
_model = None

def _load_bert_model():
    global _tokenizer, _model
    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(BERT_MODEL_NAME)
    if _model is None:
        _model = AutoModel.from_pretrained(BERT_MODEL_NAME)
    return _tokenizer, _model

def preprocess_text_for_phobert(text):
    """
    Tiền xử lý văn bản cho PhoBERT
    PhoBERT yêu cầu văn bản được tách từ trước khi tokenize
    """
    try:
        # Thử sử dụng underthesea nếu đã cài đặt
        from underthesea import word_tokenize
        return " ".join(word_tokenize(text))
    except ImportError:
        try:
            # Thử sử dụng pyvi nếu đã cài đặt
            from pyvi import ViTokenizer
            return ViTokenizer.tokenize(text)
        except ImportError:
            # Nếu không có thư viện nào, sử dụng phương pháp đơn giản
            # Thêm khoảng trắng trước và sau các dấu câu - sửa regex để tránh lỗi
            text = re.sub(r'([.,!?;:])', r' \1 ', text)
            # Loại bỏ khoảng trắng thừa
            text = re.sub(r'\s+', ' ', text).strip()
            return text

def align_bert_features_with_phonemes(bert_features, word2ph):
    """
    Căn chỉnh đặc trưng BERT với các âm vị
    
    Args:
        bert_features: Đặc trưng BERT cho mỗi token
        word2ph: Danh sách số lượng âm vị cho mỗi từ
        
    Returns:
        Đặc trưng BERT được căn chỉnh với các âm vị
    """
    aligned_features = []
    
    # Đảm bảo số lượng đặc trưng BERT khớp với số lượng từ
    if len(bert_features) < len(word2ph):
        # Nếu thiếu đặc trưng BERT, sao chép đặc trưng cuối cùng
        padding = [bert_features[-1]] * (len(word2ph) - len(bert_features))
        bert_features = torch.cat([bert_features, torch.stack(padding)])
    elif len(bert_features) > len(word2ph):
        # Nếu thừa đặc trưng BERT, cắt bớt
        bert_features = bert_features[:len(word2ph)]
    
    # Ánh xạ đặc trưng BERT cho từng âm vị
    for i, ph_len in enumerate(word2ph):
        if ph_len > 0:
            # Lặp lại đặc trưng BERT cho mỗi âm vị trong từ
            bert_feature = bert_features[i]
            aligned_features.extend([bert_feature] * ph_len)
    
    return torch.stack(aligned_features) if aligned_features else torch.zeros((1, bert_features.shape[-1]))

def get_bert_feature(text, word2ph, device="cuda"):
    """
    Trích xuất đặc trưng BERT cho văn bản tiếng Việt
    
    Args:
        text: Văn bản đầu vào
        word2ph: Danh sách số lượng âm vị cho mỗi từ
        device: Thiết bị tính toán (cuda hoặc cpu)
        
    Returns:
        Tensor đặc trưng BERT
    """
    tokenizer, model = _load_bert_model()
    
    # Tiền xử lý văn bản cho PhoBERT
    preprocessed_text = preprocess_text_for_phobert(text)
    
    with torch.no_grad():
        # Tokenize văn bản
        inputs = tokenizer(preprocessed_text, return_tensors="pt")
        
        # Chuyển sang thiết bị tính toán
        if device == "cuda" and torch.cuda.is_available():
            inputs = {k: v.to(device) for k, v in inputs.items()}
            model = model.to(device)
        
        # Lấy đặc trưng BERT
        outputs = model(**inputs)
        
        # Lấy hidden states từ lớp cuối cùng
        hidden_states = outputs.last_hidden_state[0].cpu()
        
        # Bỏ qua token đặc biệt [CLS] ở đầu và [SEP] ở cuối
        hidden_states = hidden_states[1:-1]
        
        # Căn chỉnh đặc trưng BERT với các âm vị
        bert_features = align_bert_features_with_phonemes(hidden_states, word2ph)
        
    return bert_features

if __name__ == "__main__":
    # Test
    text = "Xin chào thế giới!"
    word2ph = [1, 2, 2, 2]  # Giả sử mỗi từ có số âm vị tương ứng
    features = get_bert_feature(text, word2ph, device="cpu")
    print(f"BERT features shape: {features.shape}") 