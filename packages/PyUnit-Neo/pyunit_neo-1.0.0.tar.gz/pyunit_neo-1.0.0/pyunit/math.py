"""Mathematical and arithmetic functions for trigonometry and geometric values.
The given unit must be initialized, or it will almost always falter.

Use either floats or distances. When the typing annotiates distance, you can also 
enter a floating value. Be aware, that the return value will still be either a distance 
or a angle."""

from ._internal import Distance, Angle
import math # type: ignore

degrees = math.degrees
radians = math.radians

def alpha(dx, dy):
    """Get the angle between two points (angle from x-axis to vector (dx,dy))."""
    # Use atan2 to correctly handle signs/quadrants and dx == 0.
    degrees = math.degrees(math.atan2(dy, dx))
    return Angle(degrees)

def alpha_cos(dx, h):
    """Get the angle from adjacent (dx) and hypotenuse (h): alpha = acos(dx / h)."""
    if h == 0:
        raise ValueError("hypotenuse must be non-zero")
    ratio = clamp(dx / h)
    degrees = math.degrees(math.acos(ratio) * 180 / math.pi)
    return Angle(degrees)

def alpha_sin(dy, h):
    """Get the angle from opposite (dy) and hypotenuse (h): alpha = asin(dy / h)."""
    if h == 0:
        raise ValueError("hypotenuse must be non-zero")
    ratio = clamp(dy / h)
    degrees = math.degrees(math.asin(ratio) * 180 / math.pi)
    return Angle(degrees)

def h(dx, dy):
    """Get the distance (hypotenuse) between two points (dx, dy)."""
    return Distance(math.hypot(dx, dy))

def dx(dy, alpha):
    """Get the dx (adjacent) given dy (opposite) and angle.
    tan(alpha) == dy / dx  => dx = dy / tan(alpha)
    """
    tan_a = math.tan(alpha)
    if tan_a == 0:
        raise ValueError("tan(angle) == 0 -> dx would be infinite (angle is 0 or pi).")
    return Distance(dy / tan_a)

def dy(dx, alpha):
    """Get the dy (opposite) given dx (adjacent) and angle.
    tan(angle) == dy / dx  => dy = dx * tan(angle)
    """
    return Distance(math.tan(alpha) * dx)

def h_cos(dx, alpha):
    """Get the hypotenuse given dx (adjacent) and angle.
    cos(alpha) == dx / h  => h = dx / cos(alpha)
    """
    cos_a = math.cos(alpha)
    if cos_a == 0:
        raise ValueError("cos(angle) == 0 -> hypotenuse would be infinite (angle is pi/2 or 3pi/2).")
    return Distance(dx / cos_a)

def h_sin(dy, alpha):
    """Get the hypotenuse given dy (opposite) and angle.
    sin(alpha) == dy / h  => h = dy / sin(alpha)
    """
    sin_a = math.sin(alpha)
    if sin_a == 0:
        raise ValueError("sin(angle) == 0 -> hypotenuse would be infinite (angle is 0 or pi).")
    return Distance(dy / sin_a)

def dx_h(dy, h):
    """Get the dx (adjacent) given dy (opposite) and hypotenuse h.
    dx = sqrt(h**2 - dy**2)  (raises ValueError if h < |dy|)
    """
    if h < abs(dy):
        raise ValueError("hypotenuse must be >= absolute value of dy")
    return Distance(math.sqrt(max(0.0, h ** 2 - dy ** 2)))

def dy_h(dx, h):
    """Get the dy (opposite) given dx (adjacent) and hypotenuse h.
    dy = sqrt(h**2 - dx**2)  (raises ValueError if h < |dx|)
    """
    if h < abs(dx):
        raise ValueError("hypotenuse must be >= absolute value of dx")
    return Distance(math.sqrt(max(0.0, h ** 2 - dx ** 2)))

def dx_h2(alpha, h):
    """Get the dx (adjacent) given by angle and hypotenuse h.
    dx = cos(alpha) * h"""
    return Distance(math.cos(alpha) * h)

def dy_h2(alpha, h):
    """Get the dy (oposite) given by angle and hypotenuse h.
    dy = sin(alpha) * h"""
    return Distance(math.sin(alpha) * h)

def distance(dx, dy): # Alias to h
    """Get the distance (hypotenuse) between two points."""
    return h(dx, dy)

def step(x, factor):
    """Return a distance with the factor of the original."""
    return Distance(x * factor)

def distance_sq(dx, dy):
    """Return squared Euclidean length (avoids sqrt)."""
    return Distance(dx * dx + dy * dy)

def to_polar(dx, dy):
    """Return (r, alpha) polar coordinates for vector (dx, dy)."""
    return Distance(math.hypot(dx, dy)), Angle(math.degrees(math.atan2(dy, dx)))

def from_polar(r, alpha):
    """Return Cartesian coordinates (dx, dy) from polar (r, alpha)."""
    return Distance(r * math.cos(alpha)), Distance(r * math.sin(alpha))

def wrap_angle(alpha):
    """Normalize angle into the interval (-pi, pi]."""
    return Angle(math.degrees(((math.radians(alpha) + math.pi) % (2 * math.pi)) - math.pi))

def angle_diff(alpha1, alpha2):
    """Return minimal signed difference (alpha2 - alpha1) normalized to (-pi, pi]."""
    return wrap_angle(math.radians(alpha2) - math.radians(alpha1))

