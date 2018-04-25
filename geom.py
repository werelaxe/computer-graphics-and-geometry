from copy import copy
from math import sqrt

EPS = 0.00001


class PointsDict(dict):
    def __getitem__(self, item):
        for k, v in self.items():
            if abs(k.x - item.x) < EPS and abs(k.y - item.y) < EPS:
                return v


class Point:
    def __init__(self, *args):
        if len(args) == 2:
            self.x, self.y = args
        elif len(args) == 1:
            self.x, self.y = args[0]
        else:
            raise ValueError

    def __hash__(self):
        return hash(self.x) ^ hash(self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return "Point({}, {})".format(self.x, self.y)

    @property
    def coords(self):
        return self.x, self.y

    def dto(self, p):
        return sqrt((p.x - self.x) ** 2 + (p.y - self.y) ** 2)


class Segment:
    def __init__(self, *args):
        self.ks = []
        if len(args) == 1:
            args = args[0]
        if len(args) == 2:
            self.first, self.second = args
        elif len(args) == 4:
            self.first = Point(*args[:2])
            self.second = Point(*args[2:])
        else:
            raise ValueError
        self.a, self.b, self.c = self.get_ks()
        if abs(self.a) > EPS:
            self.b /= self.a
            self.c /= self.a
            self.a = 1
        elif abs(self.b) > EPS:
            self.a /= self.b
            self.c /= self.b
            self.b = 1
        else:
            raise ValueError("{} {} {}".format(self.a, self.b, self.c))

    def get_ks(self):
        return [
            self.first.y - self.second.y,
            self.second.x - self.first.x,
            self.first.x * self.second.y - self.second.x * self.first.y
        ]

    def intersects(self, other):
        if abs(self.a * other.b - other.a * self.b) < EPS:
            return None
        if self.a == 1:
            y = (other.a * self.c - other.c) / (other.b - other.a * self.b)
            x = -self.b * y - self.c
        elif self.b == 1:
            x = (other.b * self.c - other.c) / (other.a - self.a * other.b)
            y = -self.a * x - self.c
        else:
            raise ValueError
        suggested_point = Point(x, y)
        if suggested_point in self and suggested_point in other:
            return suggested_point

    def __contains__(self, point):
        if abs(self.a * point.x + self.b * point.y + self.c) > EPS:
            return False
        flag0 = min(self.first.x, self.second.x) <= point.x <= max(self.first.x, self.second.x)
        flag1 = min(self.first.y, self.second.y) <= point.y <= max(self.first.y, self.second.y)
        return flag0 and flag1

    def __repr__(self):
        return "Segment({}, {})".format(self.first, self.second)


class Polygon:
    def __init__(self, points):
        self.points = []
        if type(points[0]) == Point:
            self.points = points
        elif type(points[0]) == int:
            if len(points) % 2 == 1:
                raise ValueError
            it = iter(points)
            self.points = list(map(Point, zip(it, it)))
        else:
            raise ValueError
        self.segments = self.get_segments()
        self.get_index_by_segment = PointsDict([(self.segments[i], i) for i in range(len(self.segments))])
        self.get_index_by_point = PointsDict([(self.points[i], i) for i in range(len(self.points))])
        self._pure_points = copy(self.points)
        self.epoints = []

    def __repr__(self):
        return "Polygon({})".format(", ".join(str(p) for p in self.points))

    @property
    def pure_points(self):
        return self._pure_points

    def extend_points(self, other):
        for seg in self.segments:
            int_points = sorted(other.intersects_with(seg), key=lambda p: p.dto(seg.first))
            self.epoints.append(seg.first)
            self.epoints.extend(int_points)
        self.segments = self.get_segments()
        self.points = self.epoints
        self.get_index_by_segment = PointsDict([(self.segments[i], i) for i in range(len(self.segments))])
        self.get_index_by_point = PointsDict([(self.points[i], i) for i in range(len(self.points))])

    def intersects_with(self, segment: Segment):
        int_points = []
        for seg in self.segments:
            int_point = segment.intersects(seg)
            if int_point is not None:
                int_points.append(int_point)
        return int_points

    def get_segments(self):
        return list(map(Segment, zip(self.points[:-1], self.points[1:]))) + [Segment(self.points[-1], self.points[0])]

    def __contains__(self, item):
        for seg in self.segments:
            if item in seg:
                return True
        inf = Point(1234567890, 999999999)
        return len(list(filter(lambda x: x.intersects(Segment(item, inf)) is not None, self.segments))) % 2 == 1

    def find_segment_by_point(self, point):
        for seg in self.segments:
            if point in seg:
                return seg

    def _find_start_point(self, other, used):
        for point in self.points:
            if (point not in other) and (point not in used):
                return point

    def _find_chain(self, start_point, other, result, used):
        i = self.get_index_by_point[start_point]
        while self.epoints[i] not in other:
            if self.epoints[i] in used:
                return None
            result[-1].append(self.epoints[i])
            used.add(self.epoints[i])
            i = (i + 1) % len(self.epoints)
        result[-1].append(self.epoints[i])
        used.add(self.epoints[i])
        i = other.get_index_by_point[self.epoints[i]]
        i -= 1
        while other.epoints[i] in self:
            result[-1].append(other.epoints[i])
            # used.add(other.epoints[i])
            i -= 1
        used.add(other.epoints[i + 1])
        index = self.get_index_by_point[other.epoints[i + 1]]
        return self.epoints[(index + 1) % len(self.epoints)]

    def _find_cycle(self, other, used, result):
        result.append([])
        start_point = self._find_start_point(other, used)
        while start_point is not None:
            start_point = self._find_chain(start_point, other, result, used)
        if not result[-1]:
            result.pop(-1)
            return False
        else:
            return True

    def __sub__(self, other):
        self.extend_points(other)
        other.extend_points(self)
        if all(map(lambda p: p in other, self.points)):
            return []
        if all(map(lambda p: p in self, other.points)):
            return [self, other]
        result = []
        used = set()
        while self._find_cycle(other, used, result):
            pass
        return list(map(Polygon, result))
