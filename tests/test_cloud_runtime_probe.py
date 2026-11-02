from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import cloud_runtime_probe as probe


def test_probe_without_secret_makes_no_cloud_requests():
    with patch.dict('os.environ', {'ROBO_CLOUD_PROBE_ENABLED':'true', 'GOOGLE_APPLICATION_CREDENTIALS':'/missing/synthetic.json'}), patch.object(probe, 'create_ai_client') as factory, TestClient(probe.app) as client:
        assert client.get('/health').json() == {'status':'waiting_for_secret'}
        client.get('/health')
        factory.assert_not_called()


def test_health_never_reruns_probe_or_exposes_private_error():
    with patch.object(probe, 'run_probe', side_effect=RuntimeError('private-credential')) as run, TestClient(probe.app) as client:
        assert client.get('/health').json() == {'status':'failed','error_type':'RuntimeError'}
        assert 'private-credential' not in client.get('/health').text
        run.assert_called_once()
