with open('main.py', 'r', encoding='utf-8') as f: text = f.read()
text = text.replace('ft.icons.', 'ft.Icons.')
with open('main.py', 'w', encoding='utf-8') as f: f.write(text)
print('Fixed Flet icons API changes!')
