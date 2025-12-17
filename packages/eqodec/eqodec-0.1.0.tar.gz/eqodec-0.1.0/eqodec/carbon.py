from codecarbon import EmissionsTracker

def get_local_carbon_intensity(default: float = 0.4) -> float:
    """
    Attempts to infer local carbon intensity (kgCO2/kWh).
    Falls back to default if unavailable.
    """
    tracker = EmissionsTracker(
        project_name="eqodec_intensity_probe",
        log_level="error",
        save_to_file=False
    )
    tracker.start()
    tracker.stop()

    try:
        rate = tracker._emissions.emissions_rate
        return rate if rate and rate > 0 else default
    except Exception:
        return default