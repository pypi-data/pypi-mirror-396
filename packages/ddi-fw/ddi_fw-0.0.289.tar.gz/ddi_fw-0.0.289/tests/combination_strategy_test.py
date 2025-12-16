
from unittest import TestCase
from ddi_fw.pipeline.multi_modal_combination_strategy import CustomCombinationStrategy


class TryTesting(TestCase):
    
    def test_pure_combinations(self):
        import itertools
        l = ['e1','e2','e3','e4','e5']
        all_combinations = []
        for i in range(2, len(l) + 1):
            all_combinations.extend(list(itertools.combinations(l, i)))

        print(all_combinations)

        for combination in all_combinations:
            combination_descriptor = '-'.join(combination)
            print(combination_descriptor)
    
    def test_combination_strategy(self):
        group_1 = ["a", "b", "c"]
        group_2 = [1, 2, 3]
        strategy = CustomCombinationStrategy(group_1=group_1, group_2=group_2)
        combinations = strategy.generate()
        print(combinations)
