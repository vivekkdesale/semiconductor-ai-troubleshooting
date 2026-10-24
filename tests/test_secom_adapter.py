from datetime import UTC

import pytest

from semiconductor.adapters.secom import SecomAdapter


def test_loads_and_normalizes_secom(secom_files):
    records = list(SecomAdapter().load(*secom_files))
    assert len(records) == 2
    assert records[0].source_key == "secom-000000"
    assert records[0].outcome == "pass"
    assert records[1].outcome == "fail"
    assert len(records[0].values) == 590
    assert records[0].values[1] is None
    assert records[0].missing_count == 1
    assert records[0].observed_at.tzinfo == UTC


def test_rejects_row_mismatch(secom_files):
    features, labels = secom_files
    labels.write_text("-1 19/07/2008 11:55:00\n", encoding="utf-8")
    with pytest.raises(ValueError, match="row mismatch"):
        list(SecomAdapter().load(features, labels))


def test_rejects_wrong_sensor_count(tmp_path):
    features = tmp_path / "features"
    labels = tmp_path / "labels"
    features.write_text("1 2 3\n", encoding="utf-8")
    labels.write_text("-1 19/07/2008 11:55:00\n", encoding="utf-8")
    with pytest.raises(ValueError, match="590"):
        list(SecomAdapter().load(features, labels))
