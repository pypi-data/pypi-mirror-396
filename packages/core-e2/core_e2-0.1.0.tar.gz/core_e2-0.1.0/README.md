# Cursos disponibles

- Introduccion a linux [15 horas]
- Personalizacion de linux [3 horas]
- Introduccion al hacking [53 horas]

## Instalacion

Instalar el paquete usando `pip3`:

```python
pip3 install core_e2
```

## Uso basico

### Listar todo los cursos

```python
from core_e2 import list_courses

for course in list_courses():
  print(course)
```

### Obtener un curso por nombre

```python
from core_e2 import get_course_by_name

course = get_course_by_name("Introduccion a linux")
print(course)
```

### Calcular duracion total de cursos

```python
from core_e2..utils import total_duration

print(f"Duracion total: {total_duration()} horas")
```
