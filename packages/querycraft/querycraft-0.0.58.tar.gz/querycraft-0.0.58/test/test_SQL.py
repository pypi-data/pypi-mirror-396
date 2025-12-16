import unittest

import polars as pl

from querycraft.SQL import SQL
from querycraft.tools import compare_query_results_raw

class SQLTestCase(unittest.TestCase):
    def test_init(self):
        s = SQL()
        self.assertEqual(s.getDB(), None)
        self.assertEqual(s.dbTables, [])

    def test_db_1(self):
        s = SQL(db='../static/bdd/cours/cours.db')
        self.assertEqual(s.getDB(), '../static/bdd/cours/cours.db')
        self.assertEqual(s.dbTables, {
            'etudiants': [('noetu', True), ('nom', False), ('prenom', False)],
            'matieres': [('codemat', True), ('titre', False), ('responsable', False), ('diplome', False)],
            'notes': [('noe', True), ('codemat', True), ('noteex', False), ('notecc', False)]
        })

    def test_file2(self):
        s = SQL(db='../static/bdd/cours/cours.db')
        s.load('sql2.sql')
        self.assertEqual(s.name,
                         'SELECT titre, count(noteex) FROM matieres left join notes using (codemat) inner join etudiants on noetu = noetu group by codemat, titre having count(*) >1 ;')

    def test_sim(self):
        a1 = [[6, 9, 7], [1, 2, 4]]
        a2 = [[1, 2, 4], [6, 9, 7]]
        a3 = [[1, 4, 2], [6, 7, 9]]
        a4 = [[1, 2, 4], [6, 8, 7]]

        pr1 = pl.DataFrame(a1, schema=['a', 'b', 'c'], orient='row')
        pr2 = pl.DataFrame(a2, schema=['a', 'b', 'c'], orient='row')
        pr3 = pl.DataFrame(a3, schema=['a', 'c', 'b'], orient='row')
        pr4 = pl.DataFrame(a4, schema=['a', 'b', 'c'], orient='row')

        self.assertEqual(compare_query_results_raw(['a', 'b', 'c'],a1, ['a', 'b', 'c'],a1), 4)
        self.assertEqual(compare_query_results_raw(['a', 'b', 'c'],a1, ['a', 'b', 'c'],a2), 2)
        self.assertEqual(compare_query_results_raw(['a', 'b', 'c'],a2, ['a', 'c', 'b'],a3), 3)
        self.assertEqual(compare_query_results_raw(['a', 'c', 'b'],a3, ['a', 'b', 'c'],a1), 1)
        self.assertEqual(compare_query_results_raw(['a', 'c', 'c'],a3, ['a', 'b', 'c'],a4) , 0)

    def test_sim_SQL(self):
        sql1 = SQL(db='../static/bdd/cours/cours.db')
        sql1.load('sql1.sql')
        sql2 = SQL(db='../static/bdd/cours/cours.db')
        sql2.load('sql2.sql')
        sql2b = SQL(db='../static/bdd/cours/cours.db')
        sql2b.load('sql2b.sql')
        sql2c = SQL(db='../static/bdd/cours/cours.db')
        sql2c.load('sql2c.sql')

        self.assertEqual(sql1.similaire(sql2),0)
        self.assertEqual(sql1.similaire(sql1), 4)
        self.assertEqual(sql2.similaire(sql2), 4)
        self.assertEqual(sql2.similaire(sql2b), 2)
        self.assertEqual(sql2b.similaire(sql2c), 3)
        self.assertEqual(sql2.similaire(sql2c), 1)

if __name__ == '__main__':
    unittest.main()
