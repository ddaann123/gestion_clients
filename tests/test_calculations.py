# tests/test_calculations.py
import unittest
from calculations.submission_calcs import calculer_quantite_sacs
from database.db_manager import DatabaseManager
from config import DB_PATH

class TestCalculations(unittest.TestCase):
    def setUp(self):
        self.db_manager = DatabaseManager(DB_PATH)

    def test_calcul_sacs_couverture(self):
        sacs, _, _, _, _ = calculer_quantite_sacs("1000", "MAXCRETE COMPLETE", "1-1/2\"", "1:1", self.db_manager)
        self.assertEqual(sacs, 30)  # 1000 * (1.5/1) / 50 = 30 sacs

if __name__ == "__main__":
    unittest.main()