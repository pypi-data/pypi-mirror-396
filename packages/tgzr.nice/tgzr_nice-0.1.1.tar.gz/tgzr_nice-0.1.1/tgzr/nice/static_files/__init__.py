from pathlib import Path

from nicegui import app


def register():
    static_file_path = (Path(__file__) / "..").resolve()

    assets_path = static_file_path / "tgzr_assets"
    app.add_static_files("/tgzr_assets", assets_path)

    medias_path = static_file_path / "tgzr_medias"
    app.add_media_files("/tgzr_medias", medias_path)


def get_asset_ref(group: str, name: str) -> str:
    return f"tgzr_assets/{group}/{name}"


def get_asset_path(group: str, name: str) -> Path:
    return (Path(__file__) / ".." / "tgzr_assets" / group / name).resolve()


def get_asset_content(group: str, name: str) -> str:
    with open(get_asset_path(group, name), "r") as fp:
        content = fp.read()
    return content


def get_media_ref(group: str, name: str) -> str:
    return f"tgzr_medias/{group}/{name}"


def get_media_path(group: str, name: str) -> Path:
    return (Path(__file__) / ".." / "tgzr_medias" / group / name).resolve()
