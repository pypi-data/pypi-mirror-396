"""
LEBSTA Units Library
====================

A Python library for unit definitions and conversions in engineering applications.

Usage:
    import lebsta_units as units
    
    force = 100 * units.kN
    pressure = 25 * units.MPa
"""

__version__ = "1.1.2"
__author__ = "LEBSTA"

# Unidades base (SI)
m = 1.0
kg = 1.0
s = 1.0

# Constantes (standard gravity)
g = 9.80665 * m / s**2  # NIST: standard acceleration of free fall (g_n)

# Masa
ton = 1000.0 * kg  # tonelada métrica

# Longitud
cm = 0.01 * m
mm = 0.001 * m
inch = 2.54 * cm          # 1 in = 0.0254 m
ft = 0.3048 * m           # 1 ft = 0.3048 m
km = 1000.0 * m

# Fuerza (SI)
N = kg * m / s**2
kN = 1000.0 * N

# Fuerza gravitacional métrica
kgf = kg * g              # 1 kgf = 9.80665 N (si g = g_n)
tonf = ton * g            # tonelada-fuerza métrica (tf)

# Sistema inglés (derivado)
lb = 0.45359237 * kg      # libra masa (definición exacta)
lbf = lb * g              # 1 lbf ≈ 4.448222 N
kip = 1000.0 * lbf        # 1 kip = 1000 lbf = 4.448222e3 N

# Presión
Pa = N / m**2
kPa = 1000.0 * Pa
MPa = 1e6 * Pa
psi = lbf / inch**2       # 1 psi = 6.894757e3 Pa
ksi = 1000.0 * psi        # 1 ksi = 6.894757e6 Pa

# Tiempo
min = 60.0 * s
hr = 60.0 * min

# Lista de todas las unidades disponibles para importación
__all__ = [
    # Unidades base
    'm', 'kg', 's',
    # Constantes
    'g',
    # Masa
    'ton',
    # Dimensión
    'cm', 'inch', 'mm', 'ft', 'km',
    # Fuerza
    'kgf', 'tonf', 'N', 'kN', 'kip',
    # Presión
    'Pa', 'kPa', 'MPa', 'psi', 'ksi',
    # Tiempo
    'min', 'hr',
]