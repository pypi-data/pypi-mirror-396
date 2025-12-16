import argparse
import json


def validate_command(args):
    import tesseract.validate as validate

    args.asset_bands = None
    args.output_asset_bands = []
    args.save_output = None
    # try to parse args as JSON
    if args.args:
        try:
            json.loads(args.args)
        except json.decoder.JSONDecodeError:
            raise json.decoder.JSONDecodeError(
                "unable to parse model arguments as json"
            )

    args.test_data = None
    if args.config_file is not None:
        with open(args.config_file, "r") as cf:
            configs = json.load(cf)
        args.image = configs.get("image", None)
        args.args = configs.get("args", None)
        args.asset_bands = configs.get("asset_bands", None)
        args.test_data = configs.get("test_data", None)
        args.output_asset_bands = configs.get("output_asset_bands", [])
        args.save_output = configs.get("save_outputs", None)

    validator = validate.ValidationManager(
        image=args.image,
        test_data=args.test_data,
        asset_bands=args.asset_bands,
        cli=True,
        args=args.args,
        output_asset_bands=args.output_asset_bands,
        save_output=args.save_output,
        print_container_logs=args.print_container_logs,
    )
    validator.run()


def make_parser():
    parser = argparse.ArgumentParser(prog="tesseract-sdk")
    parser.set_defaults(func=lambda args: parser.print_help())

    subparsers = parser.add_subparsers(
        title="subcommand", description="valid subcommands", help="which action to run"
    )

    # Tesseract Model image testing
    parser_model_validation = subparsers.add_parser(
        "validate", help="validate your model container for use in Tesseract jobs"
    )
    parser_model_validation.add_argument(
        "image",
        type=str,
        nargs="?",
        help="the image and tag to validate, e.g. my-model-container:v0.0.1",
    )
    parser_model_validation.add_argument(
        "-a",
        "--args",
        type=str,
        help="json string of arguments to send to the container",
    )
    parser_model_validation.add_argument(
        "-p",
        "--print_container_logs",
        action="store_true",
        help="print all container logs when run is completed",
    )
    parser_model_validation.add_argument(
        "-f",
        "--config-file",
        type=str,
        help="Path to the JSON config file for validation.",
        default=None,
    )
    parser_model_validation.set_defaults(func=validate_command)

    return parser


def main():
    args = make_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
