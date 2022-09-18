import helper as h


def main():
    while True:
        inp = input("<")
        if len(inp) > 0:
            print(h.is_valid_request(inp))


if __name__ == "__main__":
    main()

