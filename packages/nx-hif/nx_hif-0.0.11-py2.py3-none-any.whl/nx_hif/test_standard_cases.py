import pytest

from pathlib import Path
from nx_hif.readwrite import read_hif, encode_hif_data


@pytest.mark.parametrize("json_file", Path("data/standard").glob("*.json"))
def test_standard_cases(json_file):
    G = read_hif(json_file)
    encode_hif_data(G)
