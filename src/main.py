import os

from extract import extract
from transform import clean, apply_business_rules
from dimensional_model import (
    build_dim_date, build_dim_technology, build_dim_country,
    build_dim_profile, build_fact
)
from load import load


def run():
    raw = extract()
    cleaned = clean(raw)
    enriched = apply_business_rules(cleaned)

    dim_date = build_dim_date(enriched)
    dim_tech = build_dim_technology(enriched)
    dim_country = build_dim_country(enriched)
    dim_profile = build_dim_profile(enriched)
    fact = build_fact(enriched, dim_date, dim_tech, dim_country, dim_profile)

    os.makedirs('data/processed', exist_ok=True)
    dim_date.to_csv('data/processed/dim_date.csv', index=False)
    dim_tech.to_csv('data/processed/dim_technology.csv', index=False)
    dim_country.to_csv('data/processed/dim_country.csv', index=False)
    dim_profile.to_csv('data/processed/dim_candidate_profile.csv', index=False)
    fact.to_csv('data/processed/fact_applications.csv', index=False)

    load(dim_date, dim_tech, dim_country, dim_profile, fact)

    print('Pipeline completo. Filas en fact_applications:', len(fact))


if __name__ == '__main__':
    run()