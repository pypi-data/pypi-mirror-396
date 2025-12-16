# LEBSTA Units

Una librería Python para definiciones de unidades y conversiones en aplicaciones de ingeniería.

## Instalación

### Instalación en modo desarrollo (recomendado para desarrollo local)

```bash
pip install -e .
```

### Instalación normal

```bash
pip install .
```

## Uso

### Importación básica

```python
import lebsta_units as units

# Usar las unidades
fuerza = 100 * units.kN
presion = 25 * units.MPa
longitud = 5 * units.m
```

### Importación selectiva

```python
from lebsta_units import kN, MPa, m, cm

fuerza = 100 * kN
presion = 25 * MPa
longitud = 5 * m
```

### Importación completa

```python
from lebsta_units import *

fuerza = 100 * kN
presion = 25 * MPa
```

## Unidades Disponibles

### Unidades Base
- `m` - Metro
- `kg` - Kilogramo
- `s` - Segundo

### Constantes Físicas
- `g` - Aceleración de la gravedad (9.80665 m/s²)

### Unidades de Masa
- `ton` - Tonelada (1000 kg)

### Unidades de Dimensión
- `cm` - Centímetro
- `mm` - Milímetro
- `inch` - Pulgada
- `ft` - Pie

### Unidades de Fuerza
- `N` - Newton
- `kN` - Kilonewton
- `kgf` - Kilogramo-fuerza
- `tonf` - Tonelada-fuerza
- `kip` - Kilo-libra fuerza

### Unidades de Presión
- `Pa` - Pascal
- `MPa` - Megapascal
- `psi` - Libras por pulgada cuadrada
- `ksi` - Kilo-libras por pulgada cuadrada

### Unidades derivadas adicionales
- `kPa` - Kilopascal

## Ejemplos

### Conversión de unidades

```python
import lebsta_units as units

# Convertir de kN a N
fuerza_kN = 50 * units.kN
fuerza_N = fuerza_kN / units.N
print(f"50 kN = {fuerza_N} N")  # 50 kN = 50000.0 N

# Convertir de MPa a psi
presion_MPa = 10 * units.MPa
presion_psi = presion_MPa / units.psi
print(f"10 MPa = {presion_psi:.2f} psi")  # 10 MPa = 1450.38 psi

# Convertir de metros a pies
longitud_m = 10 * units.m
longitud_ft = longitud_m / units.ft
print(f"10 m = {longitud_ft:.2f} ft")  # 10 m = 32.81 ft
```

### Cálculos con unidades

```python
import lebsta_units as units

# Cálculo de esfuerzo (σ = F/A)
fuerza = 100 * units.kN
area = 0.05 * units.m**2
esfuerzo = fuerza / area

# Convertir a MPa
esfuerzo_MPa = esfuerzo / units.MPa
print(f"Esfuerzo: {esfuerzo_MPa} MPa")
```

## Licencia

MIT License

## Versión

1.1.2
