#!/usr/bin/env python3
import re  # https://regex101.com/

from sqlglot import parse_one, exp
from sqlglot.expressions import From, Where, Group, Having, Limit, Offset, Order, Select, Join, Subquery, Table

from querycraft.Database import *
from querycraft.SQLException import *
from querycraft.tools import bold_substring, delEntete, group_table_as_rows, compare_query_results_raw


# ======================================================================================================================
# ======================================================================================================================


# ======================================================================================================================
# ======================================================================================================================

class SQL(object):
    def __init__(self, db=None, dbtype=None, str=None, name=None, debug=False, verbose=False, step_by_step=True):
        self.debug = debug
        self.verbose = verbose
        self.step_by_step = step_by_step
        self.group_by = None
        if db is not None:
            self.__db = Database.get(db, dbtype, debug, verbose)
        else:
            self.__db = None
        self.select = None
        self.distinct = None
        self.from_all = None
        self.from_join = None
        self.where = None
        self.group = None
        self.having = None
        self.order = None
        self.limit = None
        self.offset = None
        self.sqlTables = []
        if str is not None:
            if name is not None:
                self.name = name
            else:
                self.name = str
            self.setSQL(str)  # Exécution de la requête
        else:
            self.name = name
            self.__str = None
            self.__data = None
            self.__col_names = None

    def setDebug(self):
        self.debug = True

    def unsetDebug(self):
        self.debug = False

    def setVerbose(self):
        self.verbose = True

    def unsetVerbose(self):
        self.verbose = False

    def setSQLTables(self, sqltbl):
        """
        Permet de positionner les tables et les alias d'une requête, sans l'analyser.
        :param sqltbl: La liste des tables et alias de la requête.
        :return:
        """
        self.sqlTables = sqltbl

    def printDBTables(self):
        self.__db.printDBTables()

    def load(self, file):
        """
        Charge une requête SQL depuis le fichier.
        :param file: Le fichier contenant la requête SQL.
        """
        if not existFile(file):
            raise SQLException("Le fichier n'existe pas.")
        else:
            txt = ""
            with open(file, 'r') as f:
                txt += f.read()
            self.setSQL(txt)

    def setSQL(self, req):
        self.__str = re.sub('\s+', ' ', req)
        if self.name is None: self.name = req
        self.execute()

    def similaire(self, sql2) -> int:
        # return df_similaire(self.getPLTable(), sql2.getPLTable())
        (hd1, rw1) = self.getTable()
        (hd2, rw2) = sql2.getTable()
        return compare_query_results_raw(hd1, rw1, hd2, rw2)

    def __str__(self) -> str:
        if self.__str is not None:
            return self.__str
        else:
            return 'Requête SQL absente.'

    def traite_doublons(self, description):
        # détection des colonnes avec même nom. Si c'est le cas, préfixage par nom de table.
        for (i, c) in enumerate(self.__col_names):
            # print(c)
            unique = True
            for j in range(i + 1, len(self.__col_names)):
                a = description[j].name
                if a == c:
                    id = description[j].table_oid
                    t = self.__db.dbPGID[id]
                    self.__col_names[j] = f"{self.getAlias(t)}.{c}"
                    unique = False
            if not unique:
                id = description[i].table_oid
                t = self.__db.dbPGID[id]
                self.__col_names[i] = f"{self.getAlias(t)}.{c}"

    def getAlias(self, t):
        """
        Retourne l'alias de la table t.
        :param t: La table.
        :return: L'alias de la table.
        """
        for alias in self.sqlTables:
            if alias[0] == t:
                if alias[1] is not None:
                    return alias[1]
                else:
                    return t
        return t

    def __addPrefix(self, att):
        if '.' not in att:
            if att in self.__db.dbAttributs:
                # if x in [y for (y, z) in self.sqlTables]
                lt = [x for x in self.__db.dbAttributs[att]]
                if lt:
                    return self.getAlias(lt[0]) + '.' + att
                else:
                    return att
            else:
                return att
        else:
            return att

    def pgsql_nommer(self, att):
        return att.name
        """
        if att.table_oid:
            t = self.__db.dbPGID[att.table_oid]
            nom_att = f"{self.getAlias(t)}.{att.name}"
        else:
            nom_att = self.__addPrefix(att.name)
        return nom_att"""

    def __sqlNameColumnVerif(self, description):
        """
        Vérifie si le nom des colonnes de la requête sont bien
        cohérents. Sinon renomme les colonnes avec le bon nom.
        """
        keywords = ['select', 'Select', '*', 'from', 'From', 'join', 'on', 'having', 'where', 'using', 'limit', 'order',
                    'group', 'by', 'count', 'offset', ';', '=', 'Tab', 'Sel', 'TaJ', 'Sub', '--']

        req = self.__str.replace(';', '')
        req = req.replace('(', ' ')
        req = req.replace('.', ' ')
        req = req.replace(',', ' ')
        req = req.replace(')', ' ')
        # On épure la requête pour contenir uniquement les mots non-clés SQL (a voir avec prof car pas obligatoire mais + rapide)
        req = list(set(req.split()) - set(keywords))

        # 1) On récupère les tables liées à l'attribut de chaque colonne.
        for j, i in enumerate(description):
            if i[0] in self.__db.dbAttributs:
                lt = [x.lower() for x in self.__db.dbAttributs[i[0]]]
                lt_original = [x for x in self.__db.dbAttributs[i[0]]]

                # 2) On regarde pour chaque table liée à l'attribut lesquelles sont mentionnées dans la requête.
                in_common = list(set([x.lower() for x in req]) & set(lt))
                in_common_original = [x for x in lt_original if x.lower() in in_common]

                # 3) Si le nom d'origine dans la colonne de la table est bien mentionné, on laisse, sinon on le remplace par le nom de la première table qui mentionne l'attribut.
                if self.__col_names[j].split('.')[0].lower() not in in_common:
                    self.__col_names[j] = in_common_original[0] + '.' + i[0]

    def __sqlJoinOnVerif(self):
        """
        Vérifie si la requête avec jointure possède bien un ON
        :return: False si JOIN mais manque un ON, True sinon
        """
        result = True
        natural = False
        for i in self.__str.split():
            if (i.lower() == "join" and not natural):
                result = False
            elif (i.lower() == "natural"):
                natural = True
            elif (not result and i.lower().startswith("on")):
                result = True
            elif (not result and i.lower().startswith("using")):
                result = True
        return result

    def execute(self):
        """
        Exécute la requête
        :return:
        """
        if self.__str is None:
            raise SQLException("La requête n'est pas renseignée.")
        elif self.__db is None:
            raise SQLException("La base de donnée n'est pas renseignée.")
        elif self.__str == "":
            raise SQLException("La requête est vide.")
        elif not self.__sqlJoinOnVerif():  # JOIN sans ON réalise un produit cartésien, pas une jointure interne.
            raise SQLException("Requête SQL invalide : JOIN sans ON détecté.")
        else:
            if self.debug: print('Exécution de la requête : ', self.__str)
            (description, self.__data) = self.__db.execute(self.__str)
            if self.__db.getType() == 'pgsql':
                self.__col_names = [self.pgsql_nommer(att) for att in description]
                # Vérification du nom des colonnes.
                self.__sqlNameColumnVerif(description)
            else:  # MySQL ou SQLite où on ne peut pas identifier les tables de tuples !
                self.__col_names = [self.__addPrefix(des[0]) for des in description]
                # print(self.__col_names)
                for (i, t) in enumerate(self.__data):
                    self.__data[i] = list(t)
                    # Vérification du nom des colonnes.
                    self.__sqlNameColumnVerif(description)
                ## détection des colonnes avec même nom. Si c'est le cas, suppression de la colonne en double.
                toDelete = list()
                for (i, c) in enumerate(self.__col_names):
                    unique = True
                    for j in range(i + 1, len(self.__col_names)):
                        a = self.__col_names[j]
                        if (a == c) and (self.__colonnes_egales(i, j)):
                            toDelete.append((c, j))
                            unique = False
                if self.debug and len(toDelete) > 0:
                    print(f"Colonnes dupliquées : {toDelete}")

                toDelete.reverse()
                for (c, i) in toDelete:
                    del self.__col_names[i]
                    for j in self.__data:
                        del j[i]

    def __colonnes_egales(self, a, b):
        """
        Détermine si la colonne a est égale à la colonne b dans self.__data
        :param a: colonne a
        :param b: colonne b
        :return: bool
        """
        egale = False
        for i in self.__data:
            egale = egale or i[a] == i[b]
        return egale

    def getTable(self):
        return self.__col_names, self.__data

    def stringToQuery(self):
        # print(self.__str)
        stmt = parse_one(self.__str)
        # print(stmt)
        # pprint(stmt)

        self.select = stmt.expressions
        # print(', '.join([str(x) for x in self.select]))
        self.distinct = stmt.args["distinct"] is not None

        self.sqlTables = list()
        self.from_all = [stmt.find(From)]
        for t in self.from_all[0].find_all(exp.Table):
            if t.alias:
                self.sqlTables.append((t.this.this, str(t.alias)))
            else:
                self.sqlTables.append((t.this.this, None))
        self.from_join = None
        if 'joins' in stmt.args:
            joins = stmt.args["joins"]
            self.from_all.append(joins)
            for j in joins:
                for t in j.find_all(exp.Table):
                    if t.alias:
                        self.sqlTables.append((t.this.this, str(t.alias)))
                    else:
                        self.sqlTables.append((t.this.this, None))
            self.from_join = str(self.from_all[0]) + ' ' + ' '.join([str(j) for j in joins])
        else:
            self.from_join = str(self.from_all[0])

        self.where = stmt.find(Where)

        self.group_by = stmt.find(Group)
        if self.group_by:
            self.group = [str(x) for x in self.group_by]
        else:
            self.group = None

        self.having = stmt.find(Having)

        self.order = stmt.find(Order)
        self.limit = stmt.find(Limit)
        self.offset = stmt.find(Offset)

        if self.debug: print(self.sqlTables)
        return stmt

    def __parcoursFrom(self, smt, deep=0):
        """
        Prends la requête principale et renvoie une liste de sous-requêtes didactiques
        :param smt: La requête principale sous forme de string.
        :return: La liste des requêtes didactiques et alias de la requête.
        """
        if isinstance(smt, Select):
            if self.debug: print('\t' * deep, f"--> Select : {smt}")
            l = []
            l += self.__parcoursFrom(smt.args['from'], deep + 1)
            if "joins" in smt.args:
                joins = smt.args["joins"]
                req = f"Select * {smt.args['from']}"
                for j in joins:
                    l += self.__parcoursFrom(j, deep + 1)
                    req += f' {j}'
                    l += [f'{req} ; --(Sel)']
            if self.debug: print('\t' * deep, f"<-- Select...{l}")
            return l
        elif isinstance(smt, From):  # ok
            if self.debug: print('\t' * deep, f"--> From : {smt}")
            l = self.__parcoursFrom(smt.this, deep + 1)
            if self.debug: print('\t' * deep, f"<-- From...{l}")
            return l
        elif isinstance(smt, Table):  # ok
            if self.debug: print('\t' * deep, f"--> Table : {smt.this}")
            l = [f'Select * From {smt.this} ; --(Tab)']
            rep = f'Select * From {smt.this}'
            if "joins" in smt.args:
                joins = smt.args["joins"]
                for j in joins:
                    l += self.__parcoursFrom(j, deep + 1)
                    rep += f' {j}'
                    l += [f'{rep} ; --(TaJ)']
            if self.debug: print('\t' * deep, f"<-- Table...{l}")
            return l
        elif isinstance(smt, Join):  # ok
            if self.debug: print('\t' * deep, f"--> Join : {smt}")
            l = self.__parcoursFrom(smt.this, deep + 1)
            if self.debug: print('\t' * deep, f"<-- Join...{l}")
            return l
        elif isinstance(smt, Subquery):
            if self.debug: print('\t' * deep, f"--> Subquery : {smt.this}")
            l = self.__parcoursFrom(smt.this, deep + 1)
            rep = f'Select * From ({smt.this})'
            if "joins" in smt.args:
                joins = smt.args["joins"]
                for j in joins:
                    l += self.__parcoursFrom(j, deep + 1)
                    rep += f' {j}'
                    l += [f'{rep} ; --(Sub)']
            if self.debug: print('\t' * deep, f"<-- Subquery...{l}")
            return l
        else:
            if self.debug: print(f"==> Unknown Smt {type(smt)} : {smt} ")

    def sbs_sql(self):
        """
        Créer les différentes requêtes SQL (qui s'éxécutent directement) et 
        les renvoie dans une liste.
        :return: La liste de toutes les requêtes SQL.
        """
        smt = self.stringToQuery()
        sql_lst = []

        if self.distinct:
            cls_distinct = ' Distinct '
        else:
            cls_distinct = ''
        cls_select_bis = ''
        if self.select is not None:
            cls_select = ', '.join([str(x) for x in self.select])
        else:
            cls_select = ''

        cls_from = ' ' + self.from_join

        # pprint(self.from_join)
        cls_joins = self.from_all  # self.__buildJoins(self.from_join)
        # pprint(cls_joins)

        if self.where is not None:
            cls_where = ' ' + str(self.where)
        else:
            cls_where = ''

        if self.group is not None:
            att_list = []
            for (t, a) in self.sqlTables:
                (id_t, des) = self.__db.dbTables[t.lower()]
                for att in des:
                    att_list.append(f"{self.getAlias(t).lower()}.{att[0]}")
            cls_select_bis = ','.join(att_list)

            lgp = []
            for x in self.group:
                if '.' not in x:
                    for (t, a) in self.sqlTables:
                        (id_t, l) = self.__db.dbTables[t.lower()]
                        for y in l:
                            if x == y[0]:
                                lgp.append(self.getAlias(t).lower() + '.' + x)
                else:
                    lgp.append(x)

            txt_group = ', '.join(lgp)
            cls_group_by = ' Group By ' + txt_group
            cls_group_by_bis = ' Order By ' + txt_group
            cls_group_by_ter = ' Order By ' + ', '.join(self.group)
        else:
            cls_group_by = ''
            cls_group_by_bis = ''
            txt_group = ''
        if self.having is not None:
            cls_having = ' ' + str(self.having)
            if cls_where == '':
                cls_where_tmp = ' Where (' + txt_group + ') in (select ' + txt_group + cls_from + cls_where + cls_group_by + cls_having + ')'
            else:
                cls_where_tmp = cls_where + ' and (' + txt_group + ') in (select ' + txt_group + cls_from + cls_where + cls_group_by + cls_having + ')'
        else:
            cls_having = ''
            cls_where_tmp = cls_where
        if self.order is not None:
            cls_order_by = ' ' + str(self.order)
        else:
            cls_order_by = ''
        if self.limit is not None:
            cls_limit = ' ' + str(self.limit)
        else:
            cls_limit = ''
        if self.offset is not None:
            cls_offset = ' ' + str(self.offset)
        else:
            cls_offset = ''

        sql_str = 'select ' + cls_distinct + cls_select + cls_from + cls_where + cls_group_by + cls_having + cls_order_by + cls_limit + cls_offset + ' ;'

        # Affichage des tables sources
        # et construction du FROM

        if self.debug: print('Gestion du From :')
        lfrom = self.__parcoursFrom(smt)
        for s in lfrom:
            sql_lst.append(SQL(db=self.__db.getDBCon(), dbtype=self.__db.getType(),
                               str=s,
                               name='§1-FROM§ ' + bold_substring(sql_str, s[14:-10]), debug=self.debug,
                               verbose=self.verbose, step_by_step=self.step_by_step))

        # WHERE
        if self.where is not None:
            loc_str = 'select * ' + cls_from + cls_where + ' ;'
            if self.debug: print('Gestion du Where :', loc_str)
            s = SQL(db=self.__db.getDBCon(), dbtype=self.__db.getType(), str=loc_str,
                    name='§2-WHERE§ ' + bold_substring(sql_str, cls_from + cls_where), debug=self.debug,
                    verbose=self.verbose, step_by_step=self.step_by_step)
            s.setSQLTables(self.sqlTables)
            sql_lst.append(s)

        # GROUP BY (1)
        if self.group is not None:
            loc_str = 'select  ' + cls_select_bis + cls_from + cls_where + cls_group_by_bis + ' ;'
            if self.debug: print('Gestion du Group By (1) : ', loc_str)
            s = SQL(db=self.__db.getDBCon(), dbtype=self.__db.getType(),
                    str=loc_str,
                    name='§3-GROUP BY ' + txt_group + '§ ' + bold_substring(sql_str,
                                                                            cls_from + cls_where + cls_group_by),
                    debug=self.debug, verbose=self.verbose, step_by_step=self.step_by_step)
            s.setSQLTables(self.sqlTables)
            sql_lst.append(s)

        # HAVING
        if self.having is not None:
            loc_str = 'select  ' + cls_select_bis + cls_from + cls_where_tmp + cls_group_by_bis + ' ;'
            if self.debug: print('Gestion du Having : ', loc_str)
            s = SQL(db=self.__db.getDBCon(), dbtype=self.__db.getType(),
                    str=loc_str,
                    name='§4-GROUP BY ' + txt_group + ' HAVING§ ' + bold_substring(sql_str,
                                                                                   cls_from + cls_where + cls_group_by + cls_having),
                    debug=self.debug, verbose=self.verbose, step_by_step=self.step_by_step)
            s.setSQLTables(self.sqlTables)
            sql_lst.append(s)

        #  GROUP BY (2) (avec ou sans HAVING)
        # if self.group is not None:
        #    sql_lst.append(SQL(db=self.__db, dbtype=self.__dbtype, str='select * ' + cls_from + cls_where + cls_group_by + cls_having + ' ;',
        #                       name='<3-GROUP BY ' + txt_group + ' HAVING> ' + bold_substring(sql_str,
        #                                                                                       cls_from + cls_where + cls_group_by + cls_having)))

        # SELECT
        loc_str = 'select ' + cls_select + cls_from + cls_where + cls_group_by + cls_having + ' ;'
        if self.debug: print('Gestion du Select : ', loc_str)
        s = SQL(db=self.__db.getDBCon(), dbtype=self.__db.getType(),
                str=loc_str,
                name='§5-SELECT§ ' + bold_substring(sql_str,
                                                    cls_select + cls_from + cls_where + cls_group_by + cls_having),
                debug=self.debug, verbose=self.verbose, step_by_step=self.step_by_step)
        s.setSQLTables(self.sqlTables)
        sql_lst.append(s)

        # DISTINCT
        if self.distinct:
            loc_str = 'select ' + cls_distinct + cls_select + cls_from + cls_where + cls_group_by + cls_having + ' ;'
            if self.debug: print('Gestion du Distinct : ', loc_str)
            s = SQL(db=self.__db.getDBCon(), dbtype=self.__db.getType(),
                    str=loc_str,
                    name='§6-DISTINCT§ ' + bold_substring(sql_str,
                                                          cls_distinct + cls_select + cls_from + cls_where + cls_group_by + cls_having),
                    debug=self.debug, verbose=self.verbose, step_by_step=self.step_by_step)
            s.setSQLTables(self.sqlTables)
            sql_lst.append(s)

        # ORDER BY
        if self.order is not None:
            loc_str = 'select ' + cls_distinct + cls_select + cls_from + cls_where + cls_group_by + cls_having + cls_order_by + ' ;'
            if self.debug: print('Gestion du Order By : ', loc_str)
            s = SQL(db=self.__db.getDBCon(), dbtype=self.__db.getType(),
                    str=loc_str,
                    name='§7-ORDER BY§ ' + bold_substring(sql_str,
                                                          cls_distinct + cls_select + cls_from + cls_where + cls_group_by + cls_having + cls_order_by),
                    debug=self.debug, verbose=self.verbose, step_by_step=self.step_by_step)
            s.setSQLTables(self.sqlTables)
            sql_lst.append(s)

        # LIMIT
        if self.limit is not None:
            loc_str = 'select ' + cls_distinct + cls_select + cls_from + cls_where + cls_group_by + cls_having + cls_order_by + cls_limit + ' ;'
            if self.debug: print('Gestion du Limit : ', loc_str)
            s = SQL(db=self.__db.getDBCon(), dbtype=self.__db.getType(),
                    str=loc_str,
                    name='§8-LIMIT§ ' + bold_substring(sql_str,
                                                       cls_distinct + cls_select + cls_from + cls_where + cls_group_by + cls_having + cls_order_by + cls_limit),
                    debug=self.debug, verbose=self.verbose, step_by_step=self.step_by_step)
            s.setSQLTables(self.sqlTables)
            sql_lst.append(s)

        # OFFSET
        if self.offset is not None:
            loc_str = 'select ' + cls_distinct + cls_select + cls_from + cls_where + cls_group_by + cls_having + cls_order_by + cls_limit + cls_offset + ' ;'
            if self.debug: print('Gestion du Offset : ', loc_str)
            s = SQL(db=self.__db.getDBCon(), dbtype=self.__db.getType(),
                    str=loc_str,
                    name='§9-OFFSET§ ' + bold_substring(sql_str,
                                                        cls_distinct + cls_select + cls_from + cls_where + cls_group_by + cls_having + cls_order_by + cls_limit + cls_offset),
                    debug=self.debug, verbose=self.verbose, step_by_step=self.step_by_step)
            s.setSQLTables(self.sqlTables)
            sql_lst.append(s)

        # pprint([x.__str__() for x in sql_lst])
        return sql_lst

    def __key(self, tbl):
        k = []
        for att, isKey, isKKey in tbl:
            if isKey: k.append(att)
        return k

    def __notkey(self, tbl):
        k = []
        for att, isKey, isKKey in tbl:
            if not isKey: k.append(att)
        return k

    def printTable(self, gb: list | None) -> None:
        """
        Affiche une table sur le terminal sous la forme d'un tableau.
        """
        if gb is not None:
            rows = group_table_as_rows(self.__col_names, self.__data, group_cols=gb)
            print(format_table_3(self.__col_names, rows, inter=True))  # , table_size=40))
            print("Nombre de tuples : " + str(len(self.__data)))
        else:
            print(format_table_2(self.__col_names, self.__data))
            print("Nombre de tuples : " + str(len(self.__data)))

    def coloring(self, s):
        count = 0
        result = []
        select_replaced = False
        words = s.split(" ")

        for i, word in enumerate(words):
            if word.lower() == "select" and not select_replaced:
                words[i] = f"\033[32m{word}\033[0m"
                select_replaced = True

        s = " ".join(words)

        for char in s:
            if char == "#":
                count += 1
                if count == 1:
                    result.append("\033[32m")
                elif count == 2:
                    result.append("\033[0m")
                else:
                    result.append(char)
            else:
                result.append(char)

        return ''.join(result)

    def table(self):
        if (self.__data is None or self.__col_names is None):
            if self.debug:
                print('---> No data or column names found. SQL query is executed')
            self.execute()
        print('==================================================================================================')
        if self.debug:
            print(self.name)
        else:
            print(self.coloring(delEntete(self.name, '§')))
        if self.debug: print(self.__str)
        step = re.search(r'\§(\d)\-(.+)\§\s(.*)$', self.name)
        if step[1] in ['1', '2']:  # From et Where
            self.printTable(gb=None)
        elif step[1] in ['3', '4']:  # Group-By et Having
            gp = re.search(r'GROUP BY\s+(.+?)(\sHAVING)?$', step[2])
            if self.__db.getType() == 'pgsql':
                lgp = []
                for att in gp[1].split(','):
                    if '.' in att:
                        tatt = att.split('.')
                        for (t, a) in self.sqlTables:
                            if a == tatt[0].strip().lower():
                                lgp.append(a + '.' + tatt[1].strip())
                            elif t.lower() == tatt[0].strip().lower():
                                lgp.append(att.strip().lower())
                    else:
                        for (t, a) in self.sqlTables:
                            (id_t, l) = self.__db.dbTables[t]
                            for x in l:
                                if x[0] == att.strip():
                                    if a is None:
                                        lgp.append(t + '.' + att.strip())
                                    else:
                                        lgp.append(a + '.' + att.strip())
                                    break
                if self.debug: print(lgp)
                self.printTable(gb=lgp)  # step == '3')
            else:
                lgp = [x.strip() for x in gp[1].split(',')]
                if self.debug: print(lgp)
                self.printTable(gb=lgp)  # step == '3')
        else:  # Select, Distinct, Order By, Limit, Offset
            self.printTable(gb=None)
        print('')

    def clear_line(self):
        # Windows
        if os.name == 'nt':
            os.system('cls')
        # Unix/Linux/MacOS
        else:
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K")

    def clear_terminal(self):
        # Windows
        if os.name == 'nt':
            os.system('cls')
        # Unix/Linux/MacOS
        else:
            os.system('clear')

    def sbs(self):
        alltabs = self.sbs_sql()
        print("\033[1mRésultat\033[0m")
        alltabs[len(alltabs) - 1].table()
        input("Appuyez sur Entrée pour voir le pas à pas ou Ctrl + Z pour quitter.")
        self.clear_terminal()

        for i, s in enumerate(alltabs):
            if (i < len(alltabs) - 1):
                print("\033[1mEtape N°" + str(i + 1) + "\033[0m")
            else:
                print("\033[1mEtape N°" + str(i + 1) + " (Résultat)\033[0m")
            s.table()
            if self.step_by_step and i < len(alltabs) - 1:
                input("Appuyez sur Entrée pour continuer ou Ctrl + Z pour quitter.")
                self.clear_line()


# TODO : Faire une fonction qui compare la syntaxe de deux requêtes


if __name__ == '__main__':
    #sql_txt = """SELECT distinct  m.codemat as no, titre, count(*)
#FROM matieres m left join notes n inner join etudiants using (noetu) on m.codemat = n.codemat
#where m.codemat in (select codemat from matieres where diplome = 'L2') and noteex > 5
#group by m.codemat, titre
#having count(*) >1 Order by titre Limit 10 Offset 2;"""
    # db = Database.get('../static/bdd/cours/cours.db', 'sqlite')
    # (dsc, data) = db.execute(sql_txt)
    # pprint(data)
    # pprint(dsc)
    # db = Database.get('dbname=cours', 'pgsql')
    # (dsc, data) = db.execute(sql_txt)
    # pprint(data)
    # pprint(dsc)
    # sql = SQL('../static/bdd/cours/cours.db', 'sqlite')
    # sql.setSQL(sql_txt)
    # sql.stringToQuery()
    db = Database.get(('dbname=cours'), 'pgsql', debug=False)
