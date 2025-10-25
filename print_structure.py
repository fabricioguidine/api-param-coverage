import os
from datetime import datetime

def tree(base='.', indent='', file=None):
    for entry in sorted(os.listdir(base)):
        if entry in {'.venv', '.git', '__pycache__'}:
            continue
        path = os.path.join(base, entry)
        line = indent + '├── ' + entry
        print(line)
        if file:
            file.write(line + '\n')
        if os.path.isdir(path):
            tree(path, indent + '│   ', file=file)

if __name__ == '__main__':
    os.makedirs('outbound', exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_file = f'outbound/project_structure_{ts}.txt'
    with open(out_file, 'w', encoding='utf-8') as f:
        tree('.', file=f)
    print('Saved to', out_file)
