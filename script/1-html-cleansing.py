import os
from bs4 import BeautifulSoup
from markdownify import markdownify as md

def modify_html_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # Rimuovere tutti i tag script
        for script in soup("script"):
            script.decompose()

        # Classi da rimuovere senza split
        classes_to_remove = [
            "content content-alert-browser",
            "content content-federation-bar content-federation-bar-minified",
            "content content-federation-bar content-federation-bar-minified content-federation-bar-simplified",
            "content content-federation-bar",
            "content content-submenu",
            "content content-header",
            "content content-footer content-footer-pre",
            "content content-footer content-footer-app",
            "content content-footer content-footer-post",
            "modal modal-spinner fade",
            "modal fade"
        ]

        for class_name in classes_to_remove:
            for div in soup.find_all("div", class_=class_name):
                div.decompose()


        # Classi da includere
        # classes_to_include = [
        #     "content-main",
        #     "content-hero",
        #     "content-pre-main",
        #     "content-post-main",
        #     "content-abstract",
        #     "content-applicative"
        # ]

        # Trovare tutti i div
        # all_divs = soup.find_all("div")

        # for div in all_divs:
        #     # Controlla se il div ha una classe che non è nell'elenco delle classi da includere
        #     if not any(class_to_include in div.get('class', '') for class_to_include in classes_to_include):
        #         div.decompose()
        
        # Rimuovere tutto tranne il tag title in head
        head = soup.head
        title_tag = head.title
        head.clear()
        head.append(title_tag)

        # Sovrascrivere il file originale con il contenuto modificato
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(str(soup))
    except Exception as e:
        print(f"Errore: {e}")

def modify_all_html_files_in_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                print(f"Modificando: {file_path}")
                modify_html_file(file_path)

modify_all_html_files_in_folder('C:/poste/www.poste.it-2')