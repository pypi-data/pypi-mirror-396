import argparse
import sys
from .core.api import tensor7
from .bridge import text_to_tensor, encode_sequence
from .vis import plot_tensor_ascii, plot_attractor_trajectory
from .server import run as run_server


def main():
    parser = argparse.ArgumentParser(
        prog="cmfo",
        description="CMFO – Fractal Universal Computation Engine"
    )

    sub = parser.add_subparsers(dest="cmd", help="Subcommands")

    # Command: tensor7
    t7 = sub.add_parser("tensor7", help="Compute Tensor7 operator")
    t7.add_argument("a", type=float, help="First scalar input")
    t7.add_argument("b", type=float, help="Second scalar input")

    # Command: encode
    enc = sub.add_parser("encode", help="Convert text to T7 vector")
    enc.add_argument("text", type=str, help="Text to encode")

    # Command: visualize
    vis = sub.add_parser("visualize", help="Visualize text attractor")
    vis.add_argument("text", type=str, help="Text to visualize")

    # Command: serve
    srv = sub.add_parser("serve", help="Start HTTP API Server")
    srv.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to listen on")

    args = parser.parse_args()

    if args.cmd == "tensor7":
        result = tensor7(args.a, args.b)
        print(result)

    elif args.cmd == "encode":
        result = text_to_tensor(args.text)
        print(f"Text: '{args.text}'")
        print("Fractal Vector:", result)

    elif args.cmd == "visualize":
        print(f"Visualizing resonance for: '{args.text}'")

        # 1. Final State
        final_state = text_to_tensor(args.text)
        plot_tensor_ascii(final_state, label="Final Attractor State")

        # 2. Trajectory
        seq = encode_sequence(args.text)
        plot_attractor_trajectory(seq)

    elif args.cmd == "serve":
        run_server(port=args.port)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
