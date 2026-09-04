import pandas as pd


def clean(df):
    """Limpia el DataFrame: nombres de columnas, tipos, duplicados y nulos."""
    df = df.copy()

    df.columns = [c.strip() for c in df.columns]
    df['Application Date'] = pd.to_datetime(df['Application Date'], errors='coerce')
    df['Country'] = df['Country'].str.strip().str.title()
    df['Seniority'] = df['Seniority'].str.strip().str.title()
    # Technology solo se limpia de espacios (no .title()) para no romper
    # nombres técnicos como "QA Manual" o "DevOps".
    df['Technology'] = df['Technology'].str.strip()

    df = df.drop_duplicates()
    df = df.dropna(subset=['Application Date', 'Code Challenge Score', 'Technical Interview Score'])

    return df


def apply_business_rules(df):
    """Aplica la regla de contratación y crea columnas derivadas."""
    df = df.copy()

    df['is_hired'] = (
        (df['Code Challenge Score'] >= 7) &
        (df['Technical Interview Score'] >= 7)
    ).astype(int)

    bins = [-1, 1, 3, 6, 100]
    labels = ['0-1', '2-3', '4-6', '7+']
    df['yoe_range'] = pd.cut(df['YOE'], bins=bins, labels=labels)

    return df