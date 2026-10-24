import uuid
from unittest.mock import MagicMock

from semiconductor.services import create_investigation


def test_create_investigation_commits_and_refreshes():
    session = MagicMock()
    run_id = uuid.uuid4()
    result = create_investigation(session, run_id, "Investigate abnormal sensor cluster")
    assert result.run_id == run_id
    assert result.summary.startswith("Investigate")
    session.add.assert_called_once_with(result)
    session.commit.assert_called_once()
    session.refresh.assert_called_once_with(result)
