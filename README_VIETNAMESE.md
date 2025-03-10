# MeloTTS cho Tiếng Việt

Đây là hướng dẫn sử dụng MeloTTS để huấn luyện và tạo giọng nói tiếng Việt.

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/myshell-ai/MeloTTS.git
cd MeloTTS
```

2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

## Chuẩn bị dữ liệu

MeloTTS sử dụng bộ dữ liệu tiếng Việt từ Hugging Face. Bạn có thể tải xuống bằng lệnh:

```bash
bash download-dataset.sh
```

Hoặc tải thủ công từ: https://huggingface.co/datasets/ntt123/viet-tts-dataset

Cấu trúc dữ liệu cần có định dạng:
```
dataset/
├── meta_data.tsv
└── wavs/
    ├── speaker1/
    │   ├── file1.wav
    │   └── file2.wav
    └── speaker2/
        ├── file1.wav
        └── file2.wav
```

File `meta_data.tsv` cần có định dạng:
```
wavs/speaker1/file1.wav	Nội dung văn bản tiếng Việt
wavs/speaker1/file2.wav	Nội dung văn bản tiếng Việt khác
```

## Tiền xử lý dữ liệu

1. Tạo file metadata.list từ meta_data.tsv:
```bash
python runner/generate-metadata.py
```

2. Làm sạch dữ liệu tiếng Việt (xử lý lỗi):
```bash
python fix_vietnamese_dataset.py --input dataset/metadata.list --output dataset/metadata.cleaned.list
```

3. Tiền xử lý văn bản:
```bash
python melo/preprocess_text.py --metadata dataset/metadata.cleaned.list --config_path melo/configs/config.json
```

## Xử lý lỗi phổ biến

### Lỗi "bad escape \p at position 2"

Lỗi này xảy ra do biểu thức chính quy (regex) không hợp lệ trong quá trình xử lý văn bản. Đã được sửa trong mã nguồn. Nếu bạn vẫn gặp lỗi này, hãy chạy script làm sạch dữ liệu:

```bash
python fix_vietnamese_dataset.py
```

### Lỗi khi xử lý ký tự đặc biệt

Một số ký tự đặc biệt trong dữ liệu tiếng Việt có thể gây ra lỗi. Script `fix_vietnamese_dataset.py` sẽ loại bỏ các ký tự không hợp lệ và chuẩn hóa văn bản.

### Lỗi khi tải PhoBERT

Nếu gặp lỗi khi tải mô hình PhoBERT, hãy đảm bảo bạn có kết nối internet ổn định. Bạn cũng có thể tải trước mô hình:

```python
from transformers import AutoTokenizer, AutoModel
tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")
model = AutoModel.from_pretrained("vinai/phobert-base")
```

## Huấn luyện mô hình

Để huấn luyện mô hình, sử dụng lệnh:

```bash
bash train-no-download.sh
```

Hoặc:

```bash
python melo/preprocess_text.py --metadata dataset/metadata.cleaned.list --config_path melo/configs/config.json
bash melo/train.sh melo/configs/config.json 2
```

Trong đó, số 2 là số GPU sử dụng để huấn luyện. Nếu bạn chỉ có 1 GPU, hãy thay bằng 1.

## Tạo giọng nói

Sau khi huấn luyện, bạn có thể sử dụng mô hình để tạo giọng nói tiếng Việt:

```python
from melo.api import TTS

# Khởi tạo mô hình
tts = TTS("path/to/model", device="cuda")

# Tạo giọng nói
tts.tts("Xin chào thế giới!", speaker="VN-default", language="VN", output_path="output.wav")
```

## Kiểm tra các module tiếng Việt

Để kiểm tra xem các module tiếng Việt đã hoạt động đúng chưa, bạn có thể chạy script kiểm tra:

```bash
python test_vietnamese.py
```

Script này sẽ kiểm tra các chức năng:
- Chuẩn hóa văn bản
- Phân tích từ tiếng Việt
- Chuyển đổi grapheme-to-phoneme
- Tiền xử lý cho PhoBERT
- Trích xuất đặc trưng BERT

## Lưu ý khi sử dụng tiếng Việt

1. Đảm bảo văn bản tiếng Việt được chuẩn hóa Unicode (NFC).
2. Tiếng Việt có 6 dấu thanh (không dấu, sắc, huyền, hỏi, ngã, nặng) cần được xử lý đúng.
3. Nếu gặp vấn đề với âm vị tiếng Việt, bạn có thể cần điều chỉnh file `melo/text/vietnamese.py`.

## Tùy chỉnh nâng cao

Nếu muốn tùy chỉnh xử lý tiếng Việt, bạn có thể:

1. Điều chỉnh hàm `g2p` trong `melo/text/vietnamese.py` để cải thiện chuyển đổi grapheme-to-phoneme.
2. Thêm hoặc điều chỉnh các âm vị tiếng Việt trong `melo/text/symbols.py`.
3. Tùy chỉnh mô hình BERT trong `melo/text/vietnamese_bert.py` để sử dụng mô hình phù hợp hơn.

## Tài liệu tham khảo

- [PhoBERT: Pre-trained language models for Vietnamese](https://github.com/VinAIResearch/PhoBERT)
- [Underthesea: Vietnamese NLP Toolkit](https://github.com/undertheseanlp/underthesea)
- [PyVi: Vietnamese NLP in Python](https://github.com/trungtv/pyvi) 