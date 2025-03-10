rm -rf dataset
sh download-dataset.sh
python3 runner/generate-metadata.py
pip install -r requirements.txt
pip install -r OpenVoice/requirements.txt
python3 melo/preprocess_text.py --metadata dataset/metadata.list
bash melo/train.sh /melo/configs/config.json 2