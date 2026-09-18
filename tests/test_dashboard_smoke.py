from pathlib import Path


def test_dashboard_files_exist():
    """ARRANGE, ACT & ASSERT: Verifies that all mandatory components exist inside the dashboard package [INDEX]."""
    dashboard_dir = Path("src/dashboard")

    assert dashboard_dir.exists()
    assert (dashboard_dir / "app.py").exists()
    assert (dashboard_dir / "data.py").exists()
    assert (dashboard_dir / "health.py").exists()


def test_dashboard_app_compiles():
    """ARRANGE, ACT & ASSERT: Compiles app.py into an execution block to verify syntax without launching a live UI server [INDEX]."""
    app_path = Path("src/dashboard/app.py")

    source = app_path.read_text(encoding="utf-8")

    # The compile() built-in function intercepts trailing typos or structural bugs instantly [INDEX]
    compiled_code = compile(source, str(app_path), "exec")
    assert compiled_code is not None
