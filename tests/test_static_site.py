"""The one Railway service answers for both surfaces.

The dashboard and the API share a port, so the mapping from request path to
file is load-bearing: `/` must be the page, `/api/*` must never resolve to
a file, `..` must not escape the directory, and the database must stay
reachable only through the API. All pinned here against the pure resolver,
with no server involved.
"""

from pathlib import Path

from carbonstack.api import _STATIC_TYPES, static_target

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "dashboard"


def test_root_serves_the_dashboard():
    target = static_target(DASH, "/")
    assert target is not None and target.name == "index.html"
    assert target.is_file()


def test_dataset_and_evidence_packs_resolve():
    assert static_target(DASH, "/data.json").is_file()
    pack = static_target(DASH, "/packs/IN-TNJ-01/SUMMARY.md")
    assert pack is not None and pack.is_file()


def test_parent_traversal_never_escapes_the_directory():
    for evil in ("/../pyproject.toml",
                 "/packs/../../pyproject.toml",
                 "/packs/IN-TNJ-01/../../../etc/hostname"):
        assert static_target(DASH, evil) is None


def test_missing_paths_and_api_routes_resolve_to_nothing():
    assert static_target(DASH, "/nope") is None
    assert static_target(DASH, "/packs/IN-TNJ-01") is None  # a directory
    assert static_target(DASH, "/api/health") is None


def test_the_database_and_the_template_are_not_published():
    """pilot.db is served through the API so every read is logged and
    authorised; template.html is build input, not the page."""
    assert static_target(DASH, "/pilot.db") is None
    assert static_target(DASH, "/template.html") is None


def test_html_gets_an_html_content_type():
    assert _STATIC_TYPES[".html"].startswith("text/html")


def test_the_container_ships_the_dashboard():
    """The image serves what it contains. If the COPY goes missing, `/`
    404s in production while every local check stays green."""
    docker = (ROOT / "Dockerfile").read_text()
    assert "COPY dashboard/" in docker
    assert "CARBONSTACK_STATIC" in docker
