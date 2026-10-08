"""Verifica falhas de instalação e caminhos usando o ponto de entrada real."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT=Path(__file__).resolve().parent.parent


class Startup(unittest.TestCase):
    def launch(self,root,cwd,without_packages=False):
        command=[sys.executable]
        if without_packages:
            command.append("-S")
        command.extend([str(root/"main.py"),"--smoke-test","--scene","chefe"])
        env=os.environ.copy()
        env["PYTHONIOENCODING"]="utf-8"
        return subprocess.run(command,cwd=cwd,env=env,capture_output=True,
                              text=True,encoding="utf-8",timeout=30)

    def copy_project(self,destination):
        shutil.copy2(ROOT/"main.py",destination/"main.py")
        shutil.copytree(ROOT/"game",destination/"game",
                        ignore=shutil.ignore_patterns("__pycache__","*.pyc"))

    def test_launch_from_unrelated_working_directory(self):
        with tempfile.TemporaryDirectory(prefix="outra pasta ") as cwd:
            result=self.launch(ROOT,cwd)
            self.assertEqual(result.returncode,0,result.stderr)

    def test_missing_pygame_reports_how_to_install(self):
        with tempfile.TemporaryDirectory(prefix="jogo sem pacotes ") as folder:
            project=Path(folder)
            self.copy_project(project)
            result=self.launch(project,project,without_packages=True)
            self.assertEqual(result.returncode,1,result.stderr)
            self.assertIn("preparar_windows.bat",result.stderr)
            self.assertIn("pygame",(project/"logs"/"erro-jogo.txt").read_text(encoding="utf-8"))

    def test_missing_asset_reports_incomplete_package(self):
        with tempfile.TemporaryDirectory(prefix="jogo incompleto ") as folder:
            project=Path(folder)
            self.copy_project(project)
            shutil.copytree(ROOT/"assets",project/"assets")
            (project/"assets"/"story.json").unlink()
            result=self.launch(project,project)
            self.assertEqual(result.returncode,1,result.stderr)
            self.assertIn("Extraia o ZIP inteiro",result.stderr)
            self.assertIn("story.json",(project/"logs"/"erro-jogo.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
