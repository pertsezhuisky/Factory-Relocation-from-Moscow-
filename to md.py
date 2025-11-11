import os

def collect_code_files_to_markdown(output_file, extensions):
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for root, dirs, files in os.walk('.'):
            # Пропускаем папку .git и другие системные/виртуальные окружения
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}]
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    filepath = os.path.join(root, file)
                    # Пишем имя файла и его содержимое
                    out_file.write(f"## `{file}`\n\n")
                    out_file.write(f"```{file.split('.')[-1]}\n")
                    try:
                        with open(filepath, 'r', encoding='utf-8') as code_file:
                            out_file.write(code_file.read())
                    except Exception as e:
                        out_file.write(f"<!-- Error reading file: {e} -->\n")
                    out_file.write("\n```\n\n")

# Укажите имя выходного файла
output_markdown = 'collected_code.md'
# Укажите нужные расширения файлов
file_extensions = ['.py', '.js', '.html', '.css', '.ts', '.jsx', '.json', '.md']

collect_code_files_to_markdown(output_markdown, file_extensions)
print(f"Код из файлов успешно собран в {output_markdown}")