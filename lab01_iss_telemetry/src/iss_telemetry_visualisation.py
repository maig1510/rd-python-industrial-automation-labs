import argparse
from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

"""
Seaborn CLI wrapper

This script generates graphs with Seaborn library based on user-provided command line arguments.
The script loads data from a CSV dataset and allows the user to generate different types of plots
such as line, scatter, bar, box, and histogram charts.
"""

def validate_file(path):
    """
    Validate that the CSV file exists and contains all required columns.

    Parameters
    ----------
    path : Path
        Path to the CSV file.

    Returns
    -------
    pandas.DataFrame
        Loaded dataframe with data.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """

    if not path.exists():
        raise FileNotFoundError(f"CSV file {path} does not exist")

    df = pd.read_csv(path)

    return df


def parse_arguments():
    """
    Parse command-line arguments provided by the user.

    Returns
    -------
    argparse.Namespace
        Parsed CLI arguments.
    """

    parser = argparse.ArgumentParser(
        description="Visualisation of dataset"
    )

    parser.add_argument("file", help="CSV file name")

    parser.add_argument("--x", help="Data for X axis")
    parser.add_argument("--y", help="Data for Y axis")

    parser.add_argument("--type", choices=["line", "scatter", "bar", "box", "hist"], default="line", help="Type of plot")

    parser.add_argument("--hue", help="Categorical grouping")

    return parser.parse_args()


def validate_columns(df, args):
    """
    Validate that user-selected columns exist in the dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe containing data.

    args : argparse.Namespace
        Parsed CLI arguments.

    Raises
    ------
    ValueError
        If a requested column does not exist.
    """

    if args.x and args.x not in df.columns:
        raise ValueError(f"Column '{args.x}' not found in CSV")

    if args.type != "hist":
        if not args.y:
            raise ValueError("--y argument is required for this plot type")

        if args.y not in df.columns:
            raise ValueError(f"Column '{args.y}' not found in CSV")

    if args.hue and args.hue not in df.columns:
        raise ValueError(f"Hue column '{args.hue}' not found in CSV")


def main():
    """
    Main program entry point.
    Handles argument parsing, data loading, validation,
    and creation of the selected plot.
    """

    args = parse_arguments()

    script_dir = Path(__file__).resolve().parent
    path = script_dir / ".." / ".." / "datasets" / "iss_telemetry" / args.file
    path = path.resolve()

    df = validate_file(path)

    validate_columns(df, args)

    sns.set_theme(style="whitegrid")

    plot_functions = {
        "line": sns.lineplot,
        "scatter": sns.scatterplot,
        "bar": sns.barplot,
        "box": sns.boxplot,
        "hist": sns.histplot
    }

    plot_func = plot_functions[args.type]

    plt.figure(figsize=(6, 5))

     # Disable scientific notation
    ax = plt.gca()
    ax.get_yaxis().get_major_formatter().set_useOffset(False)
    ax.get_xaxis().get_major_formatter().set_useOffset(False)

    # Histogram only needs X axis
    if args.type == "hist":
        plot_func(data=df, x=args.x, hue=args.hue)
        plt.title(f"Histogram: {args.x}")

    # Other plot types require X and Y axes
    else:
        plot_func(data=df, x=args.x, y=args.y, hue=args.hue)
        plt.title(f"{args.type.capitalize()} plot: {args.x} vs {args.y}")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
