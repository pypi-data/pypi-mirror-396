from os import system, name
from typing import Callable

def _display(prompt: str, body_text: str) -> int | ValueError:
    break_hard = "=============================="
    break_soft = "------------------------------"
    input_prompt = ":: "
    system("cls") if name == "nt" else system("clear")
    print(f"{break_hard}\n{prompt}\n{break_soft}\n{body_text}\n{break_hard}")
    try:
        return int(input(input_prompt))
    except ValueError as e:
        return e

def _menu(prompt: str, body_text: str, validate: Callable[[int], tuple[bool, str]]) -> int:
    while True:
        response = _display(prompt, body_text)
        if type(response) is int:
            is_valid, err_mseg = validate(response)
            if is_valid:
                return response
            prompt = f"{prompt}\n{err_mseg}"
        if type(response) is ValueError: 
            prompt = f"{prompt}\nPlease only enter whole numbers"

def int_menu(prompt: str, min: int, max: int) -> int:
    validate: Callable[[int], tuple[bool, str]] = lambda x: (
        min <= x <= max,
        f"Response is out of range. Please try again."
    )
    body_text = f"Please enter a number between {min} and {max}."
    return _menu(prompt, body_text, validate)


def list_menu(prompt: str, options: list[str]) -> int:
    validate: Callable[[int], tuple[bool, str]] = lambda x: (
        0 <= x < len(options),
        f"Response is not in the available options. Please try another."
    )
    body_text = "\n".join([f"{i}: {options[i]}" for i in range(len(options))])
    return _menu(prompt, body_text, validate)

def multiple_choice_menu(prompt: str, options: list[str]) -> list[int]:
    options.insert(0, "Done")
    selected: list[int] = []
    while True:
        choice = list_menu(prompt, options)
        if choice == 0:
            return selected
        if options[choice].startswith("* "):
            options[choice] = options[choice][2:]
            selected.remove(choice)
        else:
            options[choice] = f"* {options[choice]}"
            selected.append(choice)

def _test():
    options = ["Apple", "Banana", "Cherry", "Date"]
    min_val = 1
    max_val = 10
    a = list_menu("Select a fruit from the list below:", options)
    b = int_menu("Select a number from the range below:", min_val, max_val)
    c = multiple_choice_menu("Select multiple fruits from the list below:", options)
    print(a)
    print(b)
    print(c)

if __name__ == "__main__":
    _test()

    