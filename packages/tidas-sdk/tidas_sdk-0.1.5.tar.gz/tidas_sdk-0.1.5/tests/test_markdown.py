from pathlib import Path

from tidas_sdk import create_flow_from_json, create_process_from_json

# cd sdks/python
# uv run python -m pytest tests/test_markdown.py

DATA_DIR = Path(__file__).resolve().parents[3] / "test-data"


def _data_path(name: str) -> Path:
    return DATA_DIR / name


def test_process_to_markdown_contains_core_fields() -> None:
    process = create_process_from_json(_data_path("tidas-example-process.json"))
    markdown = process.to_markdown(lang="en")
    _data_path("tidas-example-process.md").write_text(markdown, encoding="utf-8")

    assert "Entity:** Process" in markdown
    assert "Municipal sludge treatment and disposal" in markdown
    assert "ecb914eb-6f1f-4df9-8289-d9ee519386f4" in markdown
    assert "Sludge" in markdown
    assert "1000" in markdown
    assert "Classification:** Water supply; sewerage, waste management and remediation activities" in markdown
    assert "**Version:** 01.01.001" in markdown


def test_flow_to_markdown_contains_core_fields() -> None:
    flow = create_flow_from_json(_data_path("tidas-example-flow.json"))
    markdown = flow.to_markdown(lang="en")
    _data_path("tidas-example-flow.md").write_text(markdown, encoding="utf-8")

    assert "Entity:** Flow" in markdown
    assert "2-chloro-3-methyl-4-(methylsulfonyl) benzoic acid" in markdown
    assert "4d8a3345-51fd-44ac-87e0-59bc8d3b0fdc" in markdown
    assert "106904-09-0" in markdown
    assert "Classification:** Emissions > Emissions to air > Emissions to lower stratosphere and upper troposphere" in markdown
    assert "Mass" in markdown
    assert "1" in markdown
