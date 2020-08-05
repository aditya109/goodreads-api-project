import collections
import os
import string
import random
import time
import traceback


class Solution:
    def __init__(self):
        pass

    def fun1(self):
        pass

    def ideal_code(self):
        pass

    def test_my_code(self):
        start_time = time.time()

        test_case = 15
        successful_count = 0
        failed_count = 0
        for iteration in range(test_case):
            print("_______________________________________________________________________________________________")
            try:
                N = int(random.randint(1, 20))
                # seed = string.ascii_letters
                # A = ''.join(random.choice(seed) for i in range(N))
                print(f"Executing test case {iteration}: {A}")
                my_result = self.checkIfStringHasUniqueCharacters2(A)
                ideal_result = self.checkIfStringHasUniqueCharacters1(A)
                assert my_result == ideal_result
                successful_count += 1
                print(f"Test case {iteration} passed ! ✔️")
            except (AssertionError, IndexError) as err:
                failed_count += 1
                print(f"Test case {iteration} failed ! ❌")
                print(traceback.print_exc())
        print(
            "=====================================================================================================")
        print(f"Total Test Cases Run : {test_case}")
        print(f"Total Test Cases Successful ✔️: {successful_count}")
        print(f"Total Test Cases Failed ❌: {failed_count}")
        print(f"Time of Execution of {test_case} test cases : {time.time() - start_time}")


if __name__ == "__main__":
    # clearing screen
    if os.name == "nt":
        _ = os.system('cls')

    Solution().test_my_code()

    input("\n\n\nPress enter to exit 🚀")

    # clearing screen
    if os.name == "nt":
        _ = os.system('cls')
