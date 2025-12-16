class It_:
    __slots__ = ("f",)

    def __init__(self, f=lambda x: x) -> None:
        self.f = f

    def __call__(self, x):
        return self.f(x)

    def __lt__(self, other) -> "It_":
        return It_(lambda x: self.f(x) < other)

    def __gt__(self, other) -> "It_":
        return It_(lambda x: self.f(x) > other)

    def __le__(self, other) -> "It_":
        return It_(lambda x: self.f(x) <= other)

    def __ge__(self, other) -> "It_":
        return It_(lambda x: self.f(x) >= other)

    def __matmul__(self, other: "It_") -> "It_":
        return It_(lambda x: self.f(other.f(x)))

    def __eq__(self, other):  # type: ignore
        return It_(lambda x: self.f(x) == other)

    def __ne__(self, other):  # type: ignore
        return It_(lambda x: self.f(x) != other)

    def __or__(self, other: "It_") -> "It_":
        return It_(lambda x: self.f(x) or other.f(x))

    def __and__(self, other: "It_") -> "It_":
        return It_(lambda x: self.f(x) and other.f(x))

    def __sub__(self, other) -> "It_":
        if isinstance(other, It_):
            return It_(lambda x: self.f(x) - other.f(x))
        return It_(lambda x: self.f(x) - other)

    def __add__(self, other) -> "It_":
        if isinstance(other, It_):
            return It_(lambda x: self.f(x) - other.f(x))
        return It_(lambda x: self.f(x) + other)

    def __mul__(self, other) -> "It_":
        if isinstance(other, It_):
            return It_(lambda x: self.f(x) - other.f(x))
        return It_(lambda x: self.f(x) * other)

    def __truediv__(self, other) -> "It_":
        if isinstance(other, It_):
            return It_(lambda x: self.f(x) - other.f(x))
        return It_(lambda x: self.f(x) / other)

    def __floordiv__(self, other) -> "It_":
        if isinstance(other, It_):
            return It_(lambda x: self.f(x) - other.f(x))
        return It_(lambda x: self.f(x) // other)

    def __mod__(self, other) -> "It_":
        if isinstance(other, It_):
            return It_(lambda x: self.f(x) - other.f(x))
        return It_(lambda x: self.f(x) % other)


It = It_()
