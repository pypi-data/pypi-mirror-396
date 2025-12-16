import ast
import os
import json
import time
import click
import base64
import pandas as pd

from PIL import Image
from io import BytesIO

import plotly.express as px
from ..common import now_str
from ..filetype import csvfile
import plotly.graph_objects as go
from ..system import filesys as fs

from rich.console import Console
from typing import Callable, Optional, Tuple, List, Union


console = Console()
desktop_path = os.path.expanduser("~/Desktop")


class PlotHelper:
    def _verify_csv(self, csv_file):
        """Read a CSV and normalize column names (lowercase)."""
        try:
            df = csvfile.read_auto_sep(csv_file)
            df.columns = [col.lower() for col in df.columns]
            return df
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file '{csv_file}' not found")
        except Exception as e:
            raise ValueError(f"Error reading CSV file '{csv_file}': {str(e)}")

    @staticmethod
    def _norm_str(s):
        """Normalize string by converting to lowercase and replacing spaces/underscores."""
        return s.lower().replace(" ", "_").replace("-", "_")

    @staticmethod
    def _get_file_name(file_path):
        """Extract file name without extension."""
        return os.path.splitext(os.path.basename(file_path))[0]

    def _get_valid_tags(self, csv_files, tags):
        """Generate tags from file names if not provided."""
        if tags:
            return list(tags)
        return [self._norm_str(self._get_file_name(f)) for f in csv_files]

    def _prepare_long_df(self, csv_files, tags, x_col, y_cols, log=False):
        """Convert multiple CSVs into a single long-form dataframe for Plotly."""
        dfs = []
        for csv_file, tag in zip(csv_files, tags):
            df = self._verify_csv(csv_file)
            # Check columns
            if x_col not in df.columns:
                raise ValueError(f"{csv_file} is missing x_col '{x_col}'")
            missing = [c for c in y_cols if c not in df.columns]
            if missing:
                raise ValueError(f"{csv_file} is missing y_cols {missing}")

            if log:
                console.log(f"Plotting {csv_file}")
                console.print(df)

            # Wide to long
            df_long = df.melt(
                id_vars=x_col,
                value_vars=y_cols,
                var_name="metric_type",
                value_name="value",
            )
            df_long["tag"] = tag
            dfs.append(df_long)

        return pd.concat(dfs, ignore_index=True)

    def _plot_with_plotly(
        self,
        df_long,
        tags,
        outdir,
        save_fig,
        out_fmt="svg",
        font_size=16,
        x_col="epoch",
        y_cols=None,
    ):
        """Generate Plotly plots for given metrics."""
        assert out_fmt in ["svg", "pdf", "png"], "Unsupported format"
        if y_cols is None:
            raise ValueError("y_cols must be provided")

        # Group by suffix (e.g., "loss", "acc") if names like train_loss exist
        metric_groups = sorted(set(col.split("_")[-1] for col in y_cols))

        for metric in metric_groups:
            subset = df_long[df_long["metric_type"].str.contains(metric)]

            if out_fmt == "svg":  # LaTeX-style
                title = f"${'+'.join(tags)}\\_{metric}\\text{{-by-{x_col}}}$"
                xaxis_title = f"$\\text{{{x_col.capitalize()}}}$"
                yaxis_title = f"${metric.capitalize()}$"
            else:
                title = f"{'+'.join(tags)}_{metric}-by-{x_col}"
                xaxis_title = x_col.capitalize()
                yaxis_title = metric.capitalize()

            fig = px.line(
                subset,
                x=x_col,
                y="value",
                color="tag",
                line_dash="metric_type",
                title=title,
            )
            fig.update_layout(
                font=dict(family="Computer Modern", size=font_size),
                xaxis_title=xaxis_title,
                yaxis_title=yaxis_title,
            )
            fig.show()

            if save_fig:
                os.makedirs(outdir, exist_ok=True)
                timestamp = now_str()
                filename = f"{timestamp}_{'+'.join(tags)}_{metric}"
                try:
                    fig.write_image(os.path.join(outdir, f"{filename}.{out_fmt}"))
                except Exception as e:
                    console.log(f"Error saving figure '{filename}.{out_fmt}': {str(e)}")

    @classmethod
    def plot_csv_timeseries(
        cls,
        csv_files,
        outdir="./out/plot",
        tags=None,
        log=False,
        save_fig=False,
        update_in_min=0,
        out_fmt="svg",
        font_size=16,
        x_col="epoch",
        y_cols=["train_loss", "train_acc"],
    ):
        """Plot CSV files with Plotly, supporting live updates, as a class method."""
        if isinstance(csv_files, str):
            csv_files = [csv_files]
        if isinstance(tags, str):
            tags = [tags]

        if not y_cols:
            raise ValueError("You must specify y_cols explicitly")

        # Instantiate PlotHelper to call instance methods
        plot_helper = cls()
        valid_tags = plot_helper._get_valid_tags(csv_files, tags)
        assert len(valid_tags) == len(
            csv_files
        ), "Number of tags must match number of CSV files"

        def run_once():
            df_long = plot_helper._prepare_long_df(
                csv_files, valid_tags, x_col, y_cols, log
            )
            plot_helper._plot_with_plotly(
                df_long, valid_tags, outdir, save_fig, out_fmt, font_size, x_col, y_cols
            )

        if update_in_min > 0:
            interval = int(update_in_min * 60)
            console.log(f"Live update every {interval}s. Press Ctrl+C to stop.")
            try:
                while True:
                    run_once()
                    time.sleep(interval)
            except KeyboardInterrupt:
                console.log("Stopped live updates.")
        else:
            run_once()

    @staticmethod
    def get_img_grid_df(input_dir, log=False):
        """
        Use images in input_dir to create a dataframe for plot_image_grid.

        Directory structures supported:

        A. Row/Col structure:
            input_dir/
                ├── row0/
                │   ├── col0/
                │   │   ├── 0.png
                │   │   ├── 1.png
                │   └── col1/
                │       ├── 0.png
                │       ├── 1.png
                ├── row1/
                │   ├── col0/
                │   │   ├── 0.png
                │   │   ├── 1.png
                │   └── col1/
                │       ├── 0.png
                │       ├── 1.png

        B. Row-only structure (no cols):
            input_dir/
                ├── row0/
                │   ├── 0.png
                │   ├── 1.png
                ├── row1/
                │   ├── 0.png
                │   ├── 1.png

        Returns:
            pd.DataFrame: DataFrame suitable for plot_image_grid.
                        Each cell contains a list of image paths.
        """
        # --- Collect row dirs ---
        rows = sorted([r for r in fs.list_dirs(input_dir) if r.startswith("row")])
        if not rows:
            raise ValueError(f"No 'row*' directories found in {input_dir}")

        first_row_path = os.path.join(input_dir, rows[0])
        subdirs = fs.list_dirs(first_row_path)

        if subdirs:  # --- Case A: row/col structure ---
            cols_ref = sorted(subdirs)

            # Ensure column consistency
            meta_dict = {row: sorted(fs.list_dirs(os.path.join(input_dir, row))) for row in rows}
            for row, cols in meta_dict.items():
                if cols != cols_ref:
                    raise ValueError(f"Row {row} has mismatched columns: {cols} vs {cols_ref}")

            # Collect image paths
            meta_with_paths = {
                row: {
                    col: fs.filter_files_by_extension(os.path.join(input_dir, row, col), ["png", "jpg", "jpeg"])
                    for col in cols_ref
                }
                for row in rows
            }

            # Validate equal number of images per (row, col)
            n_imgs = len(meta_with_paths[rows[0]][cols_ref[0]])
            for row, cols in meta_with_paths.items():
                for col, paths in cols.items():
                    if len(paths) != n_imgs:
                        raise ValueError(
                            f"Inconsistent file counts in {row}/{col}: {len(paths)} vs expected {n_imgs}"
                        )

            # Flatten long format
            data = {"row": [row for row in rows for _ in range(n_imgs)]}
            for col in cols_ref:
                data[col] = [meta_with_paths[row][col][i] for row in rows for i in range(n_imgs)]

        else:  # --- Case B: row-only structure ---
            meta_with_paths = {
                row: fs.filter_files_by_extension(os.path.join(input_dir, row), ["png", "jpg", "jpeg"])
                for row in rows
            }

            # Validate equal number of images per row
            n_imgs = len(next(iter(meta_with_paths.values())))
            for row, paths in meta_with_paths.items():
                if len(paths) != n_imgs:
                    raise ValueError(f"Inconsistent file counts in {row}: {len(paths)} vs expected {n_imgs}")

            # Flatten long format (images indexed as img0,img1,...)
            data = {"row": rows}
            for i in range(n_imgs):
                data[f"img{i}"] = [meta_with_paths[row][i] for row in rows]

        # --- Convert to wide "multi-list" format ---
        df = pd.DataFrame(data)
        row_col = df.columns[0]       # first col = row labels
        # col_cols = df.columns[1:]     # the rest = groupable cols

        df = (
            df.melt(id_vars=[row_col], var_name="col", value_name="path")
            .groupby([row_col, "col"])["path"]
            .apply(list)
            .unstack("col")
            .reset_index()
        )

        if log:
            csvfile.fn_display_df(df)

        return df

    @staticmethod
    def _parse_cell_to_list(cell) -> List[str]:
        """Parse a DataFrame cell that may already be a list, a Python-list string, JSON list string,
        or a single path. Returns list[str]."""
        if cell is None:
            return []
        # pandas NA
        try:
            if pd.isna(cell):
                return []
        except Exception:
            pass

        if isinstance(cell, list):
            return [str(x) for x in cell]

        if isinstance(cell, (tuple, set)):
            return [str(x) for x in cell]

        if isinstance(cell, str):
            s = cell.strip()
            if not s:
                return []

            # Try Python literal (e.g. "['a','b']")
            try:
                val = ast.literal_eval(s)
                if isinstance(val, (list, tuple)):
                    return [str(x) for x in val]
                if isinstance(val, str):
                    return [val]
            except Exception:
                pass

            # Try JSON
            try:
                val = json.loads(s)
                if isinstance(val, list):
                    return [str(x) for x in val]
                if isinstance(val, str):
                    return [val]
            except Exception:
                pass

            # Fallback: split on common separators
            for sep in [";;", ";", "|", ", "]:
                if sep in s:
                    parts = [p.strip() for p in s.split(sep) if p.strip()]
                    if parts:
                        return parts

            # Single path string
            return [s]

        # anything else -> coerce to string
        return [str(cell)]

    @staticmethod
    def plot_image_grid(
        indir_or_csvf_or_df: Union[str, pd.DataFrame],
        save_path: str = None,
        dpi: int = 300, # DPI for saving raster images or PDF
        show: bool = True, # whether to show the plot in an interactive window
        img_width: int = 300,
        img_height: int = 300,
        img_stack_direction: str = "horizontal",  # "horizontal" or "vertical"
        img_stack_padding_px: int = 5,
        img_scale_mode: str = "fit",  # "fit" or "fill"
        format_row_label_func: Optional[Callable[[str], str]] = None,
        format_col_label_func: Optional[Callable[[str], str]] = None,
        title: str = "",
        tickfont=dict(size=16, family="Arial", color="black"),  # <-- bigger labels
        fig_margin: dict = dict(l=50, r=50, t=50, b=50),
        outline_color: str = "",
        outline_size: int = 1,
        cell_margin_px: int = 10,  # padding (top, left, right, bottom) inside each cell
        row_line_size: int = 0,  # if >0, draw horizontal dotted lines
        col_line_size: int = 0,  # if >0, draw vertical dotted lines
    ) -> go.Figure:
        """
        Plot a grid of images using Plotly.

        - Accepts DataFrame where each cell is either:
            * a Python list object,
            * a string representation of a Python list (e.g. "['a','b']"),
            * a JSON list string, or
            * a single path string.
        - For each cell, stack the images into a single composite that exactly fits
        (img_width, img_height) is the target size for each individual image in the stack.
        The final cell size will depend on the number of images and stacking direction.
        """

        def process_image_for_slot(
            path: str,
            target_size: Tuple[int, int],
            scale_mode: str,
            outline: str,
            outline_size: int,
        ) -> Image.Image:
            try:
                img = Image.open(path).convert("RGB")
            except Exception:
                return Image.new("RGB", target_size, (255, 255, 255))

            if scale_mode == "fit":
                img_ratio = img.width / img.height
                target_ratio = target_size[0] / target_size[1]

                if img_ratio > target_ratio:
                    new_height = target_size[1]
                    new_width = max(1, int(new_height * img_ratio))
                else:
                    new_width = target_size[0]
                    new_height = max(1, int(new_width / img_ratio))

                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                left = (new_width - target_size[0]) // 2
                top = (new_height - target_size[1]) // 2
                right = left + target_size[0]
                bottom = top + target_size[1]

                if len(outline) == 7 and outline.startswith("#"):
                    border_px = outline_size
                    bordered = Image.new(
                        "RGB",
                        (target_size[0] + 2 * border_px, target_size[1] + 2 * border_px),
                        outline,
                    )
                    bordered.paste(
                        img.crop((left, top, right, bottom)), (border_px, border_px)
                    )
                    return bordered
                return img.crop((left, top, right, bottom))

            elif scale_mode == "fill":
                if len(outline) == 7 and outline.startswith("#"):
                    border_px = outline_size
                    bordered = Image.new(
                        "RGB",
                        (target_size[0] + 2 * border_px, target_size[1] + 2 * border_px),
                        outline,
                    )
                    img = img.resize(target_size, Image.Resampling.LANCZOS)
                    bordered.paste(img, (border_px, border_px))
                    return bordered
                return img.resize(target_size, Image.Resampling.LANCZOS)
            else:
                raise ValueError("img_scale_mode must be 'fit' or 'fill'.")

        def stack_images_base64(
            image_paths: List[str],
            direction: str,
            single_img_size: Tuple[int, int],
            outline: str,
            outline_size: int,
            padding: int,
        ) -> Tuple[str, Tuple[int, int]]:
            image_paths = [p for p in image_paths if p is not None and str(p).strip() != ""]
            n = len(image_paths)
            if n == 0:
                blank = Image.new("RGB", single_img_size, (255, 255, 255))
                buf = BytesIO()
                blank.save(buf, format="PNG")
                return (
                    "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(),
                    single_img_size,
                )

            processed = [
                process_image_for_slot(
                    p, single_img_size, img_scale_mode, outline, outline_size
                )
                for p in image_paths
            ]
            pad_total = padding * (n - 1)

            if direction == "horizontal":
                total_w = sum(im.width for im in processed) + pad_total
                total_h = max(im.height for im in processed)
                stacked = Image.new("RGB", (total_w, total_h), (255, 255, 255))
                x = 0
                for im in processed:
                    stacked.paste(im, (x, 0))
                    x += im.width + padding
            elif direction == "vertical":
                total_w = max(im.width for im in processed)
                total_h = sum(im.height for im in processed) + pad_total
                stacked = Image.new("RGB", (total_w, total_h), (255, 255, 255))
                y = 0
                for im in processed:
                    stacked.paste(im, (0, y))
                    y += im.height + padding
            else:
                raise ValueError("img_stack_direction must be 'horizontal' or 'vertical'.")

            buf = BytesIO()
            stacked.save(buf, format="PNG")
            encoded = base64.b64encode(buf.getvalue()).decode()
            return f"data:image/png;base64,{encoded}", (total_w, total_h)

        def compute_stacked_size(
            image_paths: List[str],
            direction: str,
            single_w: int,
            single_h: int,
            padding: int,
            outline: str,
            outline_size: int,
        ) -> Tuple[int, int]:
            image_paths = [p for p in image_paths if p is not None and str(p).strip() != ""]
            n = len(image_paths)
            if n == 0:
                return single_w, single_h
            has_outline = len(outline) == 7 and outline.startswith("#")
            border = 2 * outline_size if has_outline else 0
            unit_w = single_w + border
            unit_h = single_h + border
            if direction == "horizontal":
                total_w = n * unit_w + (n - 1) * padding
                total_h = unit_h
            elif direction == "vertical":
                total_w = unit_w
                total_h = n * unit_h + (n - 1) * padding
            else:
                raise ValueError("img_stack_direction must be 'horizontal' or 'vertical'.")
            return total_w, total_h

        # --- Load DataFrame ---
        if isinstance(indir_or_csvf_or_df, str):
            fname, ext = os.path.splitext(indir_or_csvf_or_df)
            if ext.lower() == ".csv":
                df = pd.read_csv(indir_or_csvf_or_df)
            elif os.path.isdir(indir_or_csvf_or_df):
                df = PlotHelper.img_grid_indir_1(indir_or_csvf_or_df, log=False)
            else:
                raise ValueError("Input string must be a valid CSV file or directory path")
        elif isinstance(indir_or_csvf_or_df, pd.DataFrame):
            df = indir_or_csvf_or_df.copy()
        else:
            raise ValueError("Input must be CSV file path, DataFrame, or directory path")

        rows = df.iloc[:, 0].astype(str).tolist()
        columns = list(df.columns[1:])
        n_rows, n_cols = len(rows), len(columns)

        fig = go.Figure()

        # First pass: compute content sizes
        content_col_max = [0] * n_cols
        content_row_max = [0] * n_rows
        cell_paths = [[None] * n_cols for _ in range(n_rows)]
        for i in range(n_rows):
            for j in range(n_cols):
                raw_cell = df.iloc[i, j + 1]
                paths = PlotHelper._parse_cell_to_list(raw_cell)
                image_paths = [str(p).strip() for p in paths if str(p).strip() != ""]
                cell_paths[i][j] = image_paths
                cw, ch = compute_stacked_size(
                    image_paths,
                    img_stack_direction,
                    img_width,
                    img_height,
                    img_stack_padding_px,
                    outline_color,
                    outline_size,
                )
                content_col_max[j] = max(content_col_max[j], cw)
                content_row_max[i] = max(content_row_max[i], ch)

        # Compute display sizes (content max + padding)
        display_col_w = [content_col_max[j] + 2 * cell_margin_px for j in range(n_cols)]
        display_row_h = [content_row_max[i] + 2 * cell_margin_px for i in range(n_rows)]

        # Compute positions (cells adjacent)
        x_positions = []
        cum_w = 0
        for dw in display_col_w:
            x_positions.append(cum_w)
            cum_w += dw

        y_positions = []
        cum_h = 0
        for dh in display_row_h:
            y_positions.append(-cum_h)
            cum_h += dh

        # Second pass: create padded images (centered content)
        cell_imgs = [[None] * n_cols for _ in range(n_rows)]
        p = cell_margin_px
        for i in range(n_rows):
            for j in range(n_cols):
                image_paths = cell_paths[i][j]
                content_src, (cw, ch) = stack_images_base64(
                    image_paths,
                    img_stack_direction,
                    (img_width, img_height),
                    outline_color,
                    outline_size,
                    img_stack_padding_px,
                )
                if cw == 0 or ch == 0:
                    # Skip empty, but create white padded
                    pad_w = display_col_w[j]
                    pad_h = display_row_h[i]
                    padded = Image.new("RGB", (pad_w, pad_h), (255, 255, 255))
                else:
                    content_img = Image.open(
                        BytesIO(base64.b64decode(content_src.split(",")[1]))
                    )
                    ca_w = content_col_max[j]
                    ca_h = content_row_max[i]
                    left_offset = (ca_w - cw) // 2
                    top_offset = (ca_h - ch) // 2
                    pad_w = display_col_w[j]
                    pad_h = display_row_h[i]
                    padded = Image.new("RGB", (pad_w, pad_h), (255, 255, 255))
                    paste_x = p + left_offset
                    paste_y = p + top_offset
                    padded.paste(content_img, (paste_x, paste_y))
                buf = BytesIO()
                padded.save(buf, format="PNG")
                encoded = base64.b64encode(buf.getvalue()).decode()
                cell_imgs[i][j] = f"data:image/png;base64,{encoded}"

        # Add images to figure
        for i in range(n_rows):
            for j in range(n_cols):
                fig.add_layout_image(
                    dict(
                        source=cell_imgs[i][j],
                        x=x_positions[j],
                        y=y_positions[i],
                        xref="x",
                        yref="y",
                        sizex=display_col_w[j],
                        sizey=display_row_h[i],
                        xanchor="left",
                        yanchor="top",
                        layer="above",
                    )
                )

        # Optional grid lines (at cell boundaries, adjusted for inter-content spaces)
        if row_line_size > 0:
            for i in range(1, n_rows):
                y = (y_positions[i - 1] - display_row_h[i - 1] + y_positions[i]) / 2
                fig.add_shape(
                    type="line",
                    x0=-p,
                    x1=cum_w,
                    y0=y,
                    y1=y,
                    line=dict(width=row_line_size, color="black", dash="dot"),
                )

        if col_line_size > 0:
            for j in range(1, n_cols):
                x = x_positions[j]
                fig.add_shape(
                    type="line",
                    x0=x,
                    x1=x,
                    y0=p,
                    y1=-cum_h,
                    line=dict(width=col_line_size, color="black", dash="dot"),
                )

        # Axis labels
        col_labels = [
            format_col_label_func(c) if format_col_label_func else c for c in columns
        ]
        row_labels = [
            format_row_label_func(r) if format_row_label_func else r for r in rows
        ]

        fig.update_xaxes(
            tickvals=[x_positions[j] + display_col_w[j] / 2 for j in range(n_cols)],
            ticktext=col_labels,
            range=[-p, cum_w],
            showgrid=False,
            zeroline=False,
            tickfont=tickfont,  # <-- apply bigger font here
        )
        fig.update_yaxes(
            tickvals=[y_positions[i] - display_row_h[i] / 2 for i in range(n_rows)],
            ticktext=row_labels,
            range=[-cum_h, p],
            showgrid=False,
            zeroline=False,
            tickfont=tickfont,  # <-- apply bigger font here
        )

        fig.update_layout(
            width=cum_w + 100,
            height=cum_h + 100,
            title=title,
            title_x=0.5,
            margin=fig_margin,
        )

        # === EXPORT IF save_path IS GIVEN ===
        if save_path:
            import kaleido  # lazy import – only needed when saving
            import os

            ext = os.path.splitext(save_path)[1].lower()
            if ext in [".png", ".jpg", ".jpeg"]:
                fig.write_image(save_path, scale=dpi / 96)  # scale = dpi / base 96
            elif ext in [".pdf", ".svg"]:
                fig.write_image(save_path)  # PDF/SVG are vector → dpi ignored
            else:
                raise ValueError("save_path must end with .png, .jpg, .pdf, or .svg")
        if show:
            fig.show()
        return fig


@click.command()
@click.option("--csvfiles", "-f", multiple=True, type=str, help="csv files to plot")
@click.option(
    "--outdir", "-o", type=str, default=str(desktop_path), help="output directory"
)
@click.option(
    "--tags", "-t", multiple=True, type=str, default=[], help="tags for the csv files"
)
@click.option("--log", "-l", is_flag=True, help="log the csv files")
@click.option("--save_fig", "-s", is_flag=True, help="save the plot as file")
@click.option(
    "--update_in_min",
    "-u",
    type=float,
    default=0.0,
    help="update the plot every x minutes",
)
@click.option(
    "--x_col", "-x", type=str, default="epoch", help="column to use as x-axis"
)
@click.option(
    "--y_cols",
    "-y",
    multiple=True,
    type=str,
    required=True,
    help="columns to plot as y (can repeat)",
)
def main(csvfiles, outdir, tags, log, save_fig, update_in_min, x_col, y_cols):
    PlotHelper.plot_csv_timeseries(
        list(csvfiles),
        outdir,
        list(tags),
        log,
        save_fig,
        update_in_min,
        x_col=x_col,
        y_cols=list(y_cols),
    )


if __name__ == "__main__":
    main()
