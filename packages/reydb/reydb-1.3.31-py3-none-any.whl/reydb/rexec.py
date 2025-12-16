# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2025-09-22
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Execute methods.
"""


from typing import Any, Literal, TypeVar, Generic, overload
from collections.abc import Iterable, Generator, AsyncGenerator, Container
from datetime import timedelta as Timedelta
from sqlalchemy.sql.elements import TextClause
from reykit.rbase import throw, get_first_notnone
from reykit.rdata import FunctionGenerator
from reykit.rmonkey import monkey_sqlalchemy_result_more_fetch, monkey_sqlalchemy_row_index_field
from reykit.rrand import randn
from reykit.rstdout import echo as recho
from reykit.rtable import TableData, Table
from reykit.rtime import TimeMark, time_to
from reykit.rwrap import wrap_runtime

from . import rconn
from .rbase import DatabaseBase, handle_sql_data


__all__ = (
    'Result',
    'DatabaseExecuteSuper',
    'DatabaseExecute',
    'DatabaseExecuteAsync'
)


# Monkey patch.
_Result = monkey_sqlalchemy_result_more_fetch()
Result = _Result
monkey_sqlalchemy_row_index_field()


DatabaseConnectionT = TypeVar('DatabaseConnectionT', 'rconn.DatabaseConnection', 'rconn.DatabaseConnectionAsync')


class DatabaseExecuteSuper(DatabaseBase, Generic[DatabaseConnectionT]):
    """
    Database execute super type.
    """


    def __init__(self, dbconn: DatabaseConnectionT) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        dbconn : `DatabaseConnection` or `DatabaseConnectionAsync`instance.
        """

        # Build.
        self.conn = dbconn


    def handle_execute(
        self,
        sql: str | TextClause,
        data: TableData | None = None,
        echo: bool | None = None,
        **kwdata: Any
    ) -> tuple[TextClause, list[dict], bool]:
        """
        Handle method of execute SQL.

        Parameters
        ----------
        sql : SQL in method `sqlalchemy.text` format, or `TextClause` object.
        data : Data set for filling.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
            - `bool`: Use this value.
        kwdata : Keyword parameters for filling.

        Returns
        -------
        Parameter `sql` and `data` and `report`.
        """

        # Parameter.
        if data is None:
            if kwdata == {}:
                data = []
            else:
                data = [kwdata]
        else:
            data_table = Table(data)
            data = data_table.to_table()
            for row in data:
                row.update(kwdata)
        sql, data = handle_sql_data(sql, data)
        echo = get_first_notnone(echo, self.conn.engine.echo)

        return sql, data, echo


    def handle_select(
        self,
        table: str,
        fields: str | Iterable[str] | None = None,
        where: str | None = None,
        group: str | None = None,
        having: str | None = None,
        order: str | None = None,
        limit: int | str | tuple[int, int] | None = None
    ) -> str:
        """
        Handle method of execute select SQL.

        Parameters
        ----------
        table : Table name.
        fields : Select clause content.
            - `None`: Is `SELECT *`.
            - `str`: Join as `SELECT str`.
            - `Iterable[str]`: Join as `SELECT "str", ...`.
                `str and first character is ':'`: Use this syntax.
                `str`: Use this field.
        where : Clause `WHERE` content, join as `WHERE str`.
        group : Clause `GROUP BY` content, join as `GROUP BY str`.
        having : Clause `HAVING` content, join as `HAVING str`.
        order : Clause `ORDER BY` content, join as `ORDER BY str`.
        limit : Clause `LIMIT` content.
            - `int | str`: Join as `LIMIT int/str`.
            - `tuple[int, int]`: Join as `LIMIT int, int`.

        Returns
        -------
        Parameter `sql`.
        """

        # Parameter.
        if '"' not in table:
            table = '.'.join(
                [
                    f'"{part}"'
                    for part in table.split('.')
                ]
            )

        # Generate SQL.
        sql_list = []

        ## Part 'SELECT' syntax.
        if fields is None:
            fields = '*'
        elif type(fields) != str:
            fields = ', '.join(
                [
                    field[1:]
                    if (
                        field.startswith(':')
                        and field != ':'
                    )
                    else f'"{field}"'
                    for field in fields
                ]
            )
        sql_select = f'SELECT {fields}'
        sql_list.append(sql_select)

        ## Part 'FROM' syntax.
        sql_from = f'FROM {table}'
        sql_list.append(sql_from)

        ## Part 'WHERE' syntax.
        if where is not None:
            sql_where = f'WHERE {where}'
            sql_list.append(sql_where)

        ## Part 'GROUP BY' syntax.
        if group is not None:
            sql_group = f'GROUP BY {group}'
            sql_list.append(sql_group)

        ## Part 'GROUP BY' syntax.
        if having is not None:
            sql_having = f'HAVING {having}'
            sql_list.append(sql_having)

        ## Part 'ORDER BY' syntax.
        if order is not None:
            sql_order = f'ORDER BY {order}'
            sql_list.append(sql_order)

        ## Part 'LIMIT' syntax.
        if limit is not None:
            if type(limit) in (str, int):
                sql_limit = f'LIMIT {limit}'
            else:
                if len(limit) == 2:
                    sql_limit = f'LIMIT {limit[0]}, {limit[1]}'
                else:
                    throw(ValueError, limit)
            sql_list.append(sql_limit)

        ## Join sql part.
        sql = '\n'.join(sql_list)

        return sql


    @overload
    def handle_insert(
        self,
        table: str,
        data: TableData,
        *,
        returning: str | Iterable[str] | None = None,
        **kwdata: Any
    ) -> tuple[str, dict]: ...

    @overload
    def handle_insert(
        self,
        table: str,
        data: TableData,
        conflict: str | Iterable[str] | None = None,
        conflict_do: Literal['nothing', 'update'] | str | Iterable[str] = 'nothing',
        returning: str | Iterable[str] | None = None,
        **kwdata: Any
    ) -> tuple[str, dict]: ...

    def handle_insert(
        self,
        table: str,
        data: TableData,
        conflict: str | Iterable[str] | None = None,
        conflict_do: Literal['nothing', 'update'] | str | Iterable[str] = 'nothing',
        returning: str | Iterable[str] | None = None,
        **kwdata: Any
    ) -> tuple[str, dict]:
        """
        Handle method of execute insert SQL.

        Parameters
        ----------
        table : Table name.
        data : Insert data.
        conflict : Handle constraint conflict field names.
        conflict_do : Handle constraint conflict method.
            - `Literal['nothing']: Ignore conflict.
            - `Literal['update']: Update to all insert data.
            - `str | Iterable[str]`: Update to this fields insert data.
        returning : Return the fields of the inserted record.
        kwdata : Keyword parameters for filling.
            - `str and first character is ':'`: Use this syntax.
            - `Any`: Use this value.

        Returns
        -------
        Parameter `sql` and `kwdata`.
        """

        # Parameter.
        if '"' not in table:
            table = '.'.join(
                [
                    f'"{part}"'
                    for part in table.split('.')
                ]
            )
        if type(conflict) == str:
            conflict = (conflict,)
        if returning is not None:
            if type(returning) == str:
                if returning != '*':
                    returning = f'"{returning}"'
                returning = [returning]

        ## Data.
        data_table = Table(data)
        data = data_table.to_table()

        ## Check.
        if data in ([], [{}]):
            throw(ValueError, data)

        ## Keyword data.
        kwdata_method = {}
        kwdata_replace = {}
        for key, value in kwdata.items():
            if (
                type(value) == str
                and value.startswith(':')
                and value != ':'
            ):
                kwdata_method[key] = value[1:]
            else:
                kwdata_replace[key] = value

        # Generate SQL.
        sqls = []

        ## Part 'insert' syntax.
        fields_replace = {
            field
            for row in data
            for field in row
        }
        fields_replace = {
            field
            for field in fields_replace
            if field not in kwdata
        }
        sql_fields_list = (
            *kwdata_method,
            *kwdata_replace,
            *fields_replace
        )
        sql_fields = ', '.join(
            [
                f'"{field}"'
                for field in sql_fields_list
            ]
        )
        sql_insert = f'INSERT INTO {table} ({sql_fields})'
        sqls.append(sql_insert)

        ## Part 'values' syntax.
        sql_values_list = (
            *kwdata_method.values(),
            *[
                ':' + field
                for field in (
                    *kwdata_replace,
                    *fields_replace
                )
            ]
        )
        sql_values = ', '.join(sql_values_list)
        sql_value = f'VALUES ({sql_values})'
        sqls.append(sql_value)

        ## Part 'conflict' syntax.
        if conflict is not None:
            sql_conflict = 'ON CONFLICT(%s)' % ', '.join(
                [
                    f'"{field}"'
                    for field in conflict
                ]
            )
            sqls.append(sql_conflict)
            if conflict_do == 'nothing':
                sql_conflict_do = 'DO NOTHING'
            else:
                if (
                    conflict_do != 'update'
                    and type(conflict_do) == str
                ):
                    conflict_do = (conflict_do,)
                sql_conflict_do = 'DO UPDATE SET\n    ' + ',\n    '.join(
                    [
                        f'"{field}" = EXCLUDED."{field}"'
                        for field in sql_fields_list
                        if (
                            conflict_do == 'update'
                            or field in conflict_do
                        )
                    ]
                )
            sqls.append(sql_conflict_do)

        ## Part 'returning` syntax.
        if returning is not None:
            sql_returning = 'RETURNING ' + ', '.join(returning)
            sqls.append(sql_returning)

        ## Join sql part.
        sql = '\n'.join(sqls)

        return sql, kwdata_replace


    def handle_update(
        self,
        table: str,
        data: TableData,
        **kwdata: Any
    ) -> tuple[str, dict]:
        """
        Execute update SQL.

        Parameters
        ----------
        table : Table name.
        data : Update data, join as `key = :value`.
            - `Key`: Table field, each row of fields must be the same, the first field is `WHERE` content.
            - `Value`: Table value.
        kwdata : Keyword parameters for filling.
            - `str and first character is ':'`: Use this syntax.
            - `Any`: Use this value.

        Returns
        -------
        Parameter `sql` and `data`.
        """

        # Parameter.
        if '"' not in table:
            table = '.'.join(
                [
                    f'"{part}"'
                    for part in table.split('.')
                ]
            )

        ## Data.
        data_table = Table(data)
        data = data_table.to_table()

        ### Check.
        if data in ([], [{}]):
            throw(ValueError, data)

        ### Keyword data.
        kwdata_syntax = {}
        kwdata_value = {}
        for key, value in kwdata.items():
            if (
                type(value) == str
                and value.startswith(':')
                and value != ':'
            ):
                kwdata_syntax[key] = value[1:]
            else:
                kwdata_value[key] = value
        for row in data:
            row.update(kwdata_value)

        ### Where field.
        fields = list(data[0])
        where_filed, *set_fields = fields

        # Generate SQL.
        sql_list = []

        ## Part 'UPDATE' syntax.
        sql_update = f'UPDATE {table}'
        sql_list.append(sql_update)

        ## Part 'SET' syntax.
        sql_set_list = [
            f'"{field}" = :{field}'
            for field in set_fields
        ]
        sql_set_list.extend(
            [
                f'"{key}" = {syntax}'
                for field, syntax in kwdata_syntax.items()
            ]
        )
        sql_set = 'SET ' + ',\n    '.join(sql_set_list)
        sql_list.append(sql_set)

        ## Part 'WHERE' syntax.
        sql_where = f'WHERE "{where_filed}" = :{where_filed}'
        sql_list.append(sql_where)

        ## Join sql part.
        sql = '\n'.join(sql_list)

        return sql, data


    def handle_delete(
        self,
        table: str,
        where: str | None = None,
        order: str | None = None,
        limit: int | str | None = None
    ) -> str:
        """
        Execute delete SQL.

        Parameters
        ----------
        table : Table name.
        where : Clause `WHERE` content, join as `WHERE str`.
        order : Clause `ORDER BY` content, join as `ORDER BY str`.
        limit : Clause `LIMIT` content, join as `LIMIT int/str`.

        Returns
        -------
        Parameter `sql`.
        """

        # Parameter.
        if '"' not in table:
            table = '.'.join(
                [
                    f'"{part}"'
                    for part in table.split('.')
                ]
            )

        # Generate SQL.
        sqls = []

        ## Part 'DELETE' syntax.
        sql_delete = f'DELETE FROM {table}'
        sqls.append(sql_delete)

        ## Part 'WHERE' syntax.
        if where is not None:
            sql_where = f'WHERE {where}'
            sqls.append(sql_where)

        ## Part 'ORDER BY' syntax.
        if order is not None:
            sql_order = f'ORDER BY {order}'
            sqls.append(sql_order)

        ## Part 'LIMIT' syntax.
        if limit is not None:
            sql_limit = f'LIMIT {limit}'
            sqls.append(sql_limit)

        ## Join sqls.
        sqls = '\n'.join(sqls)

        return sqls


    def handle_copy(
        self,
        table: str,
        fields: str | Iterable[str] | None = None,
        where: str | None = None,
        limit: int | str | tuple[int, int] | None = None
    ) -> str:
        """
        Execute inesrt SQL of copy records.

        Parameters
        ----------
        table : Table name.
        fields : Select clause content.
            - `None`: Is `SELECT *`.
            - `str`: Join as `SELECT str`.
            - `Iterable[str]`: Join as `SELECT "str", ...`.
        where : Clause `WHERE` content, join as `WHERE str`.
        limit : Clause `LIMIT` content.
            - `int | str`: Join as `LIMIT int/str`.
            - `tuple[int, int]`: Join as `LIMIT int, int`.

        Returns
        -------
        Parameter `sql`.
        """

        # Parameter.
        if '"' not in table:
            table = '.'.join(
                [
                    f'"{part}"'
                    for part in table.split('.')
                ]
            )
        if fields is None:
            fields = '*'
        elif type(fields) != str:
            fields = ', '.join(fields)

        # Generate SQL.
        sqls = []

        ## Part 'INSERT' syntax.
        sql_insert = f'INSERT INTO {table}'
        if fields != '*':
            sql_insert += f' ({fields})'
        sqls.append(sql_insert)

        ## Part 'SELECT' syntax.
        sql_select = (
            f'SELECT {fields}\n'
            f'FROM {table}'
        )
        sqls.append(sql_select)

        ## Part 'WHERE' syntax.
        if where is not None:
            sql_where = f'WHERE {where}'
            sqls.append(sql_where)

        ## Part 'LIMIT' syntax.
        if limit is not None:
            if type(limit) in (str, int):
                sql_limit = f'LIMIT {limit}'
            else:
                if len(limit) == 2:
                    sql_limit = f'LIMIT {limit[0]}, {limit[1]}'
                else:
                    throw(ValueError, limit)
            sqls.append(sql_limit)

        ## Join.
        sql = '\n'.join(sqls)

        return sql


class DatabaseExecute(DatabaseExecuteSuper['rconn.DatabaseConnection']):
    """
    Database execute type.
    """


    def execute(
        self,
        sql: str | TextClause,
        data: TableData | None = None,
        echo: bool | None = None,
        **kwdata: Any
    ) -> Result:
        """
        Execute SQL.

        Parameters
        ----------
        sql : SQL in method `sqlalchemy.text` format, or `TextClause` object.
        data : Data set for filling.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
            - `bool`: Use this value.
        kwdata : Keyword parameters for filling.

        Returns
        -------
        Result object.
        """

        # Parameter.
        sql, data, echo = self.handle_execute(sql, data, echo, **kwdata)

        # Transaction.
        self.conn.get_begin()

        # Execute.

        ## Report.
        if echo:
            execute = wrap_runtime(self.conn.connection.execute, to_return=True, to_print=False)
            result, report_runtime, *_ = execute(sql, data)
            report_info = (
                f'{report_runtime}\n'
                f'Row Count: {result.rowcount}'
            )
            sql = sql.text.strip()
            if data == []:
                recho(report_info, sql, title='SQL')
            else:
                recho(report_info, sql, data, title='SQL')

        ## Not report.
        else:
            result = self.conn.connection.execute(sql, data)

        # Automatic commit.
        if self.conn.autocommit:
            self.conn.commit()
            self.conn.close()

        return result


    __call__ = execute


    def select(
        self,
        table: str,
        fields: str | Iterable[str] | None = None,
        where: str | None = None,
        group: str | None = None,
        having: str | None = None,
        order: str | None = None,
        limit: int | str | tuple[int, int] | None = None,
        echo: bool | None = None,
        **kwdata: Any
    ) -> Result:
        """
        Execute select SQL.

        Parameters
        ----------
        table : Table name.
        fields : Select clause content.
            - `None`: Is `SELECT *`.
            - `str`: Join as `SELECT str`.
            - `Iterable[str]`: Join as `SELECT "str", ...`.
                `str and first character is ':'`: Use this syntax.
                `str`: Use this field.
        where : Clause `WHERE` content, join as `WHERE str`.
        group : Clause `GROUP BY` content, join as `GROUP BY str`.
        having : Clause `HAVING` content, join as `HAVING str`.
        order : Clause `ORDER BY` content, join as `ORDER BY str`.
        limit : Clause `LIMIT` content.
            - `int | str`: Join as `LIMIT int/str`.
            - `tuple[int, int]`: Join as `LIMIT int, int`.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
        kwdata : Keyword parameters for filling.

        Returns
        -------
        Result object.

        Examples
        --------
        Parameter `fields`.
        >>> fields = ['id', ':"id" + 1 AS "id_"']
        >>> result = Database.execute.select('table', fields)
        >>> print(result.to_table())
        [{'id': 1, 'id_': 2}, ...]

        Parameter `kwdata`.
        >>> fields = ['id', ':"id" + :value AS "id_"]
        >>> result = Database.execute.select('table', fields, value=1)
        >>> print(result.to_table())
        [{'id': 1, 'id_': 2}, ...]
        """

        # Parameter.
        sql = self.handle_select(table, fields, where, group, having, order, limit)

        # Execute SQL.
        result = self.execute(sql, echo=echo, **kwdata)

        return result


    def insert(
        self,
        table: str,
        data: TableData,
        conflict: str | Iterable[str] | None = None,
        conflict_do: Literal['nothing', 'update'] | str | Iterable[str] = 'nothing',
        returning: str | Iterable[str] | None = None,
        echo: bool | None = None,
        **kwdata: Any
    ) -> Result:
        """
        Execute insert SQL.

        Parameters
        ----------
        table : Table name.
        data : Insert data.
        conflict : Handle constraint conflict field names.
        conflict_do : Handle constraint conflict method.
            - `Literal['nothing']: Ignore conflict.
            - `Literal['update']: Update to all insert data.
            - `str | Iterable[str]`: Update to this fields insert data.
        returning : Return the fields of the inserted record.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
        kwdata : Keyword parameters for filling.
            - `str and first character is ':'`: Use this syntax.
            - `Any`: Use this value.

        Returns
        -------
        Result object.

        Examples
        --------
        >>> data = [{'key': 'a'}, {'key': 'b'}]
        >>> kwdata = {'value1': 1, 'value2': ':(SELECT 2)'}
        >>> result = Database.execute.insert('table', data, **kwdata)
        >>> print(result.rowcount)
        2
        >>> result = Database.execute.select('table')
        >>> print(result.to_table())
        [{'key': 'a', 'value1': 1, 'value2': 2}, {'key': 'b', 'value1': 1, 'value2': 2}]
        """

        # Parameter.
        sql, kwdata = self.handle_insert(table, data, conflict, conflict_do, returning, **kwdata)

        # Execute SQL.
        result = self.execute(sql, data, echo, **kwdata)

        return result


    def update(
        self,
        table: str,
        data: TableData,
        echo: bool | None = None,
        **kwdata: Any
    ) -> Result:
        """
        Execute update SQL.

        Parameters
        ----------
        table : Table name.
        data : Update data, join as `key = :value`.
            - `Key`: Table field, each row of fields must be the same, the first field is `WHERE` content.
            - `Value`: Table value.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
        kwdata : Keyword parameters for filling.
            - `str and first character is ':'`: Use this syntax.
            - `Any`: Use this value.

        Returns
        -------
        Result object.

        Examples
        --------
        >>> data = [{'id': 1, 'name': 'a'}, {'id': 2, 'name': 'b'}]
        >>> kwdata = {'valid': True, 'time': ':now()'}
        >>> result = Database.execute.update('table', data, **kwdata)
        """

        # Parameter.
        sql, data = self.handle_update(table, data, **kwdata)

        # Execute SQL.
        result = self.execute(sql, data, echo)

        return result


    def delete(
        self,
        table: str,
        where: str | None = None,
        order: str | None = None,
        limit: int | str | None = None,
        echo: bool | None = None,
        **kwdata: Any
    ) -> Result:
        """
        Execute delete SQL.

        Parameters
        ----------
        table : Table name.
        where : Clause `WHERE` content, join as `WHERE str`.
        order : Clause `ORDER BY` content, join as `ORDER BY str`.
        limit : Clause `LIMIT` content, join as `LIMIT int/str`.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
        kwdata : Keyword parameters for filling.

        Returns
        -------
        Result object.

        Examples
        --------
        >>> where = '"id" IN :ids'
        >>> ids = (1, 2)
        >>> result = Database.execute.delete('table', where, ids=ids)
        >>> print(result.rowcount)
        2
        """

        # Parameter.
        sql = self.handle_delete(table, where, order, limit)

        # Execute SQL.
        result = self.execute(sql, echo=echo, **kwdata)

        return result


    def copy(
        self,
        table: str,
        fields: str | Iterable[str] | None = None,
        where: str | None = None,
        limit: int | str | tuple[int, int] | None = None,
        echo: bool | None = None,
        **kwdata: Any
    ) -> Result:
        """
        Execute inesrt SQL of copy records.

        Parameters
        ----------
        table : Table name.
        fields : Select clause content.
            - `None`: Is `SELECT *`.
            - `str`: Join as `SELECT str`.
            - `Iterable[str]`: Join as `SELECT "str", ...`.
        where : Clause `WHERE` content, join as `WHERE str`.
        limit : Clause `LIMIT` content.
            - `int | str`: Join as `LIMIT int/str`.
            - `tuple[int, int]`: Join as `LIMIT int, int`.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
        kwdata : Keyword parameters for filling.

        Returns
        -------
        Result object.

        Examples
        --------
        >>> where = '"id" IN :ids'
        >>> ids = (1, 2, 3)
        >>> result = Database.execute.copy('table', where, 2, ids=ids, id=None, time=':NOW()')
        >>> print(result.rowcount)
        2
        """

        # Parameter.
        sql = self.handle_copy(table, fields, where, limit)

        # Execute SQL.
        result = self.execute(sql, echo=echo, **kwdata)

        return result


    def count(
        self,
        table: str,
        where: str | None = None,
        echo: bool | None = None,
        **kwdata: Any
    ) -> int:
        """
        Execute inesrt SQL of count records.

        Parameters
        ----------
        table : Table name.
        where : Match condition, `WHERE` clause content, join as `WHERE str`.
            - `None`: Match all.
            - `str`: Match condition.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
        kwdata : Keyword parameters for filling.

        Returns
        -------
        Record count.

        Examples
        --------
        >>> where = '"id" IN :ids'
        >>> ids = (1, 2)
        >>> result = Database.execute.count('table', where, ids=ids)
        >>> print(result)
        2
        """

        # Execute.
        result = self.select(table, '1', where=where, echo=echo, **kwdata)
        count = len(tuple(result))

        return count


    def exist(
        self,
        table: str,
        where: str | None = None,
        echo: bool | None = None,
        **kwdata: Any
    ) -> bool:
        """
        Execute inesrt SQL of Judge the exist of record.

        Parameters
        ----------
        table : Table name.
        where : Match condition, `WHERE` clause content, join as `WHERE str`.
            - `None`: Match all.
            - `str`: Match condition.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
        kwdata : Keyword parameters for filling.

        Returns
        -------
        Judged result.

        Examples
        --------
        >>> data = [{'id': 1}]
        >>> Database.execute.insert('table', data)
        >>> where = '"id" = :id_'
        >>> id_ = 1
        >>> result = Database.execute.exist('table', where, id_=id_)
        >>> print(result)
        True
        """

        # Execute.
        result = self.count(table, where, echo, **kwdata)

        # Judge.
        judge = result != 0

        return judge


    def generator(
        self,
        sql: str | TextClause,
        data: TableData,
        echo: bool | None = None,
        **kwdata: Any
    ) -> Generator[Result, Any, None]:
        """
        Return a generator that can execute SQL.

        Parameters
        ----------
        sql : SQL in method `sqlalchemy.text` format, or `TextClause` object.
        data : Data set for filling.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
            - `bool`: Use this value.
        kwdata : Keyword parameters for filling.

        Returns
        -------
        Generator.
        """

        # Instance.
        func_generator = FunctionGenerator(
            self.execute,
            sql=sql,
            echo=echo,
            **kwdata
        )

        # Add.
        for row in data:
            func_generator(**row)

        # Create.
        generator = func_generator.generator()

        return generator


    @overload
    def sleep(self, echo: bool | None = None) -> int: ...

    @overload
    def sleep(self, second: int, echo: bool | None = None) -> int: ...

    @overload
    def sleep(self, low: int = 0, high: int = 10, echo: bool | None = None) -> int: ...

    @overload
    def sleep(self, *thresholds: float, echo: bool | None = None) -> float: ...

    @overload
    def sleep(self, *thresholds: float, precision: Literal[0], echo: bool | None = None) -> int: ...

    @overload
    def sleep(self, *thresholds: float, precision: int, echo: bool | None = None) -> float: ...

    def sleep(self, *thresholds: float, precision: int | None = None, echo: bool | None = None) -> float:
        """
        Let the database wait random seconds.

        Parameters
        ----------
        thresholds : Low and high thresholds of random range, range contains thresholds.
            - When `length is 0`, then low and high thresholds is `0` and `10`.
            - When `length is 1`, then low and high thresholds is `0` and `thresholds[0]`.
            - When `length is 2`, then low and high thresholds is `thresholds[0]` and `thresholds[1]`.
        precision : Precision of random range, that is maximum decimal digits of return value.
            - `None`: Set to Maximum decimal digits of element of parameter `thresholds`.
            - `int`: Set to this value.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
            - `bool`: Use this value.

        Returns
        -------
        Random seconds.
            - When parameters `precision` is `0`, then return int.
            - When parameters `precision` is `greater than 0`, then return float.
        """

        # Parameter.
        if len(thresholds) == 1:
            second = thresholds[0]
        else:
            second = randn(*thresholds, precision=precision)

        # Sleep.
        sql = f'SELECT SLEEP({second})'
        self.execute(sql, echo=echo)

        return second


class DatabaseExecuteAsync(DatabaseExecuteSuper['rconn.DatabaseConnectionAsync']):
    """
    Asynchronous database execute type.
    """


    async def execute(
        self,
        sql: str | TextClause,
        data: TableData | None = None,
        echo: bool | None = None,
        **kwdata: Any
    ) -> Result:
        """
        Asynchronous execute SQL.

        Parameters
        ----------
        sql : SQL in method `sqlalchemy.text` format, or `TextClause` object.
        data : Data set for filling.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
        kwdata : Keyword parameters for filling.

        Returns
        -------
        Result object.
        """

        # Parameter.
        sql, data, echo = self.handle_execute(sql, data, echo, **kwdata)

        # Transaction.
        await self.conn.get_begin()

        # Execute.

        ## Report.
        if echo:
            tm = TimeMark()
            tm()
            result = await self.conn.connection.execute(sql, data)
            tm()

            ### Generate report.
            start_time = tm.records[0]['datetime']
            spend_time: Timedelta = tm.records[1]['timedelta']
            end_time = tm.records[1]['datetime']
            start_str = time_to(start_time, True)[:-3]
            spend_str = time_to(spend_time, True)[:-3]
            end_str = time_to(end_time, True)[:-3]
            report_runtime = 'Start: %s -> Spend: %ss -> End: %s' % (
                start_str,
                spend_str,
                end_str
            )
            report_info = (
                f'{report_runtime}\n'
                f'Row Count: {result.rowcount}'
            )
            sql = sql.text.strip()
            if data == []:
                recho(report_info, sql, title='SQL')
            else:
                recho(report_info, sql, data, title='SQL')

        ## Not report.
        else:
            result = await self.conn.connection.execute(sql, data)

        # Automatic commit.
        if self.conn.autocommit:
            await self.conn.commit()
            await self.conn.close()

        return result


    __call__ = execute


    async def select(
        self,
        table: str,
        fields: str | Iterable[str] | None = None,
        where: str | None = None,
        group: str | None = None,
        having: str | None = None,
        order: str | None = None,
        limit: int | str | tuple[int, int] | None = None,
        echo: bool | None = None,
        **kwdata: Any
    ) -> Result:
        """
        Asynchronous execute select SQL.

        Parameters
        ----------
        table : Table name.
        fields : Select clause content.
            - `None`: Is `SELECT *`.
            - `str`: Join as `SELECT str`.
            - `Iterable[str]`: Join as `SELECT "str", ...`.
                `str and first character is ':'`: Use this syntax.
                `str`: Use this field.
        where : Clause `WHERE` content, join as `WHERE str`.
        group : Clause `GROUP BY` content, join as `GROUP BY str`.
        having : Clause `HAVING` content, join as `HAVING str`.
        order : Clause `ORDER BY` content, join as `ORDER BY str`.
        limit : Clause `LIMIT` content.
            - `int | str`: Join as `LIMIT int/str`.
            - `tuple[int, int]`: Join as `LIMIT int, int`.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
        kwdata : Keyword parameters for filling.

        Returns
        -------
        Result object.

        Examples
        --------
        Parameter `fields`.
        >>> fields = ['id', ':"id" + 1 AS "id_"']
        >>> result = await Database.execute.select('table', fields)
        >>> print(result.to_table())
        [{'id': 1, 'id_': 2}, ...]

        Parameter `kwdata`.
        >>> fields = ['id', ':"id" + :value AS "id_"]
        >>> result = await Database.execute.select('table', fields, value=1)
        >>> print(result.to_table())
        [{'id': 1, 'id_': 2}, ...]
        """

        # Parameter.
        sql = self.handle_select(table, fields, where, group, having, order, limit)

        # Execute SQL.
        result = await self.execute(sql, echo=echo, **kwdata)

        return result


    async def insert(
        self,
        table: str,
        data: TableData,
        conflict: str | Iterable[str] | None = None,
        conflict_do: Literal['nothing', 'update'] | str | Iterable[str] = 'nothing',
        returning: str | Iterable[str] | None = None,
        echo: bool | None = None,
        **kwdata: Any
    ) -> Result:
        """
        Asynchronous execute insert SQL.

        Parameters
        ----------
        table : Table name.
        data : Insert data.
        conflict : Handle constraint conflict field names.
        conflict_do : Handle constraint conflict method.
            - `Literal['nothing']: Ignore conflict.
            - `Literal['update']: Update to all insert data.
            - `str | Iterable[str]`: Update to this fields insert data.
        returning : Return the fields of the inserted record.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
        kwdata : Keyword parameters for filling.
            - `str and first character is ':'`: Use this syntax.
            - `Any`: Use this value.

        Returns
        -------
        Result object.

        Examples
        --------
        >>> data = [{'key': 'a'}, {'key': 'b'}]
        >>> kwdata = {'value1': 1, 'value2': ':(SELECT 2)'}
        >>> result = Database.execute.insert('table', data, **kwdata)
        >>> print(result.rowcount)
        2
        >>> result = Database.execute.select('table')
        >>> print(result.to_table())
        [{'key': 'a', 'value1': 1, 'value2': 2}, {'key': 'b', 'value1': 1, 'value2': 2}]
        """

        # Parameter.
        sql, kwdata = self.handle_insert(table, data, conflict, conflict_do, returning, **kwdata)

        # Execute SQL.
        result = await self.execute(sql, data, echo, **kwdata)

        return result


    async def update(
        self,
        table: str,
        data: TableData,
        echo: bool | None = None,
        **kwdata: Any
    ) -> Result:
        """
        Asynchronous execute update SQL.

        Parameters
        ----------
        table : Table name.
        data : Update data, join as `key = :value`.
            - `Key`: Table field, each row of fields must be the same, the first field is `WHERE` content.
            - `Value`: Table value.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
        kwdata : Keyword parameters for filling.
            - `str and first character is ':'`: Use this syntax.
            - `Any`: Use this value.

        Returns
        -------
        Result object.

        Examples
        --------
        >>> data = [{'id': 1, 'name': 'a'}, {'id': 2, 'name': 'b'}]
        >>> kwdata = {'valid': True, 'time': ':now()'}
        >>> result = Database.execute.update('table', data, **kwdata)
        """

        # Parameter.
        sql, data = self.handle_update(table, data, **kwdata)

        # Execute SQL.
        result = await self.execute(sql, data, echo)

        return result


    async def delete(
        self,
        table: str,
        where: str | None = None,
        order: str | None = None,
        limit: int | str | None = None,
        echo: bool | None = None,
        **kwdata: Any
    ) -> Result:
        """
        Asynchronous execute delete SQL.

        Parameters
        ----------
        table : Table name.
        where : Clause `WHERE` content, join as `WHERE str`.
        order : Clause `ORDER BY` content, join as `ORDER BY str`.
        limit : Clause `LIMIT` content, join as `LIMIT int/str`.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
        kwdata : Keyword parameters for filling.

        Returns
        -------
        Result object.

        Examples
        --------
        >>> where = '"id" IN :ids'
        >>> ids = (1, 2)
        >>> result = await Database.execute.delete('table', where, ids=ids)
        >>> print(result.rowcount)
        2
        """

        # Parameter.
        sql = self.handle_delete(table, where, order, limit)

        # Execute SQL.
        result = await self.execute(sql, echo=echo, **kwdata)

        return result


    async def copy(
        self,
        table: str,
        fields: str | Iterable[str] | None = None,
        where: str | None = None,
        limit: int | str | tuple[int, int] | None = None,
        echo: bool | None = None,
        **kwdata: Any
    ) -> Result:
        """
        Asynchronous execute inesrt SQL of copy records.

        Parameters
        ----------
        table : Table name.
        fields : Select clause content.
            - `None`: Is `SELECT *`.
            - `str`: Join as `SELECT str`.
            - `Iterable[str]`: Join as `SELECT "str", ...`.
        where : Clause `WHERE` content, join as `WHERE str`.
        limit : Clause `LIMIT` content.
            - `int | str`: Join as `LIMIT int/str`.
            - `tuple[int, int]`: Join as `LIMIT int, int`.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
        kwdata : Keyword parameters for filling.

        Returns
        -------
        Result object.

        Examples
        --------
        >>> where = '"id" IN :ids'
        >>> ids = (1, 2, 3)
        >>> result = await Database.execute.copy('table', ['name', 'value'], where, 2, ids=ids)
        >>> print(result.rowcount)
        2
        """

        # Parameter.
        sql = self.handle_copy(table, fields, where, limit)

        # Execute SQL.
        result = await self.execute(sql, echo=echo, **kwdata)

        return result


    async def count(
        self,
        table: str,
        where: str | None = None,
        echo: bool | None = None,
        **kwdata: Any
    ) -> int:
        """
        Asynchronous execute inesrt SQL of count records.

        Parameters
        ----------
        table : Table name.
        where : Match condition, `WHERE` clause content, join as `WHERE str`.
            - `None`: Match all.
            - `str`: Match condition.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
        kwdata : Keyword parameters for filling.

        Returns
        -------
        Record count.

        Examples
        --------
        >>> where = '"id" IN :ids'
        >>> ids = (1, 2)
        >>> result = await Database.execute.count('table', where, ids=ids)
        >>> print(result)
        2
        """

        # Execute.
        result = await self.select(table, '1', where=where, echo=echo, **kwdata)
        count = len(tuple(result))

        return count


    async def exist(
        self,
        table: str,
        where: str | None = None,
        echo: bool | None = None,
        **kwdata: Any
    ) -> bool:
        """
        Asynchronous execute inesrt SQL of Judge the exist of record.

        Parameters
        ----------
        table : Table name.
        where : Match condition, `WHERE` clause content, join as `WHERE str`.
            - `None`: Match all.
            - `str`: Match condition.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
        kwdata : Keyword parameters for filling.

        Returns
        -------
        Judged result.

        Examples
        --------
        >>> data = [{'id': 1}]
        >>> Database.execute.insert('table', data)
        >>> where = '"id" = :id_'
        >>> id_ = 1
        >>> result = await Database.execute.exist('table', where, id_=id_)
        >>> print(result)
        True
        """

        # Execute.
        result = await self.count(table, where, echo, **kwdata)

        # Judge.
        judge = result != 0

        return judge


    async def generator(
        self,
        sql: str | TextClause,
        data: TableData,
        echo: bool | None = None,
        **kwdata: Any
    ) -> AsyncGenerator[Result, Any]:
        """
        Asynchronous return a generator that can execute SQL.

        Parameters
        ----------
        sql : SQL in method `sqlalchemy.text` format, or `TextClause` object.
        data : Data set for filling.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.
        kwdata : Keyword parameters for filling.

        Returns
        -------
        AsyncGenerator.
        """

        # Instance.
        func_generator = FunctionGenerator(
            self.execute,
            sql=sql,
            echo=echo,
            **kwdata
        )

        # Add.
        for row in data:
            func_generator(**row)

        # Create.
        agenerator = func_generator.agenerator()

        return agenerator


    @overload
    async def sleep(self, echo: bool | None = None) -> int: ...

    @overload
    async def sleep(self, second: int, echo: bool | None = None) -> int: ...

    @overload
    async def sleep(self, low: int = 0, high: int = 10, echo: bool | None = None) -> int: ...

    @overload
    async def sleep(self, *thresholds: float, echo: bool | None = None) -> float: ...

    @overload
    async def sleep(self, *thresholds: float, precision: Literal[0], echo: bool | None = None) -> int: ...

    @overload
    async def sleep(self, *thresholds: float, precision: int, echo: bool | None = None) -> float: ...

    async def sleep(self, *thresholds: float, precision: int | None = None, echo: bool | None = None) -> float:
        """
        Asynchronous let the database wait random seconds.

        Parameters
        ----------
        thresholds : Low and high thresholds of random range, range contains thresholds.
            - When `length is 0`, then low and high thresholds is `0` and `10`.
            - When `length is 1`, then low and high thresholds is `0` and `thresholds[0]`.
            - When `length is 2`, then low and high thresholds is `thresholds[0]` and `thresholds[1]`.
        precision : Precision of random range, that is maximum decimal digits of return value.
            - `None`: Set to Maximum decimal digits of element of parameter `thresholds`.
            - `int`: Set to this value.
        echo : Whether report SQL execute information.
            - `None`: Use attribute `Database.echo`.

        Returns
        -------
        Random seconds.
            - When parameters `precision` is `0`, then return int.
            - When parameters `precision` is `greater than 0`, then return float.
        """

        # Parameter.
        if len(thresholds) == 1:
            second = thresholds[0]
        else:
            second = randn(*thresholds, precision=precision)

        # Sleep.
        sql = f'SELECT SLEEP({second})'
        await self.execute(sql, echo=echo)

        return second
