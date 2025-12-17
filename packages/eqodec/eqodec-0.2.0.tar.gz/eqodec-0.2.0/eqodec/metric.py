def energy_efficiency_score(
    baseline_bytes: float,
    compressed_bytes: float,
    kg_co2: float
) -> float:
    """
    Energy-Efficiency Score (EES)

    EES = GB_saved / kgCO2
    """
    if kg_co2 <= 0:
        return float("nan")

    gb_saved = (baseline_bytes - compressed_bytes) / (1024 ** 3)
    return gb_saved / kg_co2