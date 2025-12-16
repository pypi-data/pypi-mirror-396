import unittest, os
import pandas as pd
from unittest.mock import patch

from Pokemon.funciones import (
    get_grupos_pokemon,
    get_altura_media_grupo,
    get_peso_medio_grupo,
    generar_csv_pokemon_stats,
)

class TestFuncionesPokemon(unittest.TestCase):

    def setUp(self):
        # Solo parcheamos os.path.exists en el módulo Pokemon.funciones
        self.patcher_exists = patch("Pokemon.funciones.os.path.exists", return_value=True)
        self.mock_exists = self.patcher_exists.start()

        # DataFrame simulado para tests de consulta
        self.df_fake = pd.DataFrame({
            "Nombre Grupo": ["monster", "bug"],
            "Altura Media": [15.5, 5.2],
            "Peso Medio": [500.0, 20.0],
        })

        self.csv = "falso.csv"

    def tearDown(self):
        self.patcher_exists.stop()

    @patch("Pokemon.funciones.pd.read_csv")
    def test_get_grupos_pokemon(self, mock_read):
        mock_read.return_value = self.df_fake

        grupos = get_grupos_pokemon(self.csv)

        self.assertEqual(len(grupos), 2)
        self.assertIn("monster", grupos)

        print("✔ test_get_grupos_pokemon OK")

    @patch("Pokemon.funciones.pd.read_csv")
    def test_get_altura_media_grupo(self, mock_read):
        mock_read.return_value = self.df_fake

        altura = get_altura_media_grupo("monster", self.csv)
        self.assertEqual(altura, 15.5)

        altura_fake = get_altura_media_grupo("dragon", self.csv)
        self.assertIsNone(altura_fake)

        print("✔ test_get_altura_media_grupo OK")

    @patch("Pokemon.funciones.pd.read_csv")
    def test_get_peso_medio_grupo(self, mock_read):
        mock_read.return_value = self.df_fake

        peso = get_peso_medio_grupo("bug", self.csv)
        self.assertEqual(peso, 20.0)

        print("✔ test_get_peso_medio_grupo OK")

    @patch("Pokemon.funciones._download_pokemons")
    def test_generar_csv_pokemon_stats(self, mock_download):
        # Simulamos datos devueltos por la API
        mock_download.return_value = [
            {
                "id": 1,
                "name": "poke1",
                "base_experience": 100,
                "height": 10,
                "weight": 100,
                "egg_groups": ["monster"],
            },
            {
                "id": 2,
                "name": "poke2",
                "base_experience": 200,
                "height": 20,
                "weight": 300,
                "egg_groups": ["monster", "bug"],
            },
        ]

        csv_temp = "pokemon_stats_test.csv"

        # Aquí NO borramos nada para no romper el test.
        ruta = generar_csv_pokemon_stats(csv_path=csv_temp, limit=999)

        # El fichero debería existir
        self.assertTrue(os.path.exists(ruta))

        # Leemos el CSV generado con pandas REAL
        df = pd.read_csv(csv_temp)

        # Columnas correctas
        self.assertListEqual(
            list(df.columns),
            ["Nombre Grupo", "Altura Media", "Peso Medio"],
        )

        # Medias:
        # monster → (10 + 20) / 2 = 15 ; (100 + 300) / 2 = 200
        fila_monster = df[df["Nombre Grupo"] == "monster"].iloc[0]
        self.assertEqual(fila_monster["Altura Media"], 15)
        self.assertEqual(fila_monster["Peso Medio"], 200)

        # bug → solo segundo pokémon
        fila_bug = df[df["Nombre Grupo"] == "bug"].iloc[0]
        self.assertEqual(fila_bug["Altura Media"], 20)
        self.assertEqual(fila_bug["Peso Medio"], 300)

        print("✔ test_generar_csv_pokemon_stats OK")

        # Limpieza FINAL — borramos el archivo si existe
        if os.path.exists(csv_temp):
            os.remove(csv_temp)

if __name__ == "__main__":
    unittest.main()
