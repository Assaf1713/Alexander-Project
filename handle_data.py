with open('data.json', 'rb') as f:
    content = f.read()

# Check and remove BOM if present
if content.startswith(b'\xef\xbb\xbf'):
    content = content[3:]

with open('data.json', 'wb') as f:
    f.write(content)
