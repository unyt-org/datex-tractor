class EllipticCurve:
    def __init__(self, a: int, b: int, p: int):
        """Finite field F_p: y^2 = x^3 + ax + b mod p"""
        self.a = a
        self.b = b
        self.p = p

        assert (4 * a**3 + 27 * b**2) % p != 0, "Singular curve"

    def is_on_curve(self, x: int, y: int) -> bool:
        return (y**2 - (x**3 + self.a * x + self.b)) % self.p == 0


class ECPoint:
    def __init__(self, curve: EllipticCurve, x: int | None, y: int | None):
        """A point on an elliptic curve"""
        self.curve = curve
        self.x = x
        self.y = y

        # Ignore point at infinity
        if x is not None and y is not None:
            assert curve.is_on_curve(x, y), "Point is not on curve"

    def __repr__(self):
        return f"({self.x}, {self.y})" if self.x is not None else "Point at Infinity"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __neg__(self):
        """Negation of a point P = (x, y) -> -P = (x, -y mod p)"""
        return ECPoint(self.curve, self.x, -self.y % self.curve.p)

    def __add__(self, other):
        """Point addition P + Q"""
        # Identity
        if self.x is None:
            return other
        if other.y is None:
            return self

        # TODO #270: Define addition for points on elliptic Cruves
        raise NotImplementedError


    def double(self):
        """Point doubling: P + P = 2P"""
        if self.x is None or self.y is None:
            return self

        # Calculate slope: m = (3x^2 + a) / (2y) mod p
        m = ((3 * self.x**2 + self.curve.a) * pow(2 * self.y, -1, self.curve.p)) % self.curve.p

        # Calculate new x and y
        x3 = (m**2 - 2 * self.x) % self.curve.p
        y3 = (m * (self.x - x3) - self.y) % self.curve.p

        return ECPoint(self.curve, x3, y3)

    def multiply(self, k: int):
        """Scalar multiplication: k * P using double-and-add"""
        result = ECPoint(self.curve, None, None)
        temp = self  # Current power of P

        while k > 0:
            if k & 1:
                result += temp
            temp = temp.double()

            # Shift right
            k >>= 1

        return result
