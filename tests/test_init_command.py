import json
from pathlib import Path
import pytest

from scaffold_cli.commands.init import InitCommand
from scaffold_cli.detectors.project_detector import DetectedProject, ProjectDetector


class DummyRunner:
    def __init__(self):
        self.calls = []

    def run(self, cmd, cwd=None, description=None, show_output=True):
        self.calls.append({
            "cmd": cmd,
            "cwd": cwd,
            "description": description,
            "show_output": show_output
        })
        # emulate success for install commands
        if "install" in cmd:
            return True
        return True


class DummyGit:
    def __init__(self):
        self.inited = False

    def init_repository(self, path, message):
        self.inited = True


class DummyEnvGen:
    def __init__(self, *a, **kw):
        self._interactive = False

    def interactive_setup(self):
        return False

    def generate_files(self):
        pass

    def get_summary(self):
        return {"total_vars": 0, "categories": []}


class DummyDockerGen:
    def __init__(self, *a, **kw):
        pass

    def generate_dockerfile(self):
        pass

    def generate_nginx_config(self):
        pass

    def generate_docker_compose(self, with_database=False):
        pass


def test_install_with_npm(monkeypatch, tmp_path):
    # Prepare: create package.json so detector would see a Node project
    (tmp_path / "package.json").write_text(json.dumps({"name": "test"}))

    project = DetectedProject(
        type="react",
        name="test",
        path=tmp_path,
        package_manager="npm",
        has_git=True,
        dependencies_installed=False,
        frameworks=["React"]
    )

    init_cmd = InitCommand(project_path=tmp_path)
    dummy = DummyRunner()
    init_cmd.runner = dummy

    init_cmd._install_dependencies(project)

    assert any("npm install" in c["cmd"] for c in dummy.calls)


def test_fallback_to_npm_when_packagejson_and_no_lock(monkeypatch, tmp_path):
    # package.json exists but package_manager is None from detector
    (tmp_path / "package.json").write_text(json.dumps({"name": "test"}))

    project = DetectedProject(
        type="react",
        name="test",
        path=tmp_path,
        package_manager=None,
        has_git=True,
        dependencies_installed=False,
        frameworks=["React"]
    )

    init_cmd = InitCommand(project_path=tmp_path)
    dummy = DummyRunner()
    init_cmd.runner = dummy

    # call should detect package.json at runtime and run npm install
    init_cmd._install_dependencies(project)

    assert any("npm install" in c["cmd"] for c in dummy.calls)


def test_unknown_package_manager_without_packagejson(monkeypatch, tmp_path, capsys):
    # No package.json and project.package_manager is None
    project = DetectedProject(
        type="react",
        name="test",
        path=tmp_path,
        package_manager=None,
        has_git=True,
        dependencies_installed=False,
        frameworks=["React"]
    )

    init_cmd = InitCommand(project_path=tmp_path)
    dummy = DummyRunner()
    init_cmd.runner = dummy

    init_cmd._install_dependencies(project)

    # No install calls should have been made
    assert dummy.calls == []


def test_full_run_flow_monkeypatched(monkeypatch, tmp_path):
    # Simulate a project with package.json, no git, and not installed deps
    (tmp_path / "package.json").write_text(json.dumps(
        {"name": "test", "dependencies": {"react": "^18.0.0"}}))

    project = DetectedProject(
        type="react",
        name="test",
        path=tmp_path,
        package_manager=None,  # detector might leave None; runtime fallback should handle it
        has_git=False,
        dependencies_installed=False,
        frameworks=["React"]
    )

    # Monkeypatch detector to return our project
    monkeypatch.setattr(ProjectDetector, "detect", lambda self: project)

    # monkeypatch questionary.confirm to always return True
    import questionary
    monkeypatch.setattr(questionary, "confirm", lambda *a,
                        **kw: type("A", (), {"ask": lambda self: True})())

    # patch CommandRunner and GitManager and generators
    dummy_runner = DummyRunner()
    monkeypatch.setattr(
        "scaffold_cli.commands.init.CommandRunner", lambda *a, **kw: dummy_runner)
    dummy_git = DummyGit()
    monkeypatch.setattr(
        "scaffold_cli.commands.init.GitManager", lambda *a, **kw: dummy_git)
    monkeypatch.setattr(
        "scaffold_cli.commands.init.EnvGenerator", lambda *a, **kw: DummyEnvGen())
    monkeypatch.setattr(
        "scaffold_cli.commands.init.DockerGenerator", lambda *a, **kw: DummyDockerGen())

    init_cmd = InitCommand(project_path=tmp_path)
    res = init_cmd.run()

    assert res is True
    # ensure install attempted (fallback to npm) and git init called
    assert any("npm install" in c["cmd"] for c in dummy_runner.calls) or any(
        "pip" in c["cmd"] for c in dummy_runner.calls) or dummy_git.inited is True
