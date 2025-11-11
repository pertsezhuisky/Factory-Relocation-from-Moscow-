import os

def get_user_choice_directories():
    print("Поиск папок в текущей директории...")
    all_dirs = []
    for item in os.listdir('.'):
        if os.path.isdir(item) and item not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.obsidian'}:
            all_dirs.append(item)

    if not all_dirs:
        print("Дополнительных папок не найдено.")
        return []

    print("\nНайденные папки:")
    for i, d in enumerate(all_dirs):
        print(f"{i+1}. {d}")

    print("\nВведите номера папок, которые нужно также включить (через запятую, Enter для пропуска):")
    try:
        choice_input = input().strip()
        if not choice_input:
            return []
        selected_indices = [int(x.strip()) - 1 for x in choice_input.split(',')]
        selected_dirs = [all_dirs[i] for i in selected_indices if 0 <= i < len(all_dirs)]
        print(f"Выбраны папки: {selected_dirs}")
        return selected_dirs
    except ValueError:
        print("Некорректный ввод. Папки не выбраны.")
        return []

def collect_code_files_to_markdown(output_file, extensions, extra_dirs=None):
    all_dirs_to_scan = {'.', *(extra_dirs or [])}
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for dir_path in all_dirs_to_scan:
            for root, dirs, files in os.walk(dir_path):
                # Исключаем системные папки
                dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.obsidian'}]
                for file in files:
                    if any(file.endswith(ext) for ext in extensions):
                        filepath = os.path.join(root, file)
                        # Относительный путь для заголовка
                        rel_path = os.path.relpath(filepath, '.')
                        out_file.write(f"## `{rel_path}`\n\n")
                        out_file.write(f"```{file.split('.')[-1]}\n")
                        try:
                            with open(filepath, 'r', encoding='utf-8') as code_file:
                                out_file.write(code_file.read())
                        except Exception as e:
                            out_file.write(f"<!-- Error reading file: {e} -->\n")
                        out_file.write("\n```\n\n")

# --- Основной код ---
output_markdown = 'collected_code.md'
file_extensions = ['.py', '.js', '.html', '.css', '.ts', '.jsx', '.json', '.md']

extra_dirs = get_user_choice_directories()

collect_code_files_to_markdown(output_markdown, file_extensions, extra_dirs)
print(f"\nКод из файлов успешно собран в {output_markdown}")