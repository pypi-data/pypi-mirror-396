import abc
from typing import Literal

import polars as pl
from pydantic import Field

from bayesline.api._src._utils import docstrings_from_sync
from bayesline.api._src.equity.portfolioreport import (
    AsyncReportAccessorApi,
    ReportAccessorApi,
)
from bayesline.api._src.equity.report.accessor import (
    AsyncTypedReportAccessorApi,
    TypedReportAccessorApi,
)
from bayesline.api._src.equity.report.api import AsyncReportApi, ReportApi
from bayesline.api._src.equity.report.settings import ReportSettings
from bayesline.api._src.equity.universe_settings import UniverseSettings
from bayesline.api._src.types import DateLike


class UniverseCountReportSettings(ReportSettings):
    """Settings for a universe count report."""

    universe_settings: UniverseSettings = Field()
    date_aggregation: Literal["last", "mean", "sum"] = Field(
        default="last", description="The date aggregation to use"
    )


class UniverseCountReportAccessor(TypedReportAccessorApi):
    """Specific accessor for a universe count report."""

    @abc.abstractmethod
    def get_counts(self) -> pl.DataFrame:
        """
        Get the counts for the universe.

        Returns
        -------
        pl.DataFrame
            A dataframe with `[date, count]` columns.
        """


@docstrings_from_sync
class AsyncUniverseCountReportAccessor(AsyncTypedReportAccessorApi):

    @abc.abstractmethod
    async def get_counts(self) -> pl.DataFrame: ...  # noqa: D102


class UniverseCountReportApi(
    ReportApi[
        [DateLike | None, DateLike | None],
        UniverseCountReportAccessor,
        UniverseCountReportSettings,
    ]
):
    """API for a universe count report."""

    @abc.abstractmethod
    def calculate(
        self, start_date: DateLike | None, end_date: DateLike | None
    ) -> UniverseCountReportAccessor:
        """
        Calculate the universe count report.

        Parameters
        ----------
        start_date: DateLike | None
            The start date of the report.
        end_date: DateLike | None
            The end date of the report.

        Returns
        -------
        UniverseCountReportAccessor
            The universe count report accessor.
        """


@docstrings_from_sync
class AsyncUniverseCountReportApi(
    AsyncReportApi[
        [DateLike | None, DateLike | None],
        AsyncUniverseCountReportAccessor,
        UniverseCountReportSettings,
    ]
):

    @abc.abstractmethod
    async def calculate(  # noqa: D102
        self, start_date: DateLike | None, end_date: DateLike | None
    ) -> AsyncUniverseCountReportAccessor: ...


class UniverseCountReportAccessorImpl(UniverseCountReportAccessor):  # noqa: D101

    def __init__(self, accessor: ReportAccessorApi):
        self._accessor = accessor

    @property
    def accessor(self) -> ReportAccessorApi:  # noqa: D102
        return self._accessor

    def get_counts(  # noqa: D102
        self,
        *,
        dates: bool = True,
        categorical_hierarchy_levels: dict[str, int] | None = None,
    ) -> pl.DataFrame:
        expand = ["date"] if dates else []
        if categorical_hierarchy_levels:
            for name, level in categorical_hierarchy_levels.items():
                expand.append(f"{name}_level_{level}")
        return self.accessor.get_data([], expand=tuple(expand), value_cols=("count",))


class AsyncUniverseCountReportAccessorImpl(  # noqa: D101
    AsyncUniverseCountReportAccessor
):

    def __init__(self, accessor: AsyncReportAccessorApi):
        self._accessor = accessor

    @property
    def accessor(self) -> AsyncReportAccessorApi:  # noqa: D102
        return self._accessor

    async def get_counts(  # noqa: D102
        self,
        *,
        dates: bool = True,
        categorical_hierarchy_levels: dict[str, int] | None = None,
    ) -> pl.DataFrame:
        expand = ["date"] if dates else []
        if categorical_hierarchy_levels:
            for name, level in categorical_hierarchy_levels.items():
                expand.append(f"{name}_level_{level}")
        return await self.accessor.get_data(
            [], expand=tuple(expand), value_cols=("count",)
        )
