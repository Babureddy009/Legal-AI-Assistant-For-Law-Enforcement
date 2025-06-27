import json

with open('ipc_sections.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for section in data.get('sections', []):
    # Remove punishment if it is empty
    if 'punishment' in section and section['punishment'] == '':
        del section['punishment']
    # Remove punishment if it is the same as description
    elif 'punishment' in section and 'description' in section and section['punishment'].strip() == section['description'].strip():
        del section['punishment']

with open('ipc_sections.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print('Cleaned ipc_sections.json: removed empty or duplicate punishment fields.') 