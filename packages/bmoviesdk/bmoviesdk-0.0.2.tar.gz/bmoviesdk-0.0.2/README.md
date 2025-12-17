# MovieLens SDK - `bmoviesdk`

Un SDK Python léger pour interagir avec l’API REST **MovieLens**.  
Conçu pour les **Data Analysts** et **Data Scientists**, il offre une intégration native avec :

- **Pydantic**  
- **Dictionnaires Python**  
- **DataFrames Pandas**

[![PyPI version](https://badge.fury.io/py/bmoviesdk.svg)](https://badge.fury.io/py/bmoviesdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---
## Table des matières
- [Installation](#installation)
- [Configuration](#configuration)
- [Tester le SDK](#tester-le-sdk)
- [Modes de sortie disponibles](#modes-de-sortie-disponibles)
- [Tester en local](#tester-en-local)
- [Compatibilité](#compatibilité)
- [Public cible](#public-cible)
- [Licence](#licence)
- [Liens utiles](#liens-utiles)

---
## Installation

```bash
pip install bmoviesdk
```

---

## Configuration

```python
from bmoviesdk import MovieClient, MovieConfig

# Configuration avec l’URL de votre API (Render ou locale)
config = MovieConfig(movie_base_url="https://fastapi-bp4l.onrender.com")
client = MovieClient(config=config)
```

---

## Tester le SDK

### 1. Health check

```python
client.health_check()
# Retourne : {"status": "ok"}
```

### 2. Récupérer un film

```python
movie = client.get_movie(1)
print(movie.title)
```

### 3. Liste de films au format DataFrame

```python
df = client.list_movies(limit=5, output_format="pandas")
print(df.head())
```

---

## Modes de sortie disponibles

Toutes les méthodes de liste (`list_movies`, `list_ratings`, etc.) peuvent retourner :

- des objets **Pydantic** (défaut)
- des **dictionnaires**
- des **DataFrames Pandas**

Exemple :

```python
client.list_movies(limit=10, output_format="dict")
client.list_ratings(limit=10, output_format="pandas")
```

---

## Tester en local

Vous pouvez aussi utiliser une API locale :

```python
config = MovieConfig(movie_base_url="http://localhost:8000")
client = MovieClient(config=config)
```

---
## Compatibilité

- Python 3.10+
- Fonctionne avec **Windows**, **macOS** et **Linux**

---

## Public cible

- Data Analysts
- Data Scientists
- Étudiants et curieux en Data
- Développeurs Python

---

## Licence

MIT License

---

## Liens utiles

- API Render : [https://fastapi-bp4l.onrender.com](https://fastapi-bp4l.onrender.com)
- PyPI : [https://pypi.org/project/bmoviesdk/](https://pypi.org/project/bmoviesdk)