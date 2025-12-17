from contextlib import contextmanager
from pathlib import Path

import ipynbname

from ..common import console, now_str


@contextmanager
def gen_ipynb_name(
    filename,
    add_time_stamp=False,
    nb_prefix="nb__",
    separator="__",
):
    """
    Context manager that prefixes the filename with the notebook name.
    Output: NotebookName_OriginalName.ext
    """
    try:
        nb_name = ipynbname.name()
    except FileNotFoundError:
        nb_name = "script"  # Fallback

    p = Path(filename)

    # --- FIX START ---

    # 1. Get the parts separately
    original_stem = p.stem  # "test" (no extension)
    extension = p.suffix  # ".csv"

    now_string = now_str() if add_time_stamp else ""

    # 2. Construct the base name (Notebook + Separator + OriginalName)
    base_name = f"{nb_prefix}{nb_name}{separator}{original_stem}"

    # 3. Append timestamp if needed
    if now_string:
        base_name = f"{base_name}{separator}{now_string}"

    # 4. Add the extension at the VERY END
    new_filename = f"{base_name}{extension}"

    # --- FIX END ---

    final_path = p.parent / new_filename

    # Assuming you use 'rich' console based on your snippet
    # console.rule()
    # print(f"📝 Saving as: {final_path}")

    yield str(final_path)


if __name__ == "__main__":
    # --- Usage Example ---
    # Assume Notebook Name is: "MyThesisWork"
    filename = "results.csv"
    with gen_ipynb_name(filename) as filename_ipynb:
        # filename_ipynb is now: "MyThesisWork_results.csv"
        print(f"File to save: {filename_ipynb}")
        # df.to_csv(filename_ipynb)
