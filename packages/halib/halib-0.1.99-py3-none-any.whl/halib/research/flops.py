import os
import sys
import torch
import timm
from argparse import ArgumentParser
from fvcore.nn import FlopCountAnalysis
from halib import *
from halib.filetype import csvfile
from curriculum.utils.config import *
from curriculum.utils.model_helper import *


# ---------------------------------------------------------------------
# Argument Parser
# ---------------------------------------------------------------------
def parse_args():
    parser = ArgumentParser(description="Calculate FLOPs for TIMM or trained models")

    # Option 1: Direct TIMM model
    parser.add_argument(
        "--model_name", type=str, help="TIMM model name (e.g., efficientnet_b0)"
    )
    parser.add_argument(
        "--num_classes", type=int, default=1000, help="Number of output classes"
    )

    # Option 2: Experiment directory
    parser.add_argument(
        "--indir",
        type=str,
        default=None,
        help="Directory containing trained experiment (with .yaml and .pth)",
    )
    parser.add_argument(
        "-o", "--o", action="store_true", help="Open output CSV after saving"
    )
    return parser.parse_args()


# ---------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------
def _get_list_of_proc_dirs(indir):
    assert os.path.exists(indir), f"Input directory {indir} does not exist."
    pth_files = [f for f in os.listdir(indir) if f.endswith(".pth")]
    if len(pth_files) > 0:
        return [indir]
    return [
        os.path.join(indir, f)
        for f in os.listdir(indir)
        if os.path.isdir(os.path.join(indir, f))
    ]


def _calculate_flops_for_model(model_name, num_classes):
    """Calculate FLOPs for a plain TIMM model."""
    try:
        model = timm.create_model(model_name, pretrained=False, num_classes=num_classes)
        input_size = timm.data.resolve_data_config(model.default_cfg)["input_size"]
        dummy_input = torch.randn(1, *input_size)
        model.eval() # ! set to eval mode to avoid some warnings or errors
        flops = FlopCountAnalysis(model, dummy_input)
        gflops = flops.total() / 1e9
        mflops = flops.total() / 1e6
        print(f"\nModel: **{model_name}**, Classes: {num_classes}")
        print(f"Input size: {input_size}, FLOPs: **{gflops:.3f} GFLOPs**, **{mflops:.3f} MFLOPs**\n")
        return model_name, gflops, mflops
    except Exception as e:
        print(f"[Error] Could not calculate FLOPs for {model_name}: {e}")
        return model_name, -1, -1


def _calculate_flops_for_experiment(exp_dir):
    """Calculate FLOPs for a trained experiment directory."""
    yaml_files = [f for f in os.listdir(exp_dir) if f.endswith(".yaml")]
    pth_files = [f for f in os.listdir(exp_dir) if f.endswith(".pth")]

    assert (
        len(yaml_files) == 1
    ), f"Expected 1 YAML file in {exp_dir}, found {len(yaml_files)}"
    assert (
        len(pth_files) == 1
    ), f"Expected 1 PTH file in {exp_dir}, found {len(pth_files)}"

    exp_cfg_yaml = os.path.join(exp_dir, yaml_files[0])
    cfg = ExpConfig.from_yaml(exp_cfg_yaml)
    ds_label_list = cfg.dataset.get_label_list()

    try:
        model = build_model(
            cfg.model.name, num_classes=len(ds_label_list), pretrained=True
        )
        model_weights_path = os.path.join(exp_dir, pth_files[0])
        model.load_state_dict(torch.load(model_weights_path, map_location="cpu"))
        model.eval()

        input_size = timm.data.resolve_data_config(model.default_cfg)["input_size"]
        dummy_input = torch.randn(1, *input_size)
        flops = FlopCountAnalysis(model, dummy_input)
        gflops = flops.total() / 1e9
        mflops = flops.total() / 1e6

        return str(cfg), cfg.model.name, gflops, mflops
    except Exception as e:
        console.print(f"[red] Error processing {exp_dir}: {e}[/red]")
        return str(cfg), cfg.model.name, -1, -1


# ---------------------------------------------------------------------
# Main Entry
# ---------------------------------------------------------------------
def main():
    args = parse_args()

    # Case 1: Direct TIMM model input
    if args.model_name:
        _calculate_flops_for_model(args.model_name, args.num_classes)
        return

    # Case 2: Experiment directory input
    if args.indir is None:
        print("[Error] Either --model_name or --indir must be specified.")
        return

    proc_dirs = _get_list_of_proc_dirs(args.indir)
    pprint(proc_dirs)

    dfmk = csvfile.DFCreator()
    TABLE_NAME = "model_flops_results"
    dfmk.create_table(TABLE_NAME, ["exp_name", "model_name", "gflops", "mflops"])

    console.rule(f"Calculating FLOPs for models in {len(proc_dirs)} dir(s)...")
    rows = []
    for exp_dir in tqdm(proc_dirs):
        dir_name = os.path.basename(exp_dir)
        console.rule(f"{dir_name}")
        exp_name, model_name, gflops, mflops = _calculate_flops_for_experiment(exp_dir)
        rows.append([exp_name, model_name, gflops, mflops])

    dfmk.insert_rows(TABLE_NAME, rows)
    dfmk.fill_table_from_row_pool(TABLE_NAME)

    outfile = f"zout/zreport/{now_str()}_model_flops_results.csv"
    dfmk[TABLE_NAME].to_csv(outfile, sep=";", index=False)
    csvfile.fn_display_df(dfmk[TABLE_NAME])

    if args.o:
        os.system(f"start {outfile}")


# ---------------------------------------------------------------------
# Script Entry
# ---------------------------------------------------------------------
if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    main()
