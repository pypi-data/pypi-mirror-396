# types = [int, float, str]
# num_types = len(types)
# type_names = ["int", "float", "string"]
# test_int_pos_max = 10
# test_int_pos_min = 1
# test_int_neg_max = -1
# test_int_neg_min = -10
# test_pos_int_in_range = int((test_int_pos_max - test_int_pos_min) / 2)
# test_pos_int_out_of_range = test_int_pos_max + 1
#
# type_index = 0
# while type_index < num_types:
#     curr_type = types[type_index]
#     curr_type_name = type_names[type_index]
#     print(f"Testing in-range verification for {curr_type_name}s")
#
#     type_index += 1
#
# self.assertEqual(error_helper.check_value_is_in_range(test_pos_int_in_range, test_int_pos_min, test_int_pos_max,
#                                                       f"test integer {test_pos_int_in_range}"), True)

# # Create a list of the types we want to test.
# types = [int, float, bool, str, list]
# num_types = len(types)
# # Create the corresponding list of the type names
# # (i.e., what should be printed when describing them in a human-friendly manner).
# type_names = ["int", "float", "boolean", "string", "list"]
#
# test_int_pos = 5
# test_int_neg = -5
# test_list_empty = []
# test_list_int_single = [test_int_pos]
# test_list_int_multiple = [test_int_pos, test_int_neg]
# test_str_empty = ""
# test_str_single = "a"
# test_str_multiple = "abcd"
# test_list_str_single = [test_str_single]
# test_list_str_multiple = [test_str_single, test_str_multiple]
#
# # self.fail()


# print("Testing check_type function")
# types_to_test = ALL_TYPES
# # Create a list of the types we want to test.
# types = [int, float, bool, str, list]
# num_types = len(types)
# # Create the corresponding list of the type names
# # (i.e., what should be printed when describing them in a human-friendly manner).
# type_names = ["int", "float", "boolean", "string", "list"]
# assert len(type_names) == num_types
# type_indices = list(range(num_types))
# type_index_dict = dict(zip(type_names, type_indices))
#
#
#
# # Create a test int, string, and float
# test_int = 5
# test_str = str(test_int)
# test_float = float(test_int)
# test_bool_true = True
# test_bool_false = False
# test_list_empty = []
# test_list_single = [1]
# test_list_multiple = [1, 2]
#
# # print("Checking if the set of possible types from the error_helper library has the correct type (list)")
# # assert(type(types) == list )
# # print("Success: Imported types list.")
# # num_types = len(types)
# # type_names = error_helper.TYPE_NAMES
# # print("Checking if the set of type names from the error_helper library has the correct type (list)")
# # assert(type(type_names) == list)
# # print("Checking if TYPES and TYPE_NAMES from the error_helper library have the same number of elements")
# # assert(len(types) == len(type_names))
# # print(f"Success: len(TYPES) = len(TYPE_NAMES) = {len(types)}")
#
# correct_inputs_dict = {INT_NAME: [test_int],
#                        FLOAT_NAME: [test_float],
#                        BOOL_NAME: [test_bool_true, test_bool_false],
#                        STRING_NAME: [test_str],
#                        LIST_NAME: [test_list_empty, test_list_single, test_list_multiple]}
#
# incorrect_inputs_dict = {INT_NAME: [test_float, test_bool_true, test_bool_false, test_str,
#                                     test_list_empty, test_list_single, test_list_multiple],
#                          FLOAT_NAME: [test_int, test_bool_true, test_bool_false, test_str,
#                                       test_list_empty, test_list_single, test_list_multiple],
#                          BOOL_NAME: [test_int, test_float, test_bool_true, test_bool_false,
#                                      test_list_empty, test_list_single, test_list_multiple],
#                          STRING_NAME: [test_int, test_float, test_bool_true, test_bool_false,
#                                        test_list_empty, test_list_single, test_list_multiple],
#                          LIST_NAME: [test_int, test_float, test_bool_true, test_bool_false, test_str]}
#
# for type_tup in types_to_test:
#     assert len(type_tup) > 1
#     curr_type, curr_type_name = type_tup[0], type_tup[1]
#     print(f"\nTesting required_type={curr_type} cases (i.e., checking if an input is a(n) {curr_type_name})")
#     curr_correct_inputs = correct_inputs_dict[curr_type_name]
#     curr_incorrect_inputs = incorrect_inputs_dict[curr_type_name]
#     for correct_input in curr_correct_inputs:
#         print(f"Testing {curr_type_name} type verification (input = {curr_type_name} {correct_input})")
#         self.assertEqual(error_helper.check_type(correct_input, curr_type,
#                                                  f"test {curr_type_name} ({correct_input})"), True)
#         print(f"Success: {curr_type_name} {correct_input} is a(n) {curr_type_name}.")
#     for incorrect_input in curr_incorrect_inputs:
#         incorrect_type = type(incorrect_input)
#         incorrect_type_index = types.index(incorrect_type)
#         incorrect_type_name = ""
#         if 0 <= incorrect_type_index < len(type_names):
#             incorrect_type_name = type_names[incorrect_type_index]
#         print(f"Testing {curr_type_name} type verification (input = {incorrect_type_name} {incorrect_input})")
#         with self.assertRaises(TypeError):
#             error_helper.check_type(incorrect_input, curr_type,
#                                     f"test {incorrect_type_name} type ({incorrect_input})")
#         print(f"Success: {incorrect_type_name} {incorrect_input} is not a(n) {curr_type_name}.")
#
# type_index = 0
# while type_index < num_types:
#     curr_type = types[type_index]
#     curr_type_name = type_names[type_index]
#     print(f"\nTesting required_type={curr_type} cases (i.e., checking if an input is a(n) {curr_type_name})")
#     curr_correct_inputs = correct_inputs_dict[curr_type_name]
#     curr_incorrect_inputs = incorrect_inputs_dict[curr_type_name]
#     for correct_input in curr_correct_inputs:
#         print(f"Testing {curr_type_name} type verification (input = {curr_type_name} {correct_input})")
#         self.assertEqual(error_helper.check_type(correct_input, curr_type,
#                                                  f"test {curr_type_name} ({correct_input})"), True)
#         print(f"Success: {curr_type_name} {correct_input} is a(n) {curr_type_name}.")
#     for incorrect_input in curr_incorrect_inputs:
#         incorrect_type = type(incorrect_input)
#         incorrect_type_index = types.index(incorrect_type)
#         incorrect_type_name = ""
#         if 0 <= incorrect_type_index < len(type_names):
#             incorrect_type_name = type_names[incorrect_type_index]
#         print(f"Testing {curr_type_name} type verification (input = {incorrect_type_name} {incorrect_input})")
#         with self.assertRaises(TypeError):
#             error_helper.check_type(incorrect_input, curr_type,
#                                     f"test {incorrect_type_name} type ({incorrect_input})")
#         print(f"Success: {incorrect_type_name} {incorrect_input} is not a(n) {curr_type_name}.")
#     type_index += 1
#
# #
# # # Check that the alt_type option works correctly.
# # self.assertEqual(error_helper.check_type(test_int, str, f"test int ({test_int})", alt_type=int), True)
# # with self.assertRaises(TypeError):
# #     self.assertEqual(error_helper.check_type(test_int, str, f"test int ({test_int})", alt_type=float), True)