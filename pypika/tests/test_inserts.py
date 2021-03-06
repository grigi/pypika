# coding: utf-8
import unittest

from pypika import (
    Field as F,
    MySQLQuery,
    PostgreSQLQuery,
    Query,
    Table,
    Tables,
    functions as fn,
)
from pypika.functions import Avg
from pypika.terms import Values
from pypika.utils import QueryException

__author__ = "Timothy Heys"
__email__ = "theys@kayak.com"


class InsertIntoTests(unittest.TestCase):
    table_abc = Table('abc')

    def test_insert_one_column(self):
        query = Query.into(self.table_abc).insert(1)

        self.assertEqual('INSERT INTO "abc" VALUES (1)', str(query))

    def test_insert_one_column_single_element_array(self):
        query = Query.into(self.table_abc).insert((1,))

        self.assertEqual('INSERT INTO "abc" VALUES (1)', str(query))

    def test_insert_one_column_multi_element_array(self):
        query = Query.into(self.table_abc).insert((1,), (2,))

        self.assertEqual('INSERT INTO "abc" VALUES (1),(2)', str(query))

    def test_insert_single_row_with_array_value(self):
        query = Query.into(self.table_abc).insert(1, ['a', 'b', 'c'])

        self.assertEqual('INSERT INTO "abc" VALUES (1,[\'a\',\'b\',\'c\'])', str(query))

    def test_insert_multiple_rows_with_array_value(self):
        query = Query.into(self.table_abc).insert((1, ['a', 'b', 'c']),
                                                  (2, ['c', 'd', 'e']), )

        self.assertEqual('INSERT INTO "abc" '
                         'VALUES (1,[\'a\',\'b\',\'c\']),(2,[\'c\',\'d\',\'e\'])', str(query))

    def test_insert_all_columns(self):
        query = Query.into(self.table_abc).insert(1, 'a', True)

        self.assertEqual('INSERT INTO "abc" VALUES (1,\'a\',true)', str(query))

    def test_insert_all_columns_single_element(self):
        query = Query.into(self.table_abc).insert((1, 'a', True))

        self.assertEqual('INSERT INTO "abc" VALUES (1,\'a\',true)', str(query))

    def test_insert_all_columns_multi_rows(self):
        query = Query.into(self.table_abc).insert((1, 'a', True), (2, 'b', False))

        self.assertEqual('INSERT INTO "abc" VALUES (1,\'a\',true),(2,\'b\',false)', str(query))

    def test_insert_all_columns_multi_rows_chained(self):
        query = Query.into(self.table_abc).insert(1, 'a', True).insert(2, 'b', False)

        self.assertEqual('INSERT INTO "abc" VALUES (1,\'a\',true),(2,\'b\',false)', str(query))

    def test_insert_all_columns_multi_rows_chained_mixed(self):
        query = Query.into(self.table_abc).insert(
            (1, 'a', True), (2, 'b', False)
        ).insert(3, 'c', True)

        self.assertEqual('INSERT INTO "abc" VALUES '
                         '(1,\'a\',true),(2,\'b\',false),'
                         '(3,\'c\',true)', str(query))

    def test_insert_all_columns_multi_rows_chained_multiple_rows(self):
        query = Query.into(self.table_abc) \
            .insert((1, 'a', True),
                    (2, 'b', False)) \
            .insert((3, 'c', True),
                    (4, 'd', False))

        self.assertEqual('INSERT INTO "abc" VALUES '
                         '(1,\'a\',true),(2,\'b\',false),'
                         '(3,\'c\',true),(4,\'d\',false)', str(query))

    def test_insert_selected_columns(self):
        query = Query.into(self.table_abc).columns(
            self.table_abc.foo, self.table_abc.bar, self.table_abc.buz
        ).insert(1, 'a', True)

        self.assertEqual('INSERT INTO "abc" ("foo","bar","buz") VALUES (1,\'a\',true)', str(query))

    def test_insert_none_skipped(self):
        query = Query.into(self.table_abc).insert()

        self.assertEqual('', str(query))

    def test_insert_ignore(self):
        query = Query.into(self.table_abc).insert(1).ignore()

        self.assertEqual('INSERT IGNORE INTO "abc" VALUES (1)', str(query))

    def test_insert_null(self):
        query = Query.into(self.table_abc).insert(None)

        self.assertEqual('INSERT INTO "abc" VALUES (NULL)', str(query))


class PostgresInsertIntoReturningTests(unittest.TestCase):
    table_abc = Table('abc')

    def test_insert_returning_one_field(self):
        query = PostgreSQLQuery.into(self.table_abc).insert(1).returning(self.table_abc.id)

        self.assertEqual('INSERT INTO "abc" VALUES (1) RETURNING id', str(query))

    def test_insert_returning_one_field_str(self):
        query = PostgreSQLQuery.into(self.table_abc).insert(1).returning('id')

        self.assertEqual('INSERT INTO "abc" VALUES (1) RETURNING id', str(query))

    def test_insert_returning_all_fields(self):
        query = PostgreSQLQuery.into(self.table_abc).insert(1).returning(self.table_abc.star)

        self.assertEqual('INSERT INTO "abc" VALUES (1) RETURNING *', str(query))

    def test_insert_returning_all_fields_and_arithmetics(self):
        query = PostgreSQLQuery.into(self.table_abc).insert(1).returning(
            self.table_abc.star,
            self.table_abc.f1 + self.table_abc.f2
        )

        self.assertEqual('INSERT INTO "abc" VALUES (1) RETURNING *,f1+f2', str(query))

    def test_insert_all_columns_multi_rows_chained_returning_star(self):
        query = PostgreSQLQuery.into(
            self.table_abc
        ).insert(1, 'a', True).insert(2, 'b', False).returning(self.table_abc.star)

        self.assertEqual('INSERT INTO "abc" VALUES (1,\'a\',true),(2,\'b\',false) RETURNING *', str(query))

    def test_insert_all_columns_multi_rows_chained_returning_star_and_id(self):
        query = PostgreSQLQuery.into(
            self.table_abc
        ).insert(1, 'a', True).insert(2, 'b', False).returning(
            self.table_abc.name,
            self.table_abc.star,
            self.table_abc.id,
        )

        self.assertEqual('INSERT INTO "abc" VALUES (1,\'a\',true),(2,\'b\',false) RETURNING *', str(query))

    def test_insert_all_columns_multi_rows_chained_returning_star_str(self):
        query = PostgreSQLQuery.into(
            self.table_abc
        ).insert(1, 'a', True).insert(2, 'b', False).returning('*')

        self.assertEqual('INSERT INTO "abc" VALUES (1,\'a\',true),(2,\'b\',false) RETURNING *', str(query))

    def test_insert_all_columns_single_element_arrays(self):
        query = PostgreSQLQuery.into(self.table_abc).insert((1, 'a', True)).returning(self.table_abc.star)

        self.assertEqual('INSERT INTO "abc" VALUES (1,\'a\',true) RETURNING *', str(query))

    def test_insert_returning_null(self):
        query = PostgreSQLQuery.into(self.table_abc).insert(1).returning(None)

        self.assertEqual('INSERT INTO "abc" VALUES (1) RETURNING NULL', str(query))

    def test_insert_returning_tuple(self):
        query = PostgreSQLQuery.into(self.table_abc).insert(1).returning((1, 2, 3))

        self.assertEqual('INSERT INTO "abc" VALUES (1) RETURNING (1,2,3)', str(query))

    def test_insert_returning_arithmetics(self):
        query = PostgreSQLQuery.into(self.table_abc).insert(1).returning(self.table_abc.f1 + self.table_abc.f2)

        self.assertEqual('INSERT INTO "abc" VALUES (1) RETURNING f1+f2', str(query))

    def test_insert_returning_aggregate(self):
        with self.assertRaises(QueryException):
            PostgreSQLQuery.into(self.table_abc).insert(1).returning(Avg(self.table_abc.views))

    def test_insert_returning_from_other_table(self):
        table_cba = Table('cba')
        with self.assertRaises(QueryException):
            PostgreSQLQuery.into(self.table_abc).insert(1).returning(table_cba.id)


class InsertIntoOnDuplicateTests(unittest.TestCase):
    table_abc = Table('abc')

    def test_insert_one_column(self):
        query = MySQLQuery\
            .into(self.table_abc).insert(1)\
            .on_duplicate_key_update(self.table_abc.foo, self.table_abc.foo)
        self.assertEqual('INSERT INTO `abc` VALUES (1) ON DUPLICATE KEY UPDATE `foo`=`foo`', str(query))

    def test_insert_one_column_using_values(self):
        query = MySQLQuery\
            .into(self.table_abc).insert(1)\
            .on_duplicate_key_update(self.table_abc.foo, Values(self.table_abc.foo))
        self.assertEqual('INSERT INTO `abc` VALUES (1) ON DUPLICATE KEY UPDATE `foo`=VALUES(`foo`)', str(query))

    def test_insert_one_column_single_element_array(self):
        query = MySQLQuery\
            .into(self.table_abc).insert((1,))\
            .on_duplicate_key_update(self.table_abc.foo, self.table_abc.foo)

        self.assertEqual('INSERT INTO `abc` VALUES (1) ON DUPLICATE KEY UPDATE `foo`=`foo`', str(query))

    def test_insert_one_column_multi_element_array(self):
        query = MySQLQuery\
            .into(self.table_abc).insert((1,), (2,))\
            .on_duplicate_key_update(self.table_abc.foo, self.table_abc.foo)

        self.assertEqual('INSERT INTO `abc` VALUES (1),(2) ON DUPLICATE KEY UPDATE `foo`=`foo`', str(query))

    def test_insert_multiple_columns_on_duplicate_update_one_with_same_value(self):
        query = MySQLQuery\
            .into(self.table_abc).insert(1, 'a')\
            .on_duplicate_key_update(self.table_abc.bar, Values(self.table_abc.bar))

        self.assertEqual('INSERT INTO `abc` VALUES (1,\'a\') ON DUPLICATE KEY UPDATE `bar`=VALUES(`bar`)', str(query))

    def test_insert_multiple_columns_on_duplicate_update_one_with_different_value(self):
        query = MySQLQuery\
            .into(self.table_abc).insert(1, 'a') \
            .on_duplicate_key_update(self.table_abc.bar, 'b')

        self.assertEqual('INSERT INTO `abc` VALUES (1,\'a\') ON DUPLICATE KEY UPDATE `bar`=\'b\'', str(query))

    def test_insert_multiple_columns_on_duplicate_update_one_with_expression(self):
        query = MySQLQuery\
            .into(self.table_abc).insert(1, 2) \
            .on_duplicate_key_update(self.table_abc.bar, 4+F('bar'))  # todo sql expression? not python

        self.assertEqual('INSERT INTO `abc` VALUES (1,2) ON DUPLICATE KEY UPDATE `bar`=4+`bar`', str(query))

    def test_insert_multiple_columns_on_duplicate_update_one_with_expression_using_original_field_value(self):
        query = MySQLQuery\
            .into(self.table_abc).insert(1, 'a')\
            .on_duplicate_key_update(self.table_abc.bar, fn.Concat(self.table_abc.bar, 'update'))

        self.assertEqual(
            'INSERT INTO `abc` VALUES (1,\'a\') ON DUPLICATE KEY UPDATE `bar`=CONCAT(`bar`,\'update\')',
            str(query)
        )

    def test_insert_multiple_columns_on_duplicate_update_one_with_expression_using_values(self):
        query = MySQLQuery\
            .into(self.table_abc).insert(1, 'a')\
            .on_duplicate_key_update(self.table_abc.bar, fn.Concat(Values(self.table_abc.bar), 'update'))

        self.assertEqual(
            'INSERT INTO `abc` VALUES (1,\'a\') ON DUPLICATE KEY UPDATE `bar`=CONCAT(VALUES(`bar`),\'update\')',
            str(query)
        )

    def test_insert_multiple_columns_on_duplicate_update_multiple(self):
        query = MySQLQuery \
            .into(self.table_abc).insert(1, 'a', 'b') \
            .on_duplicate_key_update(self.table_abc.bar, 'b') \
            .on_duplicate_key_update(self.table_abc.baz, 'c')

        self.assertEqual(
            'INSERT INTO `abc` VALUES (1,\'a\',\'b\') ON DUPLICATE KEY UPDATE `bar`=\'b\',`baz`=\'c\'',
            str(query)
        )

    def test_insert_multi_rows_chained_mixed_on_duplicate_update_multiple(self):
        query = MySQLQuery.into(self.table_abc)\
            .insert((1, 'a', True), (2, 'b', False))\
            .insert(3, 'c', True)\
            .on_duplicate_key_update(self.table_abc.foo, self.table_abc.foo)\
            .on_duplicate_key_update(self.table_abc.bar, Values(self.table_abc.bar))

        self.assertEqual(
            'INSERT INTO `abc` VALUES (1,\'a\',true),(2,\'b\',false),(3,\'c\',true) '
            'ON DUPLICATE KEY UPDATE `foo`=`foo`,`bar`=VALUES(`bar`)',
            str(query)
        )

    def test_insert_selected_columns_on_duplicate_update_one(self):
        query = MySQLQuery.into(self.table_abc)\
            .columns(self.table_abc.foo, self.table_abc.bar, self.table_abc.baz)\
            .insert(1, 'a', True)\
            .on_duplicate_key_update(self.table_abc.baz, False)

        self.assertEqual(
            'INSERT INTO `abc` (`foo`,`bar`,`baz`) VALUES (1,\'a\',true) ON DUPLICATE KEY UPDATE `baz`=false',
            str(query)
        )

    def test_insert_selected_columns_on_duplicate_update_multiple(self):
        query = MySQLQuery.into(self.table_abc)\
            .columns(self.table_abc.foo, self.table_abc.bar, self.table_abc.baz)\
            .insert(1, 'a', True)\
            .on_duplicate_key_update(self.table_abc.baz, False)\
            .on_duplicate_key_update(self.table_abc.bar, Values(self.table_abc.bar))

        self.assertEqual(
            'INSERT INTO `abc` (`foo`,`bar`,`baz`) VALUES (1,\'a\',true) '
            'ON DUPLICATE KEY UPDATE `baz`=false,`bar`=VALUES(`bar`)',
            str(query)
        )

    def test_insert_none_skipped(self):
        query = MySQLQuery.into(self.table_abc).insert().on_duplicate_key_update(self.table_abc.baz, False)

        self.assertEqual('', str(query))

    def test_insert_ignore(self):
        query = MySQLQuery.into(self.table_abc).insert(1).ignore().on_duplicate_key_update(self.table_abc.baz, False)

        self.assertEqual('INSERT IGNORE INTO `abc` VALUES (1) ON DUPLICATE KEY UPDATE `baz`=false', str(query))


class InsertSelectFromTests(unittest.TestCase):
    table_abc, table_efg, table_hij = Tables('abc', 'efg', 'hij')

    def test_insert_star(self):
        query = Query.into(self.table_abc).from_(self.table_efg).select('*')

        self.assertEqual('INSERT INTO "abc" SELECT * FROM "efg"', str(query))

    def test_insert_ignore_star(self):
        query = Query.into(self.table_abc).from_(self.table_efg).select('*').ignore()

        self.assertEqual('INSERT IGNORE INTO "abc" SELECT * FROM "efg"', str(query))

    def test_insert_from_columns(self):
        query = Query.into(self.table_abc).from_(self.table_efg).select(
            self.table_efg.fiz, self.table_efg.buz, self.table_efg.baz
        )

        self.assertEqual('INSERT INTO "abc" '
                         'SELECT "fiz","buz","baz" FROM "efg"', str(query))

    def test_insert_columns_from_star(self):
        query = Query.into(self.table_abc).columns(
            self.table_abc.foo, self.table_abc.bar, self.table_abc.buz,
        ).from_(self.table_efg).select('*')

        self.assertEqual('INSERT INTO "abc" ("foo","bar","buz") '
                         'SELECT * FROM "efg"', str(query))

    def test_insert_columns_from_columns(self):
        query = Query.into(self.table_abc).columns(
            self.table_abc.foo, self.table_abc.bar, self.table_abc.buz
        ).from_(self.table_efg).select(
            self.table_efg.fiz, self.table_efg.buz, self.table_efg.baz
        )

        self.assertEqual('INSERT INTO "abc" ("foo","bar","buz") '
                         'SELECT "fiz","buz","baz" FROM "efg"', str(query))

    def test_insert_columns_from_columns_with_join(self):
        query = Query.into(self.table_abc).columns(
            self.table_abc.c1, self.table_abc.c2, self.table_abc.c3, self.table_abc.c4
        ).from_(self.table_efg).select(
            self.table_efg.foo, self.table_efg.bar
        ).join(self.table_hij).on(
            self.table_efg.id == self.table_hij.abc_id
        ).select(
            self.table_hij.fiz, self.table_hij.buz
        )

        self.assertEqual('INSERT INTO "abc" ("c1","c2","c3","c4") '
                         'SELECT "efg"."foo","efg"."bar","hij"."fiz","hij"."buz" FROM "efg" '
                         'JOIN "hij" ON "efg"."id"="hij"."abc_id"', str(query))


class SelectIntoTests(unittest.TestCase):
    table_abc, table_efg, table_hij = Tables('abc', 'efg', 'hij')

    def test_select_star_into(self):
        query = Query.from_(self.table_abc).select('*').into(self.table_efg)

        self.assertEqual('SELECT * INTO "efg" FROM "abc"', str(query))

    def test_select_columns_into(self):
        query = Query.from_(self.table_abc).select(
            self.table_abc.foo, self.table_abc.bar, self.table_abc.buz
        ).into(self.table_efg)

        self.assertEqual('SELECT "foo","bar","buz" INTO "efg" FROM "abc"', str(query))

    def test_select_columns_into_with_join(self):
        query = Query.from_(self.table_abc).select(
            self.table_abc.foo, self.table_abc.bar
        ).join(self.table_hij).on(
            self.table_abc.id == self.table_hij.abc_id
        ).select(
            self.table_hij.fiz, self.table_hij.buz
        ).into(self.table_efg)

        self.assertEqual('SELECT "abc"."foo","abc"."bar","hij"."fiz","hij"."buz" '
                         'INTO "efg" FROM "abc" '
                         'JOIN "hij" ON "abc"."id"="hij"."abc_id"', str(query))
