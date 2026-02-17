from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .client import ApiRequestError, GbizInfoClient
from .config import Settings, load_settings_from_env
from .validators import (
    ensure_corporate_number,
    ensure_from_to_range,
    ensure_limit,
    ensure_metadata_flag,
    ensure_page,
    ensure_yyyymmdd,
)


def _to_query(params: dict[str, Any]) -> dict[str, str]:
    query: dict[str, str] = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, bool):
            query[key] = "true" if value else "false"
        else:
            query[key] = str(value)
    return query


class GbizInfoToolset:
    def __init__(self, client: GbizInfoClient) -> None:
        self._client = client

    async def _execute(
        self,
        path: str,
        *,
        query: dict[str, str] | None = None,
        path_params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        try:
            return await self._client.get(path=path, query=query, path_params=path_params)
        except ApiRequestError as exc:
            raise ValueError(str(exc)) from exc

    async def hojin_search(
        self,
        corporate_number: str | None = None,
        name: str | None = None,
        exist_flg: str | None = None,
        corporate_type: str | None = None,
        prefecture: str | None = None,
        city: str | None = None,
        capital_stock_from: str | None = None,
        capital_stock_to: str | None = None,
        employee_number_from: str | None = None,
        employee_number_to: str | None = None,
        founded_year: str | None = None,
        net_sales_summary_of_business_results_from: str | None = None,
        net_sales_summary_of_business_results_to: str | None = None,
        total_assets_summary_of_business_results_from: str | None = None,
        total_assets_summary_of_business_results_to: str | None = None,
        average_continuous_service_years: str | None = None,
        average_age: str | None = None,
        month_average_predetermined_overtime_hours: str | None = None,
        female_workers_proportion: str | None = None,
        patent: str | None = None,
        procurement: str | None = None,
        procurement_amount_from: str | None = None,
        procurement_amount_to: str | None = None,
        subsidy: str | None = None,
        subsidy_amount_from: str | None = None,
        subsidy_amount_to: str | None = None,
        certification: str | None = None,
        ministry: str | None = None,
        source: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        if corporate_number is not None:
            ensure_corporate_number(corporate_number)
        ensure_page(page)
        ensure_limit(limit)
        ensure_metadata_flag(metadata_flg)

        query = _to_query(
            {
                "corporate_number": corporate_number,
                "name": name,
                "exist_flg": exist_flg,
                "corporate_type": corporate_type,
                "prefecture": prefecture,
                "city": city,
                "capital_stock_from": capital_stock_from,
                "capital_stock_to": capital_stock_to,
                "employee_number_from": employee_number_from,
                "employee_number_to": employee_number_to,
                "founded_year": founded_year,
                "net_sales_summary_of_business_results_from": (
                    net_sales_summary_of_business_results_from
                ),
                "net_sales_summary_of_business_results_to": (
                    net_sales_summary_of_business_results_to
                ),
                "total_assets_summary_of_business_results_from": (
                    total_assets_summary_of_business_results_from
                ),
                "total_assets_summary_of_business_results_to": (
                    total_assets_summary_of_business_results_to
                ),
                "average_continuous_service_years": average_continuous_service_years,
                "average_age": average_age,
                "month_average_predetermined_overtime_hours": (
                    month_average_predetermined_overtime_hours
                ),
                "female_workers_proportion": female_workers_proportion,
                "patent": patent,
                "procurement": procurement,
                "procurement_amount_from": procurement_amount_from,
                "procurement_amount_to": procurement_amount_to,
                "subsidy": subsidy,
                "subsidy_amount_from": subsidy_amount_from,
                "subsidy_amount_to": subsidy_amount_to,
                "certification": certification,
                "ministry": ministry,
                "source": source,
                "page": page,
                "limit": limit,
                "metadata_flg": metadata_flg,
            }
        )
        return await self._execute("/v2/hojin", query=query)

    async def _call_update_info(
        self,
        path: str,
        *,
        from_date: str,
        to_date: str,
        page: int | None,
        metadata_flg: bool | None,
    ) -> dict[str, Any]:
        ensure_yyyymmdd(from_date, field_name="from_date")
        ensure_yyyymmdd(to_date, field_name="to_date")
        ensure_from_to_range(from_date, to_date)
        ensure_page(page)
        ensure_metadata_flag(metadata_flg)
        query = _to_query(
            {
                "from": from_date,
                "to": to_date,
                "page": page,
                "metadata_flg": metadata_flg,
            }
        )
        return await self._execute(path, query=query)

    async def _call_get_info(
        self,
        path: str,
        *,
        corporate_number: str,
        metadata_flg: bool | None,
    ) -> dict[str, Any]:
        ensure_corporate_number(corporate_number)
        ensure_metadata_flag(metadata_flg)
        query = _to_query({"metadata_flg": metadata_flg})
        return await self._execute(
            path,
            query=query,
            path_params={"corporate_number": corporate_number},
        )

    async def hojin_update_info_basic(
        self,
        from_date: str,
        to_date: str,
        page: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await self._call_update_info(
            "/v2/hojin/updateInfo",
            from_date=from_date,
            to_date=to_date,
            page=page,
            metadata_flg=metadata_flg,
        )

    async def hojin_update_info_certification(
        self,
        from_date: str,
        to_date: str,
        page: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await self._call_update_info(
            "/v2/hojin/updateInfo/certification",
            from_date=from_date,
            to_date=to_date,
            page=page,
            metadata_flg=metadata_flg,
        )

    async def hojin_update_info_commendation(
        self,
        from_date: str,
        to_date: str,
        page: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await self._call_update_info(
            "/v2/hojin/updateInfo/commendation",
            from_date=from_date,
            to_date=to_date,
            page=page,
            metadata_flg=metadata_flg,
        )

    async def hojin_update_info_corporation(
        self,
        from_date: str,
        to_date: str,
        page: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await self._call_update_info(
            "/v2/hojin/updateInfo/corporation",
            from_date=from_date,
            to_date=to_date,
            page=page,
            metadata_flg=metadata_flg,
        )

    async def hojin_update_info_finance(
        self,
        from_date: str,
        to_date: str,
        page: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await self._call_update_info(
            "/v2/hojin/updateInfo/finance",
            from_date=from_date,
            to_date=to_date,
            page=page,
            metadata_flg=metadata_flg,
        )

    async def hojin_update_info_patent(
        self,
        from_date: str,
        to_date: str,
        page: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await self._call_update_info(
            "/v2/hojin/updateInfo/patent",
            from_date=from_date,
            to_date=to_date,
            page=page,
            metadata_flg=metadata_flg,
        )

    async def hojin_update_info_procurement(
        self,
        from_date: str,
        to_date: str,
        page: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await self._call_update_info(
            "/v2/hojin/updateInfo/procurement",
            from_date=from_date,
            to_date=to_date,
            page=page,
            metadata_flg=metadata_flg,
        )

    async def hojin_update_info_subsidy(
        self,
        from_date: str,
        to_date: str,
        page: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await self._call_update_info(
            "/v2/hojin/updateInfo/subsidy",
            from_date=from_date,
            to_date=to_date,
            page=page,
            metadata_flg=metadata_flg,
        )

    async def hojin_update_info_workplace(
        self,
        from_date: str,
        to_date: str,
        page: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await self._call_update_info(
            "/v2/hojin/updateInfo/workplace",
            from_date=from_date,
            to_date=to_date,
            page=page,
            metadata_flg=metadata_flg,
        )

    async def hojin_get_basic(
        self,
        corporate_number: str,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await self._call_get_info(
            "/v2/hojin/{corporate_number}",
            corporate_number=corporate_number,
            metadata_flg=metadata_flg,
        )

    async def hojin_get_certification(
        self,
        corporate_number: str,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await self._call_get_info(
            "/v2/hojin/{corporate_number}/certification",
            corporate_number=corporate_number,
            metadata_flg=metadata_flg,
        )

    async def hojin_get_commendation(
        self,
        corporate_number: str,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await self._call_get_info(
            "/v2/hojin/{corporate_number}/commendation",
            corporate_number=corporate_number,
            metadata_flg=metadata_flg,
        )

    async def hojin_get_corporation(
        self,
        corporate_number: str,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await self._call_get_info(
            "/v2/hojin/{corporate_number}/corporation",
            corporate_number=corporate_number,
            metadata_flg=metadata_flg,
        )

    async def hojin_get_finance(
        self,
        corporate_number: str,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await self._call_get_info(
            "/v2/hojin/{corporate_number}/finance",
            corporate_number=corporate_number,
            metadata_flg=metadata_flg,
        )

    async def hojin_get_patent(
        self,
        corporate_number: str,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await self._call_get_info(
            "/v2/hojin/{corporate_number}/patent",
            corporate_number=corporate_number,
            metadata_flg=metadata_flg,
        )

    async def hojin_get_procurement(
        self,
        corporate_number: str,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await self._call_get_info(
            "/v2/hojin/{corporate_number}/procurement",
            corporate_number=corporate_number,
            metadata_flg=metadata_flg,
        )

    async def hojin_get_subsidy(
        self,
        corporate_number: str,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await self._call_get_info(
            "/v2/hojin/{corporate_number}/subsidy",
            corporate_number=corporate_number,
            metadata_flg=metadata_flg,
        )

    async def hojin_get_workplace(
        self,
        corporate_number: str,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await self._call_get_info(
            "/v2/hojin/{corporate_number}/workplace",
            corporate_number=corporate_number,
            metadata_flg=metadata_flg,
        )


def create_server(settings: Settings | None = None) -> FastMCP:
    resolved_settings = settings or load_settings_from_env()
    mcp = FastMCP("gbizinfo-mcp")
    toolset = GbizInfoToolset(client=GbizInfoClient(resolved_settings))

    @mcp.tool()
    async def hojin_search(
        corporate_number: str | None = None,
        name: str | None = None,
        exist_flg: str | None = None,
        corporate_type: str | None = None,
        prefecture: str | None = None,
        city: str | None = None,
        capital_stock_from: str | None = None,
        capital_stock_to: str | None = None,
        employee_number_from: str | None = None,
        employee_number_to: str | None = None,
        founded_year: str | None = None,
        net_sales_summary_of_business_results_from: str | None = None,
        net_sales_summary_of_business_results_to: str | None = None,
        total_assets_summary_of_business_results_from: str | None = None,
        total_assets_summary_of_business_results_to: str | None = None,
        average_continuous_service_years: str | None = None,
        average_age: str | None = None,
        month_average_predetermined_overtime_hours: str | None = None,
        female_workers_proportion: str | None = None,
        patent: str | None = None,
        procurement: str | None = None,
        procurement_amount_from: str | None = None,
        procurement_amount_to: str | None = None,
        subsidy: str | None = None,
        subsidy_amount_from: str | None = None,
        subsidy_amount_to: str | None = None,
        certification: str | None = None,
        ministry: str | None = None,
        source: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_search(
            corporate_number=corporate_number,
            name=name,
            exist_flg=exist_flg,
            corporate_type=corporate_type,
            prefecture=prefecture,
            city=city,
            capital_stock_from=capital_stock_from,
            capital_stock_to=capital_stock_to,
            employee_number_from=employee_number_from,
            employee_number_to=employee_number_to,
            founded_year=founded_year,
            net_sales_summary_of_business_results_from=(
                net_sales_summary_of_business_results_from
            ),
            net_sales_summary_of_business_results_to=(
                net_sales_summary_of_business_results_to
            ),
            total_assets_summary_of_business_results_from=(
                total_assets_summary_of_business_results_from
            ),
            total_assets_summary_of_business_results_to=(
                total_assets_summary_of_business_results_to
            ),
            average_continuous_service_years=average_continuous_service_years,
            average_age=average_age,
            month_average_predetermined_overtime_hours=(
                month_average_predetermined_overtime_hours
            ),
            female_workers_proportion=female_workers_proportion,
            patent=patent,
            procurement=procurement,
            procurement_amount_from=procurement_amount_from,
            procurement_amount_to=procurement_amount_to,
            subsidy=subsidy,
            subsidy_amount_from=subsidy_amount_from,
            subsidy_amount_to=subsidy_amount_to,
            certification=certification,
            ministry=ministry,
            source=source,
            page=page,
            limit=limit,
            metadata_flg=metadata_flg,
        )

    @mcp.tool()
    async def hojin_update_info_basic(
        from_date: str,
        to_date: str,
        page: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_update_info_basic(
            from_date=from_date,
            to_date=to_date,
            page=page,
            metadata_flg=metadata_flg,
        )

    @mcp.tool()
    async def hojin_update_info_certification(
        from_date: str,
        to_date: str,
        page: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_update_info_certification(
            from_date=from_date,
            to_date=to_date,
            page=page,
            metadata_flg=metadata_flg,
        )

    @mcp.tool()
    async def hojin_update_info_commendation(
        from_date: str,
        to_date: str,
        page: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_update_info_commendation(
            from_date=from_date,
            to_date=to_date,
            page=page,
            metadata_flg=metadata_flg,
        )

    @mcp.tool()
    async def hojin_update_info_corporation(
        from_date: str,
        to_date: str,
        page: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_update_info_corporation(
            from_date=from_date,
            to_date=to_date,
            page=page,
            metadata_flg=metadata_flg,
        )

    @mcp.tool()
    async def hojin_update_info_finance(
        from_date: str,
        to_date: str,
        page: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_update_info_finance(
            from_date=from_date,
            to_date=to_date,
            page=page,
            metadata_flg=metadata_flg,
        )

    @mcp.tool()
    async def hojin_update_info_patent(
        from_date: str,
        to_date: str,
        page: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_update_info_patent(
            from_date=from_date,
            to_date=to_date,
            page=page,
            metadata_flg=metadata_flg,
        )

    @mcp.tool()
    async def hojin_update_info_procurement(
        from_date: str,
        to_date: str,
        page: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_update_info_procurement(
            from_date=from_date,
            to_date=to_date,
            page=page,
            metadata_flg=metadata_flg,
        )

    @mcp.tool()
    async def hojin_update_info_subsidy(
        from_date: str,
        to_date: str,
        page: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_update_info_subsidy(
            from_date=from_date,
            to_date=to_date,
            page=page,
            metadata_flg=metadata_flg,
        )

    @mcp.tool()
    async def hojin_update_info_workplace(
        from_date: str,
        to_date: str,
        page: int | None = None,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_update_info_workplace(
            from_date=from_date,
            to_date=to_date,
            page=page,
            metadata_flg=metadata_flg,
        )

    @mcp.tool()
    async def hojin_get_basic(
        corporate_number: str,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_get_basic(
            corporate_number=corporate_number,
            metadata_flg=metadata_flg,
        )

    @mcp.tool()
    async def hojin_get_certification(
        corporate_number: str,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_get_certification(
            corporate_number=corporate_number,
            metadata_flg=metadata_flg,
        )

    @mcp.tool()
    async def hojin_get_commendation(
        corporate_number: str,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_get_commendation(
            corporate_number=corporate_number,
            metadata_flg=metadata_flg,
        )

    @mcp.tool()
    async def hojin_get_corporation(
        corporate_number: str,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_get_corporation(
            corporate_number=corporate_number,
            metadata_flg=metadata_flg,
        )

    @mcp.tool()
    async def hojin_get_finance(
        corporate_number: str,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_get_finance(
            corporate_number=corporate_number,
            metadata_flg=metadata_flg,
        )

    @mcp.tool()
    async def hojin_get_patent(
        corporate_number: str,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_get_patent(
            corporate_number=corporate_number,
            metadata_flg=metadata_flg,
        )

    @mcp.tool()
    async def hojin_get_procurement(
        corporate_number: str,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_get_procurement(
            corporate_number=corporate_number,
            metadata_flg=metadata_flg,
        )

    @mcp.tool()
    async def hojin_get_subsidy(
        corporate_number: str,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_get_subsidy(
            corporate_number=corporate_number,
            metadata_flg=metadata_flg,
        )

    @mcp.tool()
    async def hojin_get_workplace(
        corporate_number: str,
        metadata_flg: bool | None = None,
    ) -> dict[str, Any]:
        return await toolset.hojin_get_workplace(
            corporate_number=corporate_number,
            metadata_flg=metadata_flg,
        )

    return mcp
