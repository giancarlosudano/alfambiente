import os
from bs4 import BeautifulSoup
from markdownify import markdownify as md

def html_to_markdown(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Convertire l'HTML in Markdown
        markdown_text = md(html_content)

        with open(file_path, 'w', encoding='utf-8') as markdown_file:
            markdown_file.write(markdown_text)
    except Exception as e:
        print(f"Errore: {e}")    

def convert_all_html_files_in_md_in_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                print(f"Modificando: {file_path}")
                html_to_markdown(file_path)

convert_all_html_files_in_md_in_folder('C:/poste/www.poste.it-3')