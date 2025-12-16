
TYPES = [int, float, bool, str, list]
num_types = len(TYPES)
INT_NAME = "integer"
FLOAT_NAME = "float"
BOOL_NAME = "bool"
STRING_NAME = "string"
LIST_NAME = "list"
TYPE_NAMES = [""]*num_types
type_index = 0
while type_index < num_types:
    curr_type_name = ""
    curr_type = TYPES[type_index]
    if curr_type == int:
        curr_type_name = INT_NAME
    elif curr_type == float:
        curr_type_name = FLOAT_NAME
    elif curr_type == bool:
        curr_type_name = BOOL_NAME
    elif curr_type == str:
        curr_type_name = STRING_NAME
    elif curr_type == list:
        curr_type_name = LIST_NAME
    TYPE_NAMES[type_index] = curr_type_name
    type_index += 1


def check_type(input_value, required_type, var_name, alt_type=None, alt_types=None,prefix = ""):
    """Checks if an input value has the correct type. Raises a TypeError with an informative error message
    if the input's type is invalid.

    Parameters
    ----------
    input_value : Any
        The input value to check.
    required_type : type
        The type that the input should have.
    var_name : str
        The name of the variable that is being checked (necessary for creating detailed error messages).
    alt_type : type
        An alternative valid type that the input can have, if there is one.
    alt_types : list
        A list of alternative valid types, if there are more than one.
    prefix : str
        A prefix for the error message if one is raised (i.e., any additional context that should be printed before
        information about the TypeError) (empty string by default).

    Returns
    -------
    is_correct_type : bool
        Boolean for whether the input has the required type.

    Raises
    ------
    TypeError
        Raised if the input does not have an acceptable type.

    """
    # Get the type of the input value.
    received_type = type(input_value)
    # Check if it matches the required type.
    is_correct_type = received_type == required_type
    # If the input does not have the main required type,
    # check if it matches any provided alternative types.
    if not is_correct_type:
        # Check if anything was provided for the singular alternative type parameter.
        if alt_type is not None:
            # Check if the input has the alternative type.
            is_correct_type = received_type == alt_type
        # If we couldn't find a match with the single alternative, check if we have a list
        # with multiple alternative types.
        if not is_correct_type:
            if alt_types is not None:
                if type(alt_types) is list:
                    # Check if the input type is in the alternatives list.
                    is_correct_type = received_type in alt_types
    # Raise a type error if the input did not have the required type nor a valid alternative type.
    if not is_correct_type:
        expected_type_str = str(required_type)
        if expected_type_str.startswith("<class '"):
            expected_type_str = expected_type_str[len("<class '"):len(expected_type_str) - 2]
        received_type_str = str(received_type)
        if received_type_str.startswith("<class '"):
            received_type_str = received_type_str[len("<class '"):len(received_type_str) - 2]
        # Start the error message with the prefix string.
        error_string = (f"{prefix} SUBMITTED TYPE: {received_type_str} REQUIRED TYPE: {expected_type_str}\n"
                      + f"You have submitted an incorrect type for \"{var_name}\".\n"
                      + f"Please provide a value of type {expected_type_str} for this parameter.")
        # error_string = prefix
        #
        # error_string += "SUBMITTED TYPE: " + received_type_str
        # error_string += " REQUIRED TYPE: " + expected_type_str
        # error_string += "\nYou have submitted an incorrect type for " + var_name + ".\n"
        # error_string += "Please provide a value of type " + expected_type_str + " for this parameter."
        # Raise the TypeError with the constructed error message.
        raise TypeError(error_string)
    # Return the boolean for whether the type was valid (can be ignored, since this line will only execute
    # if there was no need for a TypeError).
    return is_correct_type

def check_can_convert(input_value, post_convert_type, var_name, prefix=""):
    in_range_setup_prefix = prefix + "\nCAN CONVERT VALIDATION SETUP ERROR\n"
    # Make sure that the variable name is a string.
    check_type(var_name, str,
               "the name of the variable that is being checked (for whether it can be converted to a desired type)", prefix=in_range_setup_prefix)
    can_convert = True
    try:
        conv_value = post_convert_type(input_value)
    except (TypeError, ValueError):
        can_convert = False
        error_string = prefix + "\nCONVERSION ERROR\n"
        error_string += f"\nThe input value that you provided for {var_name} cannot be converted to a {post_convert_type.__name__}\n"
        raise TypeError(error_string)
    return can_convert

def check_value_is_in_range(input_value, min_value, max_value, var_name, min_inclusive=True, max_inclusive=True, prefix=""):
    """Checks if an input value is within a certain range. Raises a ValueError if the input value is not between the
    specified minimum and maximum values (inclusive comparisons by default (i.e., <=, >=); can be switched to exclusive
    (i.e., <, >).

    Parameters
    ----------
    input_value : Any
        The input value to check.
    min_value : Any
        The minimum value that the input should have (must match input type).
    max_value : Any
        The maximum value that the input should have (must match input type).
    var_name : str
        The name of the variable that is being checked (necessary for creating detailed error messages).
    min_inclusive : bool
        Optional flag for whether the comparison between the minimum value and the input value should be inclusive
        (min <= val). (True by default.)
    max_inclusive : bool
        Optional flag for whether the comparison between the maximum value and the input value should be inclusive
        (val <= max). (True by default.)
    prefix : str
        A prefix for the error message if one is raised (i.e., any additional context that should be printed before
        information about the TypeError) (empty string by default).
    Returns
    -------
    is_in_range : Bool
        Boolean for whether the input value is within the specified range.

    Raises
    ______
    ValueError
        Raised if the input is not within the correct range.

    """
    in_range_setup_prefix = prefix + "\nIN RANGE VALIDATION SETUP ERROR\n"
    # Make sure that the variable name is a string.
    check_type(var_name, str,
               "the name of the variable that is being checked (for whether it is within the " +
               "correct range of values)", prefix=in_range_setup_prefix)
    # Ensure that the input, min, and max all have the same type.
    input_type = type(input_value)
    # check_type(min_value, input_type,
    #            f"the minimum value for the variable {var_name}", prefix=in_range_setup_prefix)
    # check_type(max_value, input_type,
    #            f"the maximum value for the variable {var_name}", prefix=in_range_setup_prefix)
    # Ensure that the inclusive comparison flags are both booleans.
    check_type(min_inclusive, bool, f"boolean for whether we should perform an inclusive comparison (>=) "
               + f"between {var_name} and the minimum value", prefix=in_range_setup_prefix)
    check_type(max_inclusive, bool, f"boolean for whether we should perform an inclusive comparison (<=) "
               + f"between {var_name} and the maximum value", prefix=in_range_setup_prefix)
    # Check if the prefix is a string.
    check_type(prefix, str,
               "the prefix for any potential error messages", prefix=in_range_setup_prefix)
    # Check if the input is more than or equal to the minimum value.
    is_more_than_min = input_value >= min_value
    # We need to adjust the comparison if the user wants it to be exclusive.
    if not min_inclusive:
        is_more_than_min = input_value > min_value
    # Check if the input is less than or equal to the maximum value.
    is_less_than_max = input_value <= max_value
    #Re-evaluate if the comparison should be exclusive.
    if not max_inclusive:
        is_less_than_max = input_value < max_value
    # Use the two comparisons to determine if the input is in the correct range.
    is_in_range = is_more_than_min and is_less_than_max
    if not is_in_range:
        # If the value is not in the provided range, we need to raise a ValueError with
        # an informative error message.
        error_string = prefix
        if not is_more_than_min:
            error_string += "SUBMITTED VALUE: " + str(input_value) + " <"
            if min_inclusive:
                error_string += "="
            error_string += " MINIMUM VALUE: " + str(min_value) + "\n"
            error_string += "The value that you have provided for " + var_name + " is too small.\n"
            error_string += "Please provide a value greater than or equal to " + str(min_value) + ".\n"
            raise ValueError(error_string)
        elif input_value > max_value:
            error_string += "SUBMITTED VALUE: " + str(input_value)
            error_string += " > MAXIMUM VALUE: " + str(max_value)
            error_string += "The value that you have provided for " + var_name + " is too large.\n"
            error_string += "Please provide a value greater than or equal to " + str(max_value) + ".\n"
            raise ValueError(error_string)
    return is_in_range


def check_value_is_in_set(input_value, accepted_values, var_name, prefix=""):
    """Verifies whether an input value is in a provided set of accepted values.
    Raises a ValueError with an informative error message if the input is not
    in the allowable set.

    Parameters
    ----------
    input_value : Any
        Value that needs to be checked against a list of accepted values.
    accepted_values : list
        List of all the valid/acceptable values for the input variable.
    var_name : str
        The name of the variable that needs to be checked (necessary for creating detailed error messages).
    prefix : str
        A prefix for the error message (i.e., any additional context that should
        be printed before information about the ValueError) (empty string by default).

    Returns
    -------
    is_in_set : bool
        Boolean for whether the input is in the set of accepted values.

    Raises
    ------
    ValueError
        Raised if the input is not in the set of accepted values.
    """
    in_set_setup_prefix = prefix + "\nIN SET VALIDATION SETUP ERROR\n"
    # Make sure that the variable name is a string.
    check_type(var_name, str,
               "the name of the variable that is being checked (for whether it is a member of the accepted values set)",
               prefix=in_set_setup_prefix)
    # Make sure that the accepted values are provided as a list.
    check_type(accepted_values, list, f"the set of accepted values for {var_name}", prefix=in_set_setup_prefix)
    # Check if the prefix is a string.
    check_type(prefix, str,
               "the prefix for any potential error messages", prefix=in_set_setup_prefix)
    # Check if the input value is an element in the accepted values list.
    is_in_set = input_value in accepted_values
    # Raise a ValueError if the input is not one of the valid values.
    if not is_in_set:
        # Start the error message with the optional prefix parameter.
        error_string = prefix
        # Add information about the value we were asked to check.
        error_string += "SUBMITTED VALUE: " + str(input_value) + "\n"
        # Inform the user that the value is not acceptable.
        error_string += ("The value that you have provided for "
                         + var_name + " is not in the set of accepted values for this parameter.\n")
        # Tell the user which values are acceptable for this variable.
        error_string += " Please provide a value from the following list:\n"
        error_string += str(accepted_values)
        # Raise the ValueError with the constructed message.
        raise ValueError(error_string)
    return is_in_set

def check_matrix_values_in_range(input_matrix, min_value, max_value, var_name, prefix=""):
    pass

# def check_font_name(gui, font_name, prefix=""):
#     # Make sure that the font name is a string.
#     check_type(str, type(font_name),
#                f"the font family that should be used for the text (e.g., \"{gui.DEFAULT_FONT_NAME}\")",
#                prefix=prefix)
#     # Make sure that the GUI can support the font.
#     check_value_is_in_set(font_name, gui.get_supported_font_names(),
#                               f"the font family that should be used for the text (e.g., \"{gui.DEFAULT_FONT_NAME}\")",
#                               prefix=prefix)