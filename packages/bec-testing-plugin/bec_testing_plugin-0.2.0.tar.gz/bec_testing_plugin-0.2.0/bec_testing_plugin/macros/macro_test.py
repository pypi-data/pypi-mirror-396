from time import sleep


def macro_test(a: int, b: int):
    print(f"Calculating {a}+{b}...")
    print(f"{a+b}")
    return a + b


def macro_test_takes_time(a: int, b: int):
    print(f"Calculating {a}+{b}...")
    sleep(3)
    print("thinking...")
    sleep(3)
    print(f"{a+b}")
    return a + b
