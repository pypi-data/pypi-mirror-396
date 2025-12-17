#!/usr/bin/env python3
# pyright: basic
"""Test artifact parsing."""

import io
import zipfile

import imandrax_api
import imandrax_api.lib as xtypes


def main():
    with open("task_art.zip", "rb") as f:
      cntnt = f.read()

    with zipfile.ZipFile(io.BytesIO(cntnt)) as zf:
      art_task_data = zf.read(zf.namelist()[0])

    art_task = xtypes.read_artifact_data(data=art_task_data, kind="po_task")
    assert art_task is not None, "failed to parse po_task"

    print("PASSED")


if __name__ == "__main__":
    main()
