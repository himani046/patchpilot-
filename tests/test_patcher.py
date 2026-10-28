import pytest
from app.schemas import FileChange, RepairPatch
from app.tools.patcher import apply_patch


def test_patch_changes_approved_file(tmp_path):
    target = tmp_path / "billing.py"
    target.write_text("def calculate():\n    return 1\n", encoding="utf-8")
    patch = RepairPatch(changes=[FileChange(path="billing.py", content="def calculate():\n    return 2\n")])
    assert apply_patch(str(tmp_path), patch, ["billing.py"]) == ["billing.py"]
    assert "return 2" in target.read_text(encoding="utf-8")


def test_patch_rejects_path_traversal(tmp_path):
    patch = RepairPatch(changes=[FileChange(path="../outside.py", content="unsafe")])
    with pytest.raises(ValueError):
        apply_patch(str(tmp_path), patch, ["../outside.py"])


def test_patch_does_not_write_when_later_change_invalid(tmp_path):
    target = tmp_path / "good.py"
    target.write_text("safe", encoding="utf-8")
    patch = RepairPatch(changes=[FileChange(path="good.py", content="changed"), FileChange(path="../outside.py", content="unsafe")])
    with pytest.raises(ValueError):
        apply_patch(str(tmp_path), patch, ["good.py", "../outside.py"])
    assert target.read_text(encoding="utf-8") == "safe"
