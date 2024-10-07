import os


class RegularExpression:
    def __init__(self, input_source: str):
        self.data = self._read_regex(input_source).replace("+", "|")

    @staticmethod
    def _read_regex(input_source: str) -> str:
        if os.path.isfile(input_source) or input_source.startswith("@"):
            file_path = (
                input_source[1:] if input_source.startswith("@") else input_source
            )
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read().strip()
        return input_source.strip()

    def get_regex(self) -> str:
        return self.data

    def to_postfix(self) -> str:
        return self._regex_to_postfix(self.data)

    @staticmethod
    def _is_alphabet(c: str) -> bool:
        return c not in {"*", ".", "|", "(", ")"}

    @classmethod
    def _add_concat_symbol(cls, reg_exp: str) -> str:
        new_reg_exp = ""
        for i, current_char in enumerate(reg_exp):
            if i > 0:
                prev_char = reg_exp[i - 1]
                if (prev_char in ")*" or cls._is_alphabet(prev_char)) and (
                    current_char == "(" or cls._is_alphabet(current_char)
                ):
                    new_reg_exp += "."
            new_reg_exp += current_char
        return new_reg_exp

    @classmethod
    def _regex_to_postfix(cls, reg_exp: str) -> str:
        priority = {"*": 3, ".": 2, "|": 1}
        postfix_exp = ""
        operator_stack = []
        parentheses_balance = 0

        reg_exp = cls._add_concat_symbol(reg_exp)

        for i, current_char in enumerate(reg_exp):
            if cls._is_alphabet(current_char):
                postfix_exp += current_char
            elif current_char == "(":
                operator_stack.append(current_char)
                parentheses_balance += 1
            elif current_char == ")":
                if parentheses_balance <= 0:
                    raise ValueError(
                        "Invalid regular expression: Unmatched closing parenthesis"
                    )
                parentheses_balance -= 1
                while operator_stack and operator_stack[-1] != "(":
                    postfix_exp += operator_stack.pop()
                if not operator_stack:
                    raise ValueError(
                        "Invalid regular expression: Unmatched closing parenthesis"
                    )
                operator_stack.pop()  # opening parenthesis
            elif current_char in priority:
                if current_char == "*":
                    if not postfix_exp or postfix_exp[-1] == "*":
                        raise ValueError(
                            "Invalid regular expression: Misplaced asterisk"
                        )
                    if i < len(reg_exp) - 1 and reg_exp[i + 1] == "*":
                        raise ValueError(
                            "Invalid regular expression: Consecutive asterisks"
                        )
                while (
                    operator_stack
                    and operator_stack[-1] != "("
                    and priority.get(operator_stack[-1], 0) >= priority[current_char]
                ):
                    postfix_exp += operator_stack.pop()
                operator_stack.append(current_char)
            else:
                raise ValueError(
                    f"Invalid regular expression: Unknown character '{current_char}'"
                )

        if parentheses_balance != 0:
            raise ValueError(
                "Invalid regular expression: Unmatched opening parenthesis"
            )

        while operator_stack:
            postfix_exp += operator_stack.pop()

        return postfix_exp

    def __str__(self) -> str:
        return self.data

    def print(self) -> None:
        print(str(self))

    def fix(self) -> "RegularExpression":
        new_string = self.data

        def do(s):
            s = s.replace("()", "")
            s = s.replace("(|", "(")
            s = s.replace("|)", ")")
            return s

        while do(new_string) != new_string:
            new_string = do(new_string)

        return RegularExpression(new_string)
