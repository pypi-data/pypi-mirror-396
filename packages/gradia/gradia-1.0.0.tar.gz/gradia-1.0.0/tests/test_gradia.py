import os
import shutil
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from fastapi.testclient import TestClient

# Import Application Code
from gradia.core.inspector import Inspector
from gradia.core.scenario import ScenarioInferrer
from gradia.core.config import ConfigManager
from gradia.viz.server import app, RUN_DIR
from gradia.models.sklearn_wrappers import ModelFactory

# Setup
TEST_CSV = "test_data.csv"
TEST_RUN_DIR = Path("test_runs")

@pytest.fixture(scope="module")
def setup_environment():
    # 1. Create Dummy CSV
    df = pd.DataFrame({
        'feature1': np.random.rand(50),
        'feature2': np.random.rand(50),
        'label': np.random.randint(0, 2, 50) # Classification
    })
    df.to_csv(TEST_CSV, index=False)
    
    # Clean previous test runs
    if TEST_RUN_DIR.exists():
        shutil.rmtree(TEST_RUN_DIR)
    TEST_RUN_DIR.mkdir()
    
    yield
    
    # Cleanup
    if os.path.exists(TEST_CSV):
        try: os.remove(TEST_CSV)
        except: pass
    if TEST_RUN_DIR.exists():
        shutil.rmtree(TEST_RUN_DIR)

def test_scenario_inference(setup_environment):
    """Verify that Gradia correctly detects task type from CSV."""
    # inspector finds files
    inspector = Inspector(Path("."))
    datasets = inspector.find_datasets()
    
    # filter for our test file
    test_ds = next((d for d in datasets if d.name == TEST_CSV), None)
    assert test_ds is not None, f"{TEST_CSV} not found by inspector. Found: {datasets}"
    
    inferrer = ScenarioInferrer()
    scenario = inferrer.infer(str(test_ds), target_override='label')
    
    assert scenario.task_type == 'classification'
    assert 'feature1' in scenario.features

def test_model_suggestion(setup_environment):
    """Verify smart model suggestion logic."""
    inferrer = ScenarioInferrer()
    # Direct inference on path
    scenario = inferrer.infer(TEST_CSV, target_override='label')
    
    suggestion = scenario.recommended_model
    # Simple small dataset -> likely rf or svm
    assert suggestion in ['random_forest', 'svm', 'mlp', 'cnn', 'logreg', 'rf']

def test_api_endpoints(setup_environment):
    """Verify FastAPI server flows."""
    client = TestClient(app)
    
    # 1. Root should redirect because TRAINER is None
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/configure"
    
    # 2. Configure page should load (requires SCENARIO init)
    from gradia.viz import server
    
    # Manually inject state
    inferrer = ScenarioInferrer()
    scenario = inferrer.infer(TEST_CSV, target_override='label')
    
    server.SCENARIO = scenario
    server.CONFIG_MGR = ConfigManager(TEST_RUN_DIR)
    config = server.CONFIG_MGR.load_or_create() # Ensure config loaded
    server.RUN_DIR = TEST_RUN_DIR
    server.DEFAULT_CONFIG = config # Sync defaults
    
    response = client.get("/configure")
    assert response.status_code == 200
    assert "Configure Experiment" in response.text
    
    # 3. Test Report endpoint
    response = client.get("/api/report/json")
    # Even if 404 because file missing, it shouldn't crash
    assert response.status_code in [200, 404]

def test_end_to_end_training_trigger(setup_environment):
    """Verify that the API can trigger training (MOCK)."""
    client = TestClient(app)
    
    payload = {
        "model": {"type": "rf", "params": {"n_estimators": 10}},
        "training": {"epochs": 1},
        "project_name": "test_ci",
        "save_model": False
    }
    
    # Ensure server.py is in a state to accept this (TRAINER starts thread)
    from gradia.viz import server
    
    # Ensure DEFAULT_CONFIG has structure
    if not server.DEFAULT_CONFIG:
         server.CONFIG_MGR = ConfigManager(TEST_RUN_DIR)
         server.DEFAULT_CONFIG = server.CONFIG_MGR.load_or_create()
    
    # Also ensure SCENARIO is set so Trainer can init
    if server.SCENARIO is None:
        inferrer = ScenarioInferrer()
        server.SCENARIO = inferrer.infer(TEST_CSV, target_override='label')
    
    response = client.post("/api/start", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "started"}
    
    import time
    time.sleep(1.5) 
    
    assert server.TRAINER is not None
    # Verify thread started
    assert server.TRAINING_THREAD is not None
