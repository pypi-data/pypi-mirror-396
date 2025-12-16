# Librería Pokemon Stats — Proyecto Final (PJZD)

Librería sencilla para **generar y consultar estadísticas de Pokémon** agrupadas por sus *egg groups* utilizando datos reales obtenidos desde la **PokeAPI**.

Incluye funciones para:
- Descargar información de Pokémon y generar un CSV automáticamente.
- Consultar altura media y peso medio por grupo.
- Listar todos los grupos disponibles.

---
## Instalación
```bash
pip install Pokemon-PJZD==1.0.0
```
---
## Funcionalidades
### 1. get_grupos_pokemon(csv_path)

Devuelve una lista con todos los grupos de Pokémon disponibles en el fichero CSV.

### 2. get_altura_media_grupo(grupo, csv_path)

Devuelve la altura media del grupo indicado.
Si el grupo no existe, devuelve None.

### 3. get_peso_medio_grupo(grupo, csv_path)

Devuelve el peso medio del grupo indicado.
Si el grupo no existe, devuelve None.

### 4. generar_csv_pokemon_stats(csv_path="pokemon_stats.csv", limit=100)

Genera automáticamente un archivo CSV con estadísticas agrupadas por egg groups.

✔ Descarga datos reales desde la PokeAPI
✔ Ajusta el límite si se solicita más del máximo disponible
✔ Devuelve la ruta del CSV generado
---
##  Ejemplos de uso
### 1) Generar el CSV (descarga datos y calcula medias)
```python
from Pokemon import generar_csv_pokemon_stats

generar_csv_pokemon_stats(limit=150)
```
Esto creará un archivo pokemon_stats.csv con las estadísticas de 150 pokemons

### 2) Consultar los datos del CSV generado
```python
from Pokemon import (
    get_grupos_pokemon,
    get_altura_media_grupo,
    get_peso_medio_grupo,
)

csv = "pokemon_stats.csv"

print(get_grupos_pokemon(csv)) 
# ['monster', 'bug', 'water1', 'fairy', ...]

print(get_altura_media_grupo("monster", csv))
# 15.5

print(get_peso_medio_grupo("bug", csv))
# 20.0
```
---
## Licencia
### MIT License — Puedes usarlo libremente para proyectos educativos o personales.

---
## Autor

[Pedro Javier Zambudio Decillis](https://www.linkedin.com/in/pedro-zambudio/)