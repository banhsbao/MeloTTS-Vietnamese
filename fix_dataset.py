import os
import random
import json

# Read the metadata.list file
with open('dataset/metadata.list', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Shuffle the lines
random.seed(42)
random.shuffle(lines)

# Split into train and validation sets (90% train, 10% validation)
train_size = int(0.9 * len(lines))
train_lines = lines[:train_size]
val_lines = lines[train_size:]

# Write to train.list and val.list
with open('dataset/train.list', 'w', encoding='utf-8') as f:
    f.writelines(train_lines)

with open('dataset/val.list', 'w', encoding='utf-8') as f:
    f.writelines(val_lines)

print(f"Created train.list with {len(train_lines)} samples")
print(f"Created val.list with {len(val_lines)} samples")

# Update config.json with speaker IDs
speakers = set()
for line in lines:
    parts = line.strip().split('|')
    if len(parts) >= 2:
        speakers.add(parts[1])

speaker_to_id = {spk: i for i, spk in enumerate(sorted(speakers))}

print(f"Found {len(speakers)} speakers")
print(f"Speaker to ID mapping: {speaker_to_id}")

# Read the config file
with open('dataset/config.json', 'r', encoding='utf-8') as f:
    config = f.read()

# Update the config file with the speaker IDs
config_data = json.loads(config)
config_data['data']['spk2id'] = speaker_to_id
config_data['data']['n_speakers'] = len(speaker_to_id)
config_data['data']['training_files'] = 'dataset/train.list'
config_data['data']['validation_files'] = 'dataset/val.list'

# Write the updated config file
with open('dataset/config.json', 'w', encoding='utf-8') as f:
    json.dump(config_data, f, indent=2, ensure_ascii=False)

print("Updated config.json with speaker IDs and file paths") 