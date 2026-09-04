from sqlalchemy import create_engine, text

DB_USER = 'root'
DB_PASSWORD = 'root'
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'recruitment_dw'


def get_engine(with_db=True):
    db_part = f'/{DB_NAME}' if with_db else ''
    url = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}{db_part}'
    return create_engine(url)


def ensure_database_exists():
    engine = get_engine(with_db=False)
    with engine.connect() as conn:
        conn.execute(text(f'CREATE DATABASE IF NOT EXISTS {DB_NAME}'))
        conn.commit()


def apply_constraints(engine):
    """Agrega llaves primarias y foráneas después de cargar los datos."""
    ddl = [
        "ALTER TABLE dim_date ADD PRIMARY KEY (date_key)",
        "ALTER TABLE dim_technology ADD PRIMARY KEY (technology_key)",
        "ALTER TABLE dim_country ADD PRIMARY KEY (country_key)",
        "ALTER TABLE dim_candidate_profile ADD PRIMARY KEY (profile_key)",
        "ALTER TABLE fact_applications ADD PRIMARY KEY (application_key)",
        "ALTER TABLE fact_applications ADD CONSTRAINT fk_date "
        "FOREIGN KEY (date_key) REFERENCES dim_date(date_key)",
        "ALTER TABLE fact_applications ADD CONSTRAINT fk_tech "
        "FOREIGN KEY (technology_key) REFERENCES dim_technology(technology_key)",
        "ALTER TABLE fact_applications ADD CONSTRAINT fk_country "
        "FOREIGN KEY (country_key) REFERENCES dim_country(country_key)",
        "ALTER TABLE fact_applications ADD CONSTRAINT fk_profile "
        "FOREIGN KEY (profile_key) REFERENCES dim_candidate_profile(profile_key)",
    ]
    with engine.connect() as conn:
        for stmt in ddl:
            conn.execute(text(stmt))
        conn.commit()
    print('Llaves primarias y foráneas aplicadas correctamente.')


def validate_load(engine):
    """Verifica conteo de filas y ausencia de referencias huérfanas."""
    with engine.connect() as conn:
        counts = {}
        for table in ['dim_date', 'dim_technology', 'dim_country',
                      'dim_candidate_profile', 'fact_applications']:
            counts[table] = conn.execute(text(f'SELECT COUNT(*) FROM {table}')).scalar()

        orphans = {}
        checks = {
            'date_key': 'dim_date',
            'technology_key': 'dim_technology',
            'country_key': 'dim_country',
            'profile_key': 'dim_candidate_profile',
        }
        for fk_col, dim_table in checks.items():
            query = text(f"""
                SELECT COUNT(*) FROM fact_applications f
                LEFT JOIN {dim_table} d ON f.{fk_col} = d.{fk_col}
                WHERE d.{fk_col} IS NULL
            """)
            orphans[fk_col] = conn.execute(query).scalar()

    print('--- Validación de carga ---')
    for table, count in counts.items():
        print(f'  {table}: {count} filas')
    print('--- Referencias huérfanas (deben ser 0) ---')
    for fk_col, n in orphans.items():
        print(f'  {fk_col}: {n}')

    if any(n > 0 for n in orphans.values()):
        raise ValueError('Se encontraron referencias inválidas en fact_applications.')


def load(dim_date, dim_tech, dim_country, dim_profile, fact):
    ensure_database_exists()
    engine = get_engine()

    dim_date.to_sql('dim_date', engine, if_exists='replace', index=False)
    dim_tech.to_sql('dim_technology', engine, if_exists='replace', index=False)
    dim_country.to_sql('dim_country', engine, if_exists='replace', index=False)
    dim_profile.to_sql('dim_candidate_profile', engine, if_exists='replace', index=False)
    fact.to_sql('fact_applications', engine, if_exists='replace', index=False)

    print(f'Base de datos "{DB_NAME}" creada/actualizada en MySQL.')

    apply_constraints(engine)
    validate_load(engine)