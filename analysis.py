# analysis.py

"""
Скрипт для анализа и визуализации результатов ПОСЛЕ выполнения симуляции.
Запускается отдельно командой: python analysis.py
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import config

def plot_results():
    """
    Читает итоговый CSV, выводит данные в консоль и строит
    сравнительный график KPI для всех сценариев.
    """
    csv_path = os.path.join(config.OUTPUT_DIR, config.RESULTS_CSV_FILENAME)
    
    # Проверка, что файл с результатами существует
    if not os.path.exists(csv_path):
        print(f"Ошибка: Файл с результатами не найден по пути '{csv_path}'")
        print("Пожалуйста, сначала запустите симуляцию командой: python main.py")
        return

    # Загружаем данные. Указываем правильные разделители.
    df = pd.read_csv(csv_path, sep=';', decimal='.')
    
    print("\n" + "="*80)
    print("Загружены данные для анализа:")
    print("="*80)
    print(df.to_string(index=False))
    print("="*80 + "\n")

    # --- Настройка визуализации ---
    sns.set_theme(style="whitegrid")
    # Создаем фигуру с двумя осями Y для отображения данных разного масштаба
    fig, ax1 = plt.subplots(figsize=(13, 8))

    # Ось Y 1 (левая): Пропускная способность (столбчатая диаграмма)
    color1 = 'tab:blue'
    ax1.set_xlabel('Сценарии', fontsize=12)
    ax1.set_ylabel('Пропускная способность (обработано заказов)', color=color1, fontsize=12)
    # Используем Seaborn для красивых столбцов
    plot1 = sns.barplot(
        x='Scenario_Name', 
        y='Achieved_Throughput_Monthly', 
        data=df, 
        ax=ax1, 
        palette='Blues_d',
        label='Пропускная способность'
    )
    ax1.tick_params(axis='y', labelcolor=color1)
    # Поворачиваем подписи по оси X для лучшей читаемости
    plt.xticks(rotation=15, ha="right")

    # Ось Y 2 (правая): Годовой OPEX (линейный график)
    ax2 = ax1.twinx()  # Создаем вторую ось, которая делит ось X с первой
    color2 = 'tab:red'
    ax2.set_ylabel('Годовой OPEX (млн руб.)', color=color2, fontsize=12)
    # Рисуем линию поверх столбцов
    plot2 = sns.lineplot(
        x='Scenario_Name', 
        y=df['Total_Annual_OPEX_RUB'] / 1_000_000, 
        data=df, 
        ax=ax2, 
        color=color2, 
        marker='o', 
        linewidth=2,
        label='Годовой OPEX'
    )
    ax2.tick_params(axis='y', labelcolor=color2)
    
    # Общий заголовок и компоновка
    plt.title(f"Сравнение сценариев для локации '{df['Location_Name'][0]}'", fontsize=16, pad=20)
    fig.tight_layout()  # Автоматически подбирает отступы, чтобы ничего не обрезалось

    # Сохранение итогового изображения
    output_image_path = os.path.join(config.OUTPUT_DIR, "simulation_comparison.png")
    plt.savefig(output_image_path)
    
    print(f"[Analysis] Сравнительный график успешно сохранен: '{output_image_path}'")
    plt.show()

if __name__ == "__main__":
    plot_results()