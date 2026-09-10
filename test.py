import flet as ft
def main(page):
    btn = ft.ElevatedButton('test')
    page.add(btn)
    try:
        btn.content = 'Checking...'
        page.update()
        print('SUCCESS: content accepts string')
    except Exception as e:
        print(f'ERROR: {e}')
    
    try:
        btn.text = 'Checking 2...'
        page.update()
        print('SUCCESS: text accepts string')
    except Exception as e:
        print(f'ERROR: {e}')

ft.app(target=main)
