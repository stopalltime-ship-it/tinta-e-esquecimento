"""Gera a entrega Windows completa. Execute este script em Windows."""
from pathlib import Path
import importlib.metadata
import hashlib
import os
import shutil
import subprocess
import sys
from build_source import build_source


def main():
    if sys.platform != "win32":
        raise SystemExit("Execute em Windows ou use a build automática do GitHub Actions.")
    root=Path(__file__).resolve().parent
    os.chdir(root)
    subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-v"],check=True)
    subprocess.run([sys.executable,"-m","PyInstaller","--noconfirm","--clean","--onedir",
                    "--windowed","--noupx","--name","TintaEEsquecimento","main.py"],check=True)
    output=root/"dist"/"TintaEEsquecimento"
    shutil.copytree(root/"assets",output/"assets",dirs_exist_ok=True)
    for name in ("LEIA-ME.txt","CREDITOS.md"):
        shutil.copy2(root/name,output/name)
    # Preservar os avisos da biblioteca distribuída junto com o executável.
    notices=output/"licencas-pygame"
    notices.mkdir(exist_ok=True)
    distribution=importlib.metadata.distribution("pygame")
    for entry in distribution.files or []:
        if entry.name.lower() in ("copying","license","license.txt","copying.txt","lgpl.txt"):
            origin=Path(distribution.locate_file(entry))
            if origin.is_file():
                shutil.copy2(origin,notices/entry.name)
    subprocess.run([str(output/"TintaEEsquecimento.exe"),"--smoke-test","--scene","chefe"],check=True,timeout=30)
    # A pasta assets permanece ao lado do .exe, como pede a atividade.
    archive=shutil.make_archive(str(root/"dist"/"Tinta-e-Esquecimento-Windows"),"zip",root/"dist","TintaEEsquecimento")
    source=build_source()
    checksums=[]
    for package in (Path(archive),source):
        checksums.append(f"{hashlib.sha256(package.read_bytes()).hexdigest()}  {package.name}\n")
    (root/"dist"/"SHA256SUMS.txt").write_text("".join(checksums),encoding="utf-8")
    print(f"Entrega criada: {archive}")


if __name__ == "__main__":
    main()
