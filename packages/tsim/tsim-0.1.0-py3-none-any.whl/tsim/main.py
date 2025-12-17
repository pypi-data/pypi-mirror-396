ocr_correction_map = {
    "0": "O",
    "1": "I",
    "2": "Z",
    "3": "E",
    "4": "A",
    "5": "S",
    "6": "G",
    "7": "T",
    "8": "B",
    "9": "G",
    "@": "A",
    "$": "S",
    "|": "I",
    "!": "I",
    "(": "C",
}


def get_confidence(received_str: str, expected_str: str, mode: str):
    """
    Returns the confidence/error of similarity of two strings

    :param received_str: The string to compare
    :param expected_str: The string to be expected in the comparison
    :param mode: "c" to return confidence, "e" to return the error
    :return: Confidence (0-1)/Error depending on the mode used
    """
    received_str = received_str.lower()
    expected_str = expected_str.lower()

    error_count: int = 0
    char_at: int = 0
    while char_at != len(received_str) and char_at != len(expected_str):
        if received_str[char_at] == expected_str[char_at]:
            char_at += 1
            continue

        if len(received_str) < len(expected_str):
            received_str_temp: str = list(received_str)
            received_str_temp.insert(char_at, expected_str[char_at])
            received_str = "".join(received_str_temp)
            error_count += 1
            continue

        if len(received_str) > len(expected_str):
            expected_str_temp: str = list(expected_str)
            expected_str_temp.insert(char_at, received_str[char_at])
            expected_str = "".join(expected_str_temp)
            error_count += 1
            continue

        error_count += 1
        char_at += 1

    if mode == "c":
        confidence: float = 1 - (error_count / len(received_str))

        return confidence

    if mode == "e":
        return error_count


def get_abbreviated_confidence(received_str: str, expected_str: str, mode: str):
    """
    Returns the confidence of similarity of two strings taking into account abbreviated part of the string

    :param received_str: The string to compare
    :param expected_str: The string to be expected in the comparison
    :param mode: "c" to return confidence, "e" to return the error
    :return: Confidence (0-1)/Error depending on the mode used
    """
    received_str = received_str.replace(".", "")
    expected_str = expected_str.replace(".", "")

    if len(received_str) <= 2 and (received_str[0] == expected_str[0]):
        return 0.85
    elif len(expected_str) <= 2 and (received_str[0] == expected_str[0]):
        return 0.85
    else:
        return get_confidence(received_str, expected_str, mode)


def get_name_confidence(received_name: str, expected_name: str):
    """
    Returns the confidence of similarity between two names

    :param received_name: The name to compare
    :param expected_name: The name to be expected in the comparison
    :return: The confidence level of the similarity of the names (0-1)
    """
    received_name = received_name.replace(".", "")
    expected_name = expected_name.replace(".", "")

    for character in ocr_correction_map:
        received_name = received_name.replace(character, ocr_correction_map[character])
        expected_name = expected_name.replace(character, ocr_correction_map[character])

    received_list = received_name.strip().split()
    expected_list = expected_name.strip().split()

    if len(received_list) != len(expected_list):
        return 0

    error_count = 0

    expected_list.sort()
    received_list.sort()

    for i in range(len(received_list)):
        error_count += get_abbreviated_confidence(
            received_list[i], expected_list[i], "e"
        )

    return 1 - error_count / len(received_name)
