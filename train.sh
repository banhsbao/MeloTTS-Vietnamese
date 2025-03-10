rm -rf dataset
sh download-dataset.sh
python runner/generate-metadata.py
python melo/preprocess_text.py --metadata dataset/metadata.list
bash melo/train.sh /melo/configs/config.json 2