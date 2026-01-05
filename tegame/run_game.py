from tegame import Tegame
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run an automated simulation of 'The Game'."
    )

    parser.add_argument(
        "--players",
        type=int,
        default=2,
        choices=[2, 3, 4, 5],
        help="Number of players (2–5). Default: 2"
    )

    parser.add_argument(
        "--verb",
        type=int,
        default=2,
        choices=[0, 1, 2, 3],
        help="Verbosity level: 0=silent, 1=final, 2=story, 3=debug. Default: 2"
    )

    parser.add_argument(
        "--thresh-secondchoice",
        type=int,
        default=4,
        help="Risk tolerance for selecting a non-preferred pile. Default: 4"
    )

    parser.add_argument(
        "--thresh-nonmandatory",
        type=int,
        default=2,
        help="Max allowed damage for non-mandatory moves. Default: 2"
    )

    return parser.parse_args()




if __name__ == "__main__":
    args = parse_args()

    mygame = Tegame(
        players=args.players,
        verb_lvl=args.verb,
        thresh_secondchoice=args.thresh_secondchoice,
        thresh_nonmandatory=args.thresh_nonmandatory
    )

    mygame.run_game()