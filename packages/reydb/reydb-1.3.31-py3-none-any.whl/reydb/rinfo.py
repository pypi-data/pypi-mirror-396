# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-05
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Database information methods.
"""


from typing import Literal, TypeVar, Generic, Final, overload

from . import rengine
from .rbase import DatabaseBase
from .rexec import Result


__all__ = (
    'DatabaseInformationBase',
    'DatabaseInformationCatalogSuper',
    'DatabaseInformationCatalog',
    'DatabaseInformationCatalogAsync',
    'DatabaseInformationParameterSuper',
    'DatabaseInformationParameter',
    'DatabaseInformationParameterAsync'
)


DatabaseEngineT = TypeVar('DatabaseEngineT', 'rengine.DatabaseEngine', 'rengine.DatabaseEngineAsync')


class DatabaseInformationBase(DatabaseBase):
    """
    Database information base type.
    """


class DatabaseInformationCatalogSuper(DatabaseInformationBase, Generic[DatabaseEngineT]):
    """
    Database information catalog super type.
    """


    def __init__(self, engine: DatabaseEngineT) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        engine: Database engine.
        """

        # Parameter.
        self.engine = engine


    def handle_after_catalog(self, result: Result) -> dict[str, list[str]]:
        """
        After handle method of get database catalog.

        Parameters
        ----------
        result : Database select result.

        Returns
        -------
        Parameter `catalog`.
        """

        # Convert.
        catalog = {}
        for table, column in result:

            ## Add table. 
            if table not in catalog:
                catalog[table] = [column]
                continue

            ## Add column.
            columns: list = catalog[table]
            columns.append(column)

        return catalog


    def handle_exist(
        self,
        catalog: dict[str, dict[str, list[str]]],
        table: str,
        column: str | None = None
    ) -> bool:
        """
        Handle method of judge database or table or column whether it exists.

        Parameters
        ----------
        catalog : Database catalog.
        table : Table name.
        column : Column name.

        Returns
        -------
        Judge result.
        """

        # Parameter.

        # Judge.
        judge = (
            (columns := catalog.get(table)) is not None
            and (
                column is None
                or column in columns
            )
        )

        return judge


class DatabaseInformationCatalog(DatabaseInformationCatalogSuper['rengine.DatabaseEngine']):
    """
    Database information catalog type.
    """


    def catalog(self, filter_system: bool = True) -> dict[str, list[str]]:
        """
        Get database catalog.

        Parameters
        ----------
        filter_system : Whether filter default database.

        Returns
        -------
        Catalog.
        """

        # Parameter.
        if filter_system:
            where = "table_schema = 'public'"
        else:
            where = None

        # Get.
        result = self.engine.execute.select(
            'information_schema.columns',
            ['table_name', 'column_name'],
            where,
            order='ordinal_position'
        )
        catalog = self.handle_after_catalog(result)

        # Cache.
        if self.engine._catalog is None:
            self.engine._catalog = catalog
        else:
            self.engine._catalog.update(catalog)

        return catalog


    __call__ = catalog


    def exist(
        self,
        table: str,
        column: str | None = None,
        cache: bool = True
    ) -> bool:
        """
        Judge database or table or column whether it exists.

        Parameters
        ----------
        table : Table name.
        column : Column name.
        cache : Whether use cache data, can improve efficiency.

        Returns
        -------
        Judge result.
        """

        # Parameter.
        if (
            cache
            and self.engine._catalog is not None
        ):
            catalog = self.engine._catalog
        else:
            catalog = self.catalog()

        # Judge.
        result = self.handle_exist(catalog, table, column)

        return result


class DatabaseInformationCatalogAsync(DatabaseInformationCatalogSuper['rengine.DatabaseEngineAsync']):
    """
    Asynchronous database information schema type.
    """


    async def catalog(self, filter_system: bool = True) -> dict[str, list[str]]:
        """
        Asynchronous get database catalog.

        Parameters
        ----------
        filter_system : Whether filter default database.

        Returns
        -------
        Catalog.
        """

        # Parameter.
        if filter_system:
            where = "table_schema = 'public'"
        else:
            where = None

        # Get.
        result = await self.engine.execute.select(
            'information_schema.columns',
            ['table_name', 'column_name'],
            where,
            order='ordinal_position'
        )
        catalog = self.handle_after_catalog(result)

        # Cache.
        if self.engine._catalog is None:
            self.engine._catalog = catalog
        else:
            self.engine._catalog.update(catalog)

        return catalog


    __call__ = catalog


    async def exist(
        self,
        table: str,
        column: str | None = None,
        cache: bool = True
    ) -> bool:
        """
        Asynchronous judge database or table or column whether it exists.

        Parameters
        ----------
        table : Table name.
        column : Column name.
        cache : Whether use cache data, can improve efficiency.

        Returns
        -------
        Judge result.
        """

        # Parameter.
        if (
            cache
            and self.engine._catalog is not None
        ):
            catalog = self.engine._catalog
        else:
            catalog = await self.catalog()

        # Judge.
        result = self.handle_exist(catalog, table, column)

        return result


