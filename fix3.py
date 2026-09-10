with open('main.py', 'r', encoding='utf-8') as f: text = f.read()

text = text.replace('ft.margin.only(top=40, left=40, right=40, bottom=10)', 'ft.Margin(top=40, left=40, right=40, bottom=10)')
text = text.replace('ft.margin.only(left=40, right=40, bottom=40)', 'ft.Margin(left=40, right=40, bottom=40, top=0)')
text = text.replace('ft.margin.symmetric(horizontal=40, vertical=10)', 'ft.Margin(left=40, right=40, top=10, bottom=10)')
text = text.replace('ft.border.only(right=ft.border.BorderSide(1, "#4dffffff"))', 'ft.Border(right=ft.BorderSide(1, "#4dffffff"))')
text = text.replace('ft.border.only(right=ft.border.BorderSide(1, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)))', 'ft.Border(right=ft.BorderSide(1, "#4dffffff"))')
text = text.replace('ft.border.only(right=ft.border.BorderSide(1, ft.colors.with_opacity(0.3, ft.colors.WHITE)))', 'ft.Border(right=ft.BorderSide(1, "#4dffffff"))')

# Let's also fix ElevatedButton to ElevatedButton or Button
text = text.replace('ft.ElevatedButton', 'ft.ElevatedButton') # Deprecation warning is fine, won't crash
text = text.replace('ft.TextButton', 'ft.TextButton')

with open('main.py', 'w', encoding='utf-8') as f: f.write(text)
print('Fixed Flet Margin/Border API changes!')
