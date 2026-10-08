"""Explicit synthetic data for presentation hardening tests and UX examples."""
from test_regression import fixture, run, zero
from test_hardening import disappearance
from data_pipeline import D, N, T, P, C, G


def recommendation_rich(store_count=6, inactive_count=0):
    locations = ['12 Rustaveli Avenue', '24 Chavchavadze Avenue', '8 Abashidze Street',
                 '17 Pekini Avenue', '31 Vazha-Pshavela Avenue', '6 Tsereteli Avenue']
    rows = []
    for month in ['July', 'August']:
        for i, address in enumerate(locations[:store_count]):
            rows.append(fixture(f'DEMO-{i+1:02}', month, **{
                'Store Name': f'Demo Pharmacy {i+1:02}',
                'Store Address Address': address + ', Tbilisi, Georgia',
                D: 200 + i * 20, N: 10000 + i * 800, T: 450 + i * 20,
                P: 140 if i == 0 else 32, C: 10,
                G: 2000 + i * 600, '% CVR': i * .01,
            }))
    for i in range(inactive_count):
        rows.append(zero(f'Inactive-{i+1}', **{'Store Address Address': f'Demo inactive branch {i+1}, Tbilisi, Georgia'}))
    return run(rows)


def no_recommendations():
    return run([fixture('Healthy Central'), fixture('Healthy North')])


def current_partial():
    return disappearance()


def historical_gap():
    return run([fixture('A', 'June'), fixture('B', 'June'), fixture('A', 'July'),
                fixture('A'), fixture('B')])
