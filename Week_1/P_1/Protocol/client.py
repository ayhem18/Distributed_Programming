import grpc
import service_pb2_grpc as pb2_grpc
import service_pb2 as pb2
import re


def is_reverse_command(string):

    pattern = r'reverse\s+.+'
    match = re.match(pattern, string)
    if match is None:
        print(f"{string} does not respect the reverse command pattern")
        return None
    if match.end() - match.start() != len(string):  # check if the entire string matches with the pattern
        print(f"{string} partially matches with the pattern")
        return None

    splits = re.split(r'\s+', string)
    string_start_index = string.find(splits[1])
    return string[string_start_index:]


def is_split_command(string):
    pattern = r'split\s+.+'
    match = re.match(pattern, string)

    if match is None:
        print(f"{string} does not respect the split command pattern")
        return None

    # the match object is not None: the beginning of the string match with the pattern
    if match.end() - match.start() != len(string):  # check if the entire string matches with the pattern
        print(f"{string} partially matches with the pattern")
        return None

    parts = re.split(r'\s+', string)
    # the first part represents the split command
    # the rest should be concatenated together
    # and set as single string to the server
    return " ".join(parts[1:]), r'\s+'


def is_prime_command(string):
    pattern = r'isprime\s+(\d+\s+)*(\d)+'
    match = re.match(pattern, string)

    if match is None:
        print(f"{string} does not respect the isprime command pattern")
        return None

    # the match object is not None: the beginning of the string match with the pattern
    if match.end() - match.start() != len(string):  # check if the entire string matches with the pattern
        print(f"{string} partially matches with the pattern")
        return None

    numbers = re.split(r"\s+", string)
    return [int(n) for n in numbers[1:]]  # the numbers are saved string from the index 1


def generate_messages(numbers: list):
    for n in numbers:
        # print(f"Sending {str(n)} to the server !!")
        msg = pb2.isPrimeRequest(number=n)
        yield msg


def main():
    channel = grpc.insecure_channel("127.0.0.1:5555")
    # set the reverse service
    client_reverse = pb2_grpc.reverseStub(channel)

    # set the split service
    client_split = pb2_grpc.splitStub(channel)

    # set the isPrime service
    client_is_prime = pb2_grpc.isPrimeStub(channel)

    while True:
        user_input = input("Please enter your command\n")

        # check if the command is prime number verification

        prime = is_prime_command(user_input)
        if prime is not None:
            for reply in client_is_prime.is_prime(generate_messages(prime)):
                print(reply.number_primer)

            continue

        # check if the command is splitting
        split = is_split_command(user_input)

        if split is not None:
            split_pair = pb2.SplitRequest(text=split[0], delimiter=split[1])
            print(client_split.splitString(split_pair))
            continue

        # check if the command is reverse
        text_to_reverse = is_reverse_command(user_input)

        if text_to_reverse is not None:
            reverse_request = pb2.ReverseRequest(text=text_to_reverse)
            print(client_reverse.ReverseString(reverse_request))


if __name__ == "__main__":
    main()
