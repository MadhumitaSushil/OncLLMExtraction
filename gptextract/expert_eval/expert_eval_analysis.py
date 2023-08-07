import os
import pandas as pd


def read_scores(f_scores, data_dir):
    df = pd.read_csv(os.path.join(data_dir, f_scores))
    return df


def aggregate_scores(df_scores, fout='expert_eval_results.csv', output_dir='../../output'):
    grouped_df = df_scores.groupby('Relation').sum()
    grouped_df = grouped_df.transpose()

    dtype_mapping = {
        1: 'int32',
        2: 'int32',
        3: 'int32',
        4: 'int32',
        5: 'int32',
        6: 'int32',
        7: 'int32',
        8: 'int32',
    }

    score_mapping = {
        1: 'Exactly correct',
        2: 'Partially correct with some information missing',
        3: 'Correct, but contains more information than necessary',
        4: 'Contains necessary correct information, but additionally provides extra incorrect information',
        5: 'Ambiguous langauge in text',
        6: 'Hallucinations1: Answers incorrectly from information in text',
        7: 'Hallucinations2: Produces information not present in text',
        8: 'Missing output',

    }

    grouped_df = grouped_df.astype(dtype_mapping)
    grouped_df = grouped_df.rename(columns=score_mapping)

    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    print(grouped_df)

    grouped_df.to_csv(os.path.join(output_dir, fout))


if __name__ == '__main__':
    df = read_scores('OncPNHumanEval_scores.csv', '../../output/')
    aggregate_scores(df)