def mean_angle(angles):
    """Compute circular mean of the provided angles using vector summation.

    If the resultant vector is near-zero (angles cancel), the function returns 0.0.
    """
    s = 0.0
    c = 0.0
    count = 0
    for a in angles:
        s += math.sin(a)
        c += math.cos(a)
        count += 1
    if count == 0:
        raise ValueError("mean_angle requires at least one angle")
    # If magnitude is near-zero angles are cancelling; return 0 to avoid unstable atan2.
    if math.isclose(s, 0.0, abs_tol=1e-15) and math.isclose(c, 0.0, abs_tol=1e-15):
        return 0.0
    return Angle(math.degrees(math.atan2(s, c)))

def angle_between(v1x, v1y, v2x, v2y):
    """Return signed angle from vector v1 to v2 in (-pi, pi].

    Uses atan2(cross, dot).
    """
    d = dot(v1x, v1y, v2x, v2y)
    c = cross(v1x, v1y, v2x, v2y)
    return Angle(math.degrees(math.atan2(c, d)))

def dot(dx1, dy1, dx2, dy2):
    """2D dot product."""
    return dx1 * dx2 + dy1 * dy2

def cross(dx1, dy1, dx2, dy2):
    """Scalar 2D cross product (z component) = dx1*dy2 - dy1*dx2."""
    return dx1 * dy2 - dy1 * dx2

def norm2(dx, dy):
    """Alias for squared norm (same as distance_sq)."""
    return distance_sq(dx.m, dy.m)

def normalize(dx, dy):
    """Return unit vector in direction of (dx, dy). Returns (0.0, 0.0) for zero-length input."""
    r = math.hypot(dx, dy)
    if math.isclose(r, 0.0, abs_tol=1e-15):
        return 0.0, 0.0
    return Distance(dx.m / r), Distance(dy.m / r)

def scale_to(dx, dy, length):
    """Scale vector (dx, dy) to the provided length. Returns (0,0) when input is zero vector.

    If length is negative a ValueError is raised.
    """
    if length < 0:
        raise ValueError("length must be non-negative")
    ux, uy = normalize(dx, dy)
    return Distance(ux * length), Distance(uy * length)

def rotate(dx, dy, alpha):
    """Rotate vector (dx, dy) by angle alpha (radians) counter-clockwise."""
    ca = math.cos(alpha)
    sa = math.sin(alpha)
    return dx * math.radians(ca) - dy * math.radians(sa), dx * math.radians(sa) + dy * math.radians(ca)

def project_point_on_line(px, py, ax, ay, bx, by):
    """Project point P(px,py) onto the infinite line defined by A(ax,ay) -> B(bx,by).

    Returns the coordinates of the projection (can be outside segment AB).
    """
    abx = bx - ax
    aby = by - ay
    denom = distance_sq(abx, aby)
    if math.isclose(denom, 0.0, abs_tol=1e-15):
        # A and B are the same point; projection is A
        return ax, ay
    apx = px - ax
    apy = py - ay
    t = dot(apx, apy, abx, aby) / denom
    return ax + t * abx, ay + t * aby

def distance_point_to_segment(px, py, ax, ay, bx, by):
    """Shortest distance from point P(px,py) to segment AB."""
    abx = bx - ax
    aby = by - ay
    denom = distance_sq(abx, aby)
    if math.isclose(denom, 0.0, abs_tol=1e-15):
        # AB is a single point
        return math.hypot(px - ax, py - ay)
    apx = px - ax
    apy = py - ay
    t = dot(apx, apy, abx, aby) / denom
    t_clamped = clamp(t, 0.0, 1.0)
    projx = ax + t_clamped * abx
    projy = ay + t_clamped * aby
    return math.hypot(px - projx, py - projy)

def lerp(a, b, t):
    """Linear interpolation between scalars a and b by t (t typically in [0,1])."""
    return a + (b - a) * t

def lerp_point(ax, ay, bx, by, t):
    """Linear interpolation between two points A and B."""
    return lerp(ax, bx, t), lerp(ay, by, t)

def step_towards(current, target, max_step):
    """Move `current` toward `target` by at most `max_step` (absolute distance).

    If max_step < 0 a ValueError is raised.
    """
    if max_step < 0:
        raise ValueError("max_step must be non-negative")
    delta = target - current
    if abs(delta) <= max_step:
        return target
    return Distance(current + math.copysign(max_step, delta))

def clamp(x, a, b):
    """Clamp x into the closed interval [a, b]."""
    if a > b:
        raise ValueError("clamp: lower bound a must be <= upper bound b")
    return max(a, min(b, x))

def sign(x):
    """Return the sign of x: -1 for negative, 0 for zero, +1 for positive."""
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0

def lerp_angle(a1, a2, t):
    """Interpolate angles on the circle using shortest path.

    t==0 -> a1, t==1 -> a2. Result is normalized to (-pi, pi].
    """
    diff = math.radians(angle_diff(a1, a2))
    return wrap_angle(math.radians(a1) + diff * t)

def shortest_rotation(a_from, a_to):
    """Return the signed smallest rotation to bring a_from to a_to (in radians)."""
    return angle_diff(a_from, a_to)

def is_angle_close(a1, a2, tol):
    """Return True if angles a1 and a2 are within tol radians using circular difference."""
    return abs(math.radians(angle_diff(a1, a2))) <= tol