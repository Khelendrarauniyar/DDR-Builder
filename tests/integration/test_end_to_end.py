from pathlib import Path


def test_project_structure_exists():
    assert Path("src/main.py").exists()
    assert Path("src/pipeline_runner.py").exists()
    assert Path("src/report/ddr_composer.py").exists()
