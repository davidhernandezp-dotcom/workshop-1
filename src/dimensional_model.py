def build_dim_date(df):
    dates = df[['Application Date']].drop_duplicates().reset_index(drop=True)
    dates['date_key'] = dates.index + 1
    dates['year'] = dates['Application Date'].dt.year
    dates['month'] = dates['Application Date'].dt.month
    dates['month_name'] = dates['Application Date'].dt.strftime('%B')
    dates['quarter'] = dates['Application Date'].dt.quarter
    dates = dates.rename(columns={'Application Date': 'full_date'})
    return dates


def build_dim_technology(df):
    tech = df[['Technology']].drop_duplicates().reset_index(drop=True)
    tech['technology_key'] = tech.index + 1
    tech = tech.rename(columns={'Technology': 'technology_name'})
    return tech


def build_dim_country(df):
    country = df[['Country']].drop_duplicates().reset_index(drop=True)
    country['country_key'] = country.index + 1
    country = country.rename(columns={'Country': 'country_name'})
    return country


def build_dim_profile(df):
    profile = df[['Seniority', 'yoe_range']].drop_duplicates().reset_index(drop=True)
    profile['profile_key'] = profile.index + 1
    return profile


def build_fact(df, dim_date, dim_tech, dim_country, dim_profile):
    fact = df.merge(dim_date, left_on='Application Date', right_on='full_date')
    fact = fact.merge(dim_tech, left_on='Technology', right_on='technology_name')
    fact = fact.merge(dim_country, left_on='Country', right_on='country_name')
    fact = fact.merge(dim_profile, on=['Seniority', 'yoe_range'])

    # Verifica que el merge no haya duplicado ni perdido filas
    assert len(fact) == len(df), (
        f"Error de integridad: fact tiene {len(fact)} filas, "
        f"df original tenía {len(df)}"
    )

    fact = fact[[
        'date_key', 'technology_key', 'country_key', 'profile_key',
        'Code Challenge Score', 'Technical Interview Score', 'is_hired'
    ]].reset_index(drop=True)

    fact = fact.rename(columns={
        'Code Challenge Score': 'code_challenge_score',
        'Technical Interview Score': 'technical_interview_score'
    })

    fact['application_key'] = fact.index + 1
    return fact