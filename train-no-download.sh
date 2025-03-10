pip install -r requirements.txt
pip install -r OpenVoice/requirements.txt
python3 melo/preprocess_text.py --metadata dataset/metadata.list --config_path melo/configs/config.json
bash melo/train.sh melo/configs/config.json 2