import os
import argparse


### Sanity checks: on failure, makes no sense to continue
def sanity_checks(args: argparse.ArgumentParser):
    if args.input_filename is None:
        print("No input file provided.")
        return False

    if args.output_filename is None:
        print("No output file provided.")
        return False

    # Debug output
    if args.verbose:
        print('Input filename:', args.input_filename)
        print('Output filename:', args.output_filename)
        print()

    return True


def argparsing():
    # Parser
    parser = argparse.ArgumentParser(os.path.basename(__file__))
    parser.add_argument("-v", "--verbose",
                        dest='verbose',
                        help="Verbose mode. Default is off",
                        action="store_true",
                        default=False)
    parser.add_argument("--parallel",
                        dest='parallel',
                        help="Use parallel approachauthentication key.",
                        action="store_true",
                        default=False)
    parser.add_argument("-i", "--input-filename",
                        dest='input_filename',
                        help="Input filename.",
                        default=None,
                        type=str)
    parser.add_argument("-o", "--output-filename",
                        dest='output_filename',
                        help="Output filename.",
                        default=None,
                        type=str)

    args = parser.parse_args()
    if args is None:
        parser.print_usage()
        return None

    return args