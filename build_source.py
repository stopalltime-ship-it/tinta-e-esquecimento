"""Cria o ZIP completo para executar e editar em VS Code, sem executáveis."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


ROOT=Path(__file__).resolve().parent
FILES=("main.py","requirements.txt","requirements-build.txt","preparar_windows.bat",
       "jogar.bat","build_windows.py","build_source.py","README.md","CREDITOS.md",
       "LEIA-ME.txt","COMECAR_NO_VSCODE.txt","RELEASE_NOTES.md",".gitignore")
FOLDERS=("game","assets","tests","docs",".vscode",".github")


def build_source():
    destination=ROOT/"dist"/"Tinta-e-Esquecimento-Fonte.zip"
    destination.parent.mkdir(exist_ok=True)
    paths=[ROOT/name for name in FILES]
    for folder in FOLDERS:
        paths.extend(path for path in (ROOT/folder).rglob("*")
                     if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc")
    with ZipFile(destination,"w",ZIP_DEFLATED) as archive:
        for path in sorted(paths):
            archive.write(path,Path("Tinta-e-Esquecimento-Fonte")/path.relative_to(ROOT))
    print(f"Código e recursos para VS Code: {destination}")
    return destination


if __name__ == "__main__":
    build_source()
