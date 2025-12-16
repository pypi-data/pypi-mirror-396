import re
from typing import Literal

from inspect_ai.scorer import Score, Scorer, Target, accuracy, scorer, stderr
from inspect_ai.solver import TaskState

Mode = Literal["exact", "start", "contains", "end"]


@scorer(metrics=[accuracy(), stderr()])
def match(
    mode: Mode = "exact",
    case: bool = True,
    numeric: bool = False,
) -> Scorer:
    """Matches output with target assigning 'C' for correct and 'I' for incorrect.

    If `numeric` is True, treats output and taraget as numbers when
    matcing.

    If `case` is True, string comparison is case sensitive.
    """

    async def score(state: TaskState, target: Target) -> Score:
        # Never compare leading or trailing whitespace
        output = state.output.completion.strip()
        expect = target.text.strip()

        if numeric:
            return match_numeric(mode, expect, output)
        else:
            return match_str(mode, case, expect, output)

    return score


class NumError(Exception):
    def __init__(self, answer: str):
        self.answer = answer


def match_numeric(mode: Mode, target: str, output: str):
    # Target must be numeric
    try:
        expect_val = to_number(target)
    except ValueError:
        return Score(
            value="I",
            explanation="Target is non-numeric, skipping comparison",
        )

    # Get available numbers as candidate values - mode used to limit
    # tokens that are parsed
    try:
        got_vals = output_nums(mode, output)
    except NumError as e:
        # Raised for modes that target specific tokens (e.g. 'exact',
        # 'start', 'end') - will not fire for 'contains'
        return Score(
            value="I",
            answer=e.answer,
            explanation="Answer is non-numeric",
        )

    # Compare got vals to target based on mode
    if mode in ("exact", "start", "end"):
        # These modes are expected to match a single number value
        assert len(got_vals) == 1, got_vals
        got_val = got_vals[0]
        value = "C" if got_val == expect_val else "I"
        explanation = {
            ("exact", "C"): "Answer equals target (numeric)",
            ("exact", "I"): "Answer does not equal target (numeric)",
            ("start", "C"): "Answer starts with target (numeric)",
            ("start", "I"): "Answer does not start with target (numeric)",
            ("end", "C"): "Answer ends with target (numeric)",
            ("end", "I"): "Answer does not end with target (numeric)",
        }[(mode, value)]
        return Score(
            value=value,
            answer=str(got_val),
            explanation=explanation,
        )
    else:
        assert mode == "contains", mode
        # This mode can match zero or more number values - if there are
        # no numbers, there's no answer to compare
        if not got_vals:
            return Score(
                value="I",
                explanation="Output does not contain numbers",
            )

        # Try to find a matching got number
        try:
            got_val = next((val for val in got_vals if val == expect_val))
        except StopIteration:
            # No matching answers - use got vals as answer
            if len(got_vals) == 1:
                answer = str(got_vals[0])
            else:
                answer = (
                    f"Possible answers: {', '.join([str(val) for val in got_vals])}"
                )
            return Score(
                value="I",
                answer=answer,
                explanation="Answer does not contain target (numeric)",
            )
        else:
            # Output contains target
            return Score(
                value="C",
                answer=str(got_val),
                explanation="Answer contains target (numeric)",
            )


NUM_END_STRIP_P = re.compile(r"[^0-9]+$")


def output_nums(mode: Mode, output: str) -> list[int | float]:
    if mode == "exact":
        answer = output
        try:
            return [to_number(answer)]
        except ValueError:
            raise NumError(answer)
    elif mode == "start":
        token = output.split(maxsplit=1)[0]
        answer = NUM_END_STRIP_P.sub("", token)
        try:
            return [to_number(answer)]
        except ValueError:
            raise NumError(token)
    elif mode == "end":
        token = output.rsplit(maxsplit=1)[-1]
        answer = NUM_END_STRIP_P.sub("", token)
        try:
            return [to_number(answer)]
        except ValueError:
            raise NumError(token)
    else:
        assert mode == "contains", mode
        nums = []
        for token in output.split():
            answer = NUM_END_STRIP_P.sub("", token)
            try:
                nums.append(to_number(answer))
            except ValueError:
                pass
        return nums


NUM_STRIP_P = re.compile(r"(^[^0-9\.\-\+]+|[,]|[^0-9\.\-\+]+$)")


def to_number(s: str) -> float | int:
    s = NUM_STRIP_P.sub("", s)
    try:
        return int(s)
    except ValueError:
        return float(s)


# Trailing periods are currently the only trailing punctuation that's
# stripped for 'end' match
STR_END_STRIP_P = re.compile(r"[\.]$")


def match_str(mode: Mode, case: bool, target: str, output: str):
    # Use lower case for case-insensitive match
    got_val = output if case else output.lower()
    expect_val = target if case else target.lower()

    # If mode is 'end', strip trailing punctuation
    if mode == "end":
        got_val = STR_END_STRIP_P.sub("", got_val)

    # Match based on mode
    if mode == "exact":
        match = got_val == expect_val
    elif mode == "start":
        match = got_val.startswith(expect_val)
    elif mode == "end":
        match = got_val.endswith(expect_val)
    else:
        assert mode == "contains", mode
        match = expect_val in got_val

    value = "C" if match else "I"

    # Answer should not be output in cases where mode looks for partial
    # match (start, end, and contains) - use expect_val rather than
    # target as output may contain a different case for answer for
    # case-insensitive matches
    if mode == "exact":
        answer = output
    else:
        answer = expect_val if match else None

    # Exaplanation based on mode and match
    explanation = {
        ("exact", "C"): "Answer matches target",
        ("exact", "I"): "Answer does not match target",
        ("start", "C"): "Answer starts with target",
        ("start", "I"): "Answer does not start with target",
        ("end", "C"): "Answer ends with target",
        ("end", "I"): "Answer does not end with target",
        ("contains", "C"): "Answer contains target",
        ("contains", "I"): "Answer does not contain target",
    }[(mode, value)]
    if not case:
        explanation += " (ignore case)"

    return Score(
        value=value,
        answer=answer,
        explanation=explanation,
    )
