import pandas as pd

print("="*80)
print("ПРОВЕРКА ОТЧЕТОВ")
print("="*80)

# Проверка warehouse_analysis_report.xlsx
try:
    xls = pd.ExcelFile('output/warehouse_analysis_report.xlsx')
    print(f"\nwarehouse_analysis_report.xlsx: {len(xls.sheet_names)} вкладок")
    for i, sheet in enumerate(xls.sheet_names, 1):
        df = pd.read_excel(xls, sheet_name=sheet)
        print(f"  {i}. {sheet} ({len(df)} строк)")
except Exception as e:
    print(f"Ошибка при чтении warehouse_analysis_report.xlsx: {e}")

# Проверка validation_report.xlsx
try:
    xls = pd.ExcelFile('output/validation_report.xlsx')
    print(f"\nvalidation_report.xlsx: {len(xls.sheet_names)} вкладок")
    for i, sheet in enumerate(xls.sheet_names, 1):
        df = pd.read_excel(xls, sheet_name=sheet)
        print(f"  {i}. {sheet} ({len(df)} строк)")
except Exception as e:
    print(f"Ошибка при чтении validation_report.xlsx: {e}")

print("\n" + "="*80)
