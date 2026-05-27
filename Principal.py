from Classes.Nucleus.Graph import Graph
from Classes.Nucleus.RouteCam import Route
from Classes.Nucleus.AirportVertex import Airport
from Classes.RouteEngine.RoutePlanner import RoutePlanner

# =========================
# AIRCRAFTS
# =========================

class CommercialAirplane:
    def __init__(self):
        self.type = "Commercial"
        self.costPerKm = 0.35

class RegionalPlane:
    def __init__(self):
        self.type = "Regional"
        self.costPerKm = 0.22

class Propeller:
    def __init__(self):
        self.type = "Propeller"
        self.costPerKm = 0.12


commercial = CommercialAirplane()
regional = RegionalPlane()
propeller = Propeller()

# =========================
# AIRPORTS
# =========================

bog = Airport(
    "BOG",
    "El Dorado",
    "Bogota",
    "Colombia",
    True,
    120,
    40,
    [],
    []
)

mde = Airport(
    "MDE",
    "Jose Maria Cordova",
    "Medellin",
    "Colombia",
    False,
    90,
    35,
    [],
    []
)

clo = Airport(
    "CLO",
    "Alfonso Bonilla",
    "Cali",
    "Colombia",
    False,
    80,
    30,
    [],
    []
)

lim = Airport(
    "LIM",
    "Jorge Chavez",
    "Lima",
    "Peru",
    True,
    100,
    40,
    [],
    []
)

mia = Airport(
    "MIA",
    "Miami International",
    "Miami",
    "USA",
    True,
    200,
    70,
    [],
    []
)

mad = Airport(
    "MAD",
    "Barajas",
    "Madrid",
    "Spain",
    True,
    220,
    75,
    [],
    []
)

# =========================
# GRAPH
# =========================

graph = Graph()

graph.airports.extend([
    bog,
    mde,
    clo,
    lim,
    mia,
    mad
])

# =========================
# ROUTES
# =========================

r1 = Route(
    bog,
    mde,
    1,
    commercial,
    250,
    80,
    1
)

r2 = Route(
    mde,
    lim,
    3,
    regional,
    1800,
    150,
    1
)

r3 = Route(
    bog,
    clo,
    1,
    propeller,
    300,
    50,
    1
)

r4 = Route(
    clo,
    lim,
    4,
    propeller,
    2200,
    100,
    1
)

r5 = Route(
    lim,
    mia,
    5,
    commercial,
    4200,
    300,
    1
)

r6 = Route(
    bog,
    mia,
    6,
    commercial,
    3900,
    500,
    1
)

r7 = Route(
    mia,
    mad,
    9,
    commercial,
    7100,
    900,
    1
)

r8 = Route(
    lim,
    mad,
    11,
    regional,
    9500,
    700,
    1
)

# =========================
# BLOCK ONE ROUTE
# =========================

r6.isBlocked = True

# =========================
# ADJACENCIES
# =========================

bog.insertAdjacencies(r1)
bog.insertAdjacencies(r3)
bog.insertAdjacencies(r6)

mde.insertAdjacencies(r2)

clo.insertAdjacencies(r4)

lim.insertAdjacencies(r5)
lim.insertAdjacencies(r8)

mia.insertAdjacencies(r7)

# =========================
# PLANNER
# =========================

planner = RoutePlanner()

# =========================
# TEST 1 - DISTANCE
# =========================

print("\nTEST DISTANCE\n")

result = planner.calculateRoute(
    graph,
    bog,
    mad,
    "distance"
)

print(result)

# =========================
# TEST 2 - COST
# =========================

print("\nTEST COST\n")

result = planner.calculateRoute(
    graph,
    bog,
    mad,
    "cost"
)

print(result)

# =========================
# TEST 3 - TIME
# =========================

print("\nTEST TIME\n")

result = planner.calculateRoute(
    graph,
    bog,
    mad,
    "time"
)

print(result)

# =========================
# TEST 4 - ONLY COMMERCIAL
# =========================

print("\nTEST ONLY COMMERCIAL\n")

result = planner.calculateRoute(
    graph,
    bog,
    mad,
    "cost",
    ["Commercial"]
)

print(result)

# =========================
# TEST 5 - EXCLUDE HUBS
# =========================

print("\nTEST EXCLUDE HUBS\n")

result = planner.calculateRoute(
    graph,
    bog,
    mad,
    "cost",
    None,
    True
)

print(result)

# =========================
# TEST 6 - BLOCKED ROUTE
# =========================

print("\nTEST BLOCKED ROUTE\n")

result = planner.calculateRoute(
    graph,
    bog,
    mia,
    "distance"
)

print(result)