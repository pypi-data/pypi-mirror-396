import os
import sys

from cvsx2mvsx.etl.pipelines.config import PipelineConfig

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cvsx2mvsx.etl.pipelines.pipeline import Pipeline
from cvsx2mvsx.etl.pipelines.pipeline_steps import (
    ExtractCVSX,
    LoadMVStory,
    TransformToInternal,
    TransformToMVStory,
)

CVSX_ZIPPED_DIR = "data/cvsx/zipped"
mvstory_DIR = "data/mvstory"


def ensure_dirs():
    os.makedirs(mvstory_DIR, exist_ok=True)


def convert_all_cvsx():
    ensure_dirs()

    pipeline = Pipeline(
        [
            ExtractCVSX(),
            TransformToInternal(),
            TransformToMVStory(),
            LoadMVStory(),
        ]
    )

    for root, dirs, files in os.walk(CVSX_ZIPPED_DIR):
        for file in files:
            if not file.lower().endswith(".cvsx"):
                continue

            cvsx_path = os.path.join(root, file)
            base_name = os.path.splitext(file)[0]

            rel_path = os.path.relpath(root, CVSX_ZIPPED_DIR)

            output_subdir = os.path.join(mvstory_DIR, rel_path)
            os.makedirs(output_subdir, exist_ok=True)

            output_mvstory_path = os.path.join(output_subdir, f"{base_name}.mvstory")

            print(f"Converting: {cvsx_path}")

            configs = [
                PipelineConfig(
                    input_path=cvsx_path,
                    output_path=output_mvstory_path,
                    lattice_to_mesh=True,
                )
            ]

            if "lattice" in cvsx_path:
                configs += [
                    PipelineConfig(
                        input_path=cvsx_path,
                        output_path=os.path.join(
                            output_subdir, f"{base_name}-volume.mvstory"
                        ),
                        lattice_to_mesh=False,
                    )
                ]

            try:
                for config in configs:
                    pipeline.run(config)
            except Exception as e:
                print(f"❌ Failed to convert {file}: {e}")

            if not os.path.exists(output_mvstory_path):
                print(f"❌ ERROR: MVStory file not found after converting {cvsx_path}")


def main():
    convert_all_cvsx()
    print("\n✅ Done converting and unzipping all files!")


if __name__ == "__main__":
    main()