class DatabaseInformationParameterSuper(DatabaseInformationBase, Generic[DatabaseEngineT]):
    """
    Database information parameters super type.
    """


    def __init__(
        self,
        engine: DatabaseEngineT
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        engine: Database engine.
        """

        # Parameter.
        self.engine = engine


class DatabaseInformationParameter(DatabaseInformationParameterSuper['rengine.DatabaseEngine']):
    """
    Database information parameters type.
    """


    def __getitem__(self, key: str) -> str | None:
        """
        Get item of parameter dictionary.

        Parameters
        ----------
        key : Parameter key.

        Returns
        -------
        Parameter value.
        """

        # Get.
        value = self.get(key)

        return value


    def __setitem__(self, key: str, value: str | float) -> None:
        """
        Set item of parameter dictionary.

        Parameters
        ----------
        key : Parameter key.
        value : Parameter value.
        """

        # Set.
        params = {key: value}

        # Update.
        self.update(params)


    @overload
    def get(self) -> dict[str, str]: ...

    @overload
    def get(self, key: str) -> str | None: ...

    def get(self, key: str | None = None) -> dict[str, str] | str | None:
        """
        Get parameter.

        Parameters
        ----------
        key : Parameter key.
            - `None`: Return dictionary of all parameters.
            - `str`: Return value of parameter.

        Returns
        -------
        Parameter value or directory.
        """

        # Get.

        ## All.
        if key is None:
            sql = 'SHOW ALL'
            result = self.engine.execute(sql)
            param = result.to_dict(val_field=1)

        ## One.
        else:
            sql = 'SHOW ' + key
            result = self.engine.execute(sql)
            param = result.scalar()

        return param


    def update(self, params: dict[str, str | float]) -> None:
        """
        Update parameter.

        Parameters
        ----------
        params : Update parameter key value pairs.
        """

        # Update.
        sql = ';\n'.join(
            [
                f'SET "{key}" = \'{value}\''
                for key, value in params.items()
            ]
        )
        self.engine.execute(sql, **params)


class DatabaseInformationParameterAsync(DatabaseInformationParameterSuper['rengine.DatabaseEngineAsync']):
    """
    Asynchronous database information parameters type.
    """


    async def __getitem__(self, key: str) -> str | None:
        """
        Asynchronous get item of parameter dictionary.

        Parameters
        ----------
        key : Parameter key.

        Returns
        -------
        Parameter value.
        """

        # Get.
        value = await self.get(key)

        return value


    async def __setitem__(self, key: str, value: str | float) -> None:
        """
        Asynchronous set item of parameter dictionary.

        Parameters
        ----------
        key : Parameter key.
        value : Parameter value.
        """

        # Set.
        params = {key: value}

        # Update.
        await self.update(params)


    @overload
    async def get(self) -> dict[str, str]: ...

    @overload
    async def get(self, key: str) -> str | None: ...

    async def get(self, key: str | None = None) -> dict[str, str] | str | None:
        """
        Get parameter.

        Parameters
        ----------
        key : Parameter key.
            - `None`: Return dictionary of all parameters.
            - `str`: Return value of parameter.

        Returns
        -------
        Parameter value or directory.
        """

        # Get.

        ## All.
        if key is None:
            sql = 'SHOW ALL'
            result = await self.engine.execute(sql)
            param = result.to_dict(val_field=1)

        ## One.
        else:
            sql = f'SHOW "{key}"'
            result = await self.engine.execute(sql)
            param = result.scalar()

        return param


    async def update(self, params: dict[str, str | float]) -> None:
        """
        Update parameter.

        Parameters
        ----------
        params : Update parameter key value pairs.
        """

        # Update.
        sql = ';\n'.join(
            [
                f'SET "{key}" = \'{value}\''
                for key, value in params.items()
            ]
        )
        await self.engine.execute(sql, **params)
