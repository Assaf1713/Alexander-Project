import chardet

with open('data.json', 'rb') as f:
    result = chardet.detect(f.read())
    print(result)
