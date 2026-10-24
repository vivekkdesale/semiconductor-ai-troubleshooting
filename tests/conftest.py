from pathlib import Path

import pytest


@pytest.fixture
def secom_files(tmp_path: Path) -> tuple[Path, Path]:
    features = tmp_path / "secom.data"
    labels = tmp_path / "secom_labels.data"
    row1 = " ".join(["1.5", "NaN"] + [str(index) for index in range(2, 590)])
    row2 = " ".join(["2.5"] * 590)
    features.write_text(row1 + "\n" + row2 + "\n", encoding="utf-8")
    labels.write_text("-1 19/07/2008 11:55:00\n1 19/07/2008 12:05:00\n", encoding="utf-8")
    return features, labels
