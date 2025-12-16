from dataclasses import dataclass


@dataclass
class TableNames:
    """
    Names of ESO tables
    """
    observations = "ivoa.ObsCore"


@dataclass
class MockData:
    observations = "~/Repos/salutator/.mock_data/select_all_obscore.csv"


TAP_URL = "https://archive.eso.org/tap_obs"
