import unittest
from unittest import TestCase
import pandas as pd
from ddi_fw.vectorization import IDF


class IDFTesting(TestCase):
    def test_calculate_idf_values(self):
        item1 = 'T001|T002|T001|T001'
        item2 = 'T002|T003'
        item3 = 'T004|T005'

        all_data = [item1, item2, item3]

        df = pd.DataFrame(all_data, columns=['tui_description'])

        df['tui_description'] = df['tui_description'].apply(
            lambda x: x.split('|') if x is not None else [])

        print(df.head())

        idf = IDF(dataframe=df, columns=["tui_description"])
        idf.calculate()
        idf_scores_dict = idf.idf_scores
        idf_scores = idf.to_dataframe()
        print(idf_scores.head())

        # # idf_scores = calculate_idf(df['tui_description'])
        # idf_scores_sorted_desc = sorted(
        #     idf_scores.items(), key=lambda x: x[1], reverse=True)
        # threshold = 1
        # keys_over_threshold = [k for k,v in idf_scores.items() if v > threshold]


if __name__ == '__main__':
    unittest.main()
