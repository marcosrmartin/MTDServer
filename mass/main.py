import argparse
from logging import DEBUG, INFO
from .config import configure_logging
from .mtd_controller import MTDController

def main():
    parser = argparse.ArgumentParser(
                        prog='mass',
                        description='MASS MTD which rotates between Nginx and HTTPD servers'
                        )

    parser.add_argument('-d', '--duration', type=int, help="Total duration of the MASS life.", default=300)
    parser.add_argument('-l', '--lower', type=int, help="Lower time for the time bounds.", default=11)
    parser.add_argument('-u', '--upper', type=int, help="Upper time for the time bounds.", default=15)
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        configure_logging(DEBUG)
    else:
        configure_logging(INFO)

    mtd = MTDController(args.duration, args.lower, args.upper)
    mtd.start()

if __name__ == "__main__":
    main()
