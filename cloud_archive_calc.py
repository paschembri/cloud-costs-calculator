#!/usr/bin/env python3
from dataclasses import dataclass
import streamlit as st

HOURS_PER_MONTH = 720


def format_costs(value):
    return f'{value:,.2f} €HT'.replace(',', ' ')


@dataclass
class ColdStorageProvider:
    name: str
    provider_name: str
    description: str
    at_rest_cost: float
    ingress_cost: float
    egress_cost: float
    free_tier: float = 0

    def monthly_cost(self, data_at_rest):
        if data_at_rest < self.free_tier:
            return float(0)
        return data_at_rest * self.at_rest_cost * HOURS_PER_MONTH

    def ingest_costs(self, data_to_ingest):
        if data_to_ingest < self.free_tier:
            return float(0)

        return data_to_ingest * self.ingress_cost

    def compute_tco(self, data_at_rest, data_to_ingest, months):
        initial_costs = self.ingest_costs(data_at_rest)
        incremental_costs = 0.0

        for _ in range(months):
            incremental_costs += self.monthly_cost(
                data_at_rest
            ) + self.ingest_costs(data_to_ingest)

            data_at_rest += data_to_ingest

        return initial_costs + incremental_costs


OVHCloud = ColdStorageProvider(
    'Cloud Archive',
    'OVHCloud',
    'Standard (EC 6+3)',
    float(0.0000033333),
    float(0.01),
    float(0.01),
    0,
)

Scaleway = ColdStorageProvider(
    'Glacier C14',
    'Scaleway',
    'Standard (EC 6+3)',
    float(0.00000348),
    0,
    float(0.01),
    75,
)


# Streamlit specific


st.title("Calculateur de coûts de sauvegardes")
st.header("Données d'entrées")

data_at_rest = st.slider(
    'Quel est le volume initial de données à sauvegarder ?',
    0,
    10000,
    500,
    10,
    format='%d GB',
)

monthly_data_to_ingest = st.slider(
    'Quel est le volume de données à sauvegarder mensuellement ?',
    0,
    500,
    50,
    10,
    format='%d GB',
)

months = st.slider(
    "Durée de la simulation",
    0,
    120,
    36,
    1,
    format='%d mois',
)

ovh_data_at_rest_cost = OVHCloud.ingest_costs(data_at_rest)
ovh_tco = OVHCloud.compute_tco(data_at_rest, monthly_data_to_ingest, months)

scaleway_data_at_rest_cost = Scaleway.ingest_costs(data_at_rest)
scaleway_tco = Scaleway.compute_tco(
    data_at_rest, monthly_data_to_ingest, months
)


st.header("Calculs")
st.header("Coûts d'archivage initial")

col1, col2 = st.columns(2)
col1.metric("OVHCloud", format_costs(ovh_data_at_rest_cost))
col2.metric("Scaleway", format_costs(scaleway_data_at_rest_cost))

st.header(f"Coûts totaux sur {months} mois")

col1, col2 = st.columns(2)
col1.metric("OVHCloud", format_costs(ovh_tco))
col2.metric("Scaleway", format_costs(scaleway_tco))
