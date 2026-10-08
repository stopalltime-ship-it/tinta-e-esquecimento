"""Execute com python main.py. As opções extras servem à verificação da build."""
import argparse
import os


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


if __name__ == "__main__":
    main()
