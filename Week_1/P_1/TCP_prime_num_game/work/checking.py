from multiprocessing import current_process

# MSG = "{process} is currently verifying whether the {num} is prime"


# def print_processing_msg(number):
#     print(MSG.format(process=current_process().name, num=str(number)), )


def is_prime(number):
    """returns True if number
    is prime, False otherwise"""
    if number <= 1:
        # print_processing_msg(number)
        return False
    if number <= 3:
        # print_processing_msg(number)
        return True
    for divisor in range(3, number, 2):  # skip even numbers: as a prime number (larger than 2) cannot be even
        if number % divisor == 0:
            # print_processing_msg(number)
            return False
    # print_processing_msg(number)
    return True
