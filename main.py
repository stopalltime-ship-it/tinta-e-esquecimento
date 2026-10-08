"""Execute com python main.py. As opções extras servem à verificação da build."""
import argparse
import os
from pathlib import Path
import sys
import traceback


def main():
    parser=argparse.ArgumentParser(description="Tinta e Esquecimento")
    parser.add_argument("--smoke-test",action="store_true",help="Abre três quadros sem dispositivo de vídeo/áudio.")
    parser.add_argument("--frames",type=int)
    parser.add_argument("--screenshot")
    parser.add_argument("--scene",choices=["menu","fase1","fase2","chefe","final"],default="menu")
    args=parser.parse_args()
    if args.smoke_test:
        os.environ["SDL_VIDEODRIVER"]="dummy"
        os.environ["SDL_AUDIODRIVER"]="dummy"
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"]="1"
    from game.app import Game
    game=Game()
    if args.scene in ("fase1","fase2","chefe"):
        game.start_chapter({"fase1":0,"fase2":1,"chefe":2}[args.scene])
        game.state="play"
    elif args.scene == "final":
        game.state="ending"
        game.signature="Ilo"
    game.run(args.frames or (3 if args.smoke_test else None),args.screenshot)


def report_error(error):
    """Preserva o diagnóstico mesmo na build Windows sem console."""
    root=Path(sys.executable).parent if getattr(sys,"frozen",False) else Path(__file__).resolve().parent
    detail="".join(traceback.format_exception(type(error),error,error.__traceback__))
    if isinstance(error,ModuleNotFoundError) and error.name == "pygame":
        message="Pygame não está instalado neste Python. Execute preparar_windows.bat na pasta do código e tente novamente com F5 ou jogar.bat."
    elif isinstance(error,FileNotFoundError):
        message="Um arquivo necessário não foi encontrado. Extraia o ZIP inteiro e mantenha a pasta assets junto de main.py ou do executável."
    else:
        message=f"O jogo não conseguiu iniciar ou continuar: {error}"
    # O projeto pode estar em uma pasta sem permissão de escrita.
    fallback=Path(os.environ.get("LOCALAPPDATA",str(Path.home()))) / "TintaEEsquecimento"
    for folder in (root/"logs",fallback):
        try:
            folder.mkdir(parents=True,exist_ok=True)
            log=folder/"erro-jogo.txt"
            log.write_text(f"Python: {sys.version}\nInterpretador: {sys.executable}\nProjeto: {root}\n\n{detail}",encoding="utf-8")
            message+=f"\n\nDetalhes do erro: {log}"
            break
        except OSError:
            continue
    if sys.stderr is not None:
        print(message,file=sys.stderr)
        print(detail,file=sys.stderr)
    if getattr(sys,"frozen",False) and sys.platform == "win32" and "--smoke-test" not in sys.argv:
        import ctypes
        ctypes.windll.user32.MessageBoxW(None,message,"Tinta e Esquecimento — erro",0x10)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        report_error(error)
        raise SystemExit(1)
