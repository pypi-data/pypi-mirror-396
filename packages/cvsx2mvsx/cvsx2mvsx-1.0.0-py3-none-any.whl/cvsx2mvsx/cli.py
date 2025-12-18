import argparse
import os
import sys

from cvsx2mvsx.etl.pipelines.config import PipelineConfig
from cvsx2mvsx.etl.pipelines.pipeline import Pipeline
from cvsx2mvsx.etl.pipelines.pipeline_steps import (
    ExtractCVSX,
    LoadMVStory,
    LoadMVSX,
    TransformToInternal,
    TransformToMVStory,
    TransformToMVSX,
)


def main():
    parser = argparse.ArgumentParser(description="Convert CVSX files declaratively.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--format", choices=["mvsx", "mvstory"], default="mvsx")
    parser.add_argument("--lattice-to-mesh", action="store_true")

    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: File {args.input} not found.")
        sys.exit(1)

    config = PipelineConfig(
        input_path=args.input,
        output_path=args.output,
        lattice_to_mesh=args.lattice_to_mesh,
    )

    mvsx_pipeline = Pipeline(
        [
            ExtractCVSX(),
            TransformToInternal(),
            TransformToMVSX(),
            LoadMVSX(),
        ]
    )

    mvstory_pipeline = Pipeline(
        [
            ExtractCVSX(),
            TransformToInternal(),
            TransformToMVStory(),
            LoadMVStory(),
        ]
    )

    # 3. Execute
    print(f"Running pipeline for format: {args.format}...")

    if args.format == "mvsx":
        mvsx_pipeline.run(config)
    else:
        mvstory_pipeline.run(config)

    print("Done.")


if __name__ == "__main__":
    main()
