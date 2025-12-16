A# h4u2 — Lista de cursos (proyecto de prueba en Python)

Proyecto **de ejemplo** para practicar cómo estructurar un paquete en Python que mantiene una lista de cursos (nombre, duración y link), permite **listarlos**, **buscarlos por nombre**, y calcular la **duración total**.

---

## Estructura del proyecto

```
.
├─ setup.py
├─ README.md
└─ h4u2/
   ├─ __init__.py
   ├─ courses.py
   └─ utils.py
```

---

## Requisitos

- Python 3.x
- pip

---

## Instalación

### Opción A: modo desarrollo (editable)

Desde la carpeta del proyecto:

```bash
python -m pip install -U pip
pip install -e .
```

### Opción B: instalación normal

```bash
pip install .
```

---

## Uso

### 1) Listar cursos

```python
from h4u2 import list_courses

list_courses()
```

### 2) Buscar un curso por nombre

```python
from h4u2 import search_course_by_name

course = search_course_by_name("Curso de Python")
print(course)
```

> Si no existe, devuelve `None`.

### 3) Duración total

```python
from h4u2.utils import total_duration

print(total_duration())
```

---

## Importar directo desde `h4u2`

Si tu `__init__.py` exporta los símbolos del paquete, también puedes:

```python
from h4u2 import list_courses, search_course_by_name, total_duration

list_courses()
print(search_course_by_name("Curso de JavaScript"))
print(total_duration())
```

---

## API (referencia rápida)

### `h4u2.courses`
- `Courses(name, duration, link)`
- `courses` (lista de cursos)
- `list_courses()`
- `search_course_by_name(name) -> Courses | None`

### `h4u2.utils`
- `total_duration() -> int`

---

## Personalizar cursos

Edita `h4u2/courses.py` y ajusta la lista:

```python
courses = [
    Courses("Curso nuevo", 5, "https://example.com/nuevo"),
]
```

---

## Notas

- Este repo es **solo un proyecto de prueba** para practicar empaquetado y organización de código.
- Si quieres convertirlo en CLI, puedes agregar un `entry_points` en `setup.py`.

---

## Licencia

Proyecto de prueba (sin licencia definida). Si quieres, cambia esto a MIT/Apache-2.0/etc.
