from halib import *
from flops import _calculate_flops_for_model

from halib import *
from argparse import ArgumentParser


def main():
    csv_file = "./results-imagenet.csv"
    df = pd.read_csv(csv_file)
    # make param_count column as float
    # df['param_count'] = df['param_count'].astype(float)
    df['param_count'] = pd.to_numeric(df['param_count'], errors='coerce').fillna(99999).astype(float)
    df = df[df['param_count'] < 5.0]  # filter models with param_count < 20M

    dict_ls = []

    for index, row in tqdm(df.iterrows()):
        console.rule(f"Row {index+1}/{len(df)}")
        model = row['model']
        num_class = 2
        _, _, mflops = _calculate_flops_for_model(model, num_class)
        dict_ls.append({'model': model, 'param_count': row['param_count'], 'mflops': mflops})

    # Create a DataFrame from the list of dictionaries
    result_df = pd.DataFrame(dict_ls)

    final_df = pd.merge(df, result_df, on=['model', 'param_count'])
    final_df.sort_values(by='mflops', inplace=True, ascending=True)
    csvfile.fn_display_df(final_df)


if __name__ == "__main__":
    main()
