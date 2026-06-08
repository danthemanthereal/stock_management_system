import json
import re
from collections import defaultdict
from typing import List, Optional, Tuple
import aiofiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.database.models import FinancialMetric


async def get_needed_metrics_map():
    considered_financial_metrics = ["revenue",
                                    "total_employee_number",
                                    "total_equity",
                                    "total_liabilities",
                                    "total_current_liabilities",
                                    "cash_and_cash_equivalents",
                                    "total_free_cash_flow",
                                    "total_current_assets",
                                    "total_non_current_assets",
                                    "total_assets",
                                    "good_will"]

    async with aiofiles.open(
            "/Users/danielschmidt/Desktop/stock_management_system/Stock_management_fast_api/src/financial_metric_analysis_component/current_financial_metrics_guro_focus.json") as financial_metrics_file:
        metrics = await financial_metrics_file.read()
        financial_metrics = json.loads(metrics)

    annuals = financial_metrics.get("annual", [])

    needed_financial_metrics_map = {}

    for current_year_map in annuals:
        for key, value in current_year_map.items():
            if key not in considered_financial_metrics:
                continue

            needed_financial_metrics_map.setdefault(key, []).append(value)
    return needed_financial_metrics_map


def get_key_metrics_from_fmp() -> list[str]:
    return [
        "capexToDepreciation",
        "salesGeneralAndAdministrativeToRevenue",
        "researchAndDevelopementToRevenue",
        "intangiblesToTotalAssets",
        "daysOfPayablesOutstanding",
        "daysOfInventoryOutstanding",
        "freeCashFlowToEquity",
        "freeCashFlowToFirm",
        "netDebtToEBITDA"
    ]


def get_ratio_metrics_of_fmp() -> list[str]:
    return [
        "ebitMargin",
        "operatingProfitMargin",
        "pretaxProfitMargin",
        "netProfitMargin",
        "payablesTurnover",
        "fixedAssetTurnover",
        "solvencyRatio",
        "priceToEarningsRatio",
        "priceToEarningsGrowthRatio",
        "forwardPriceToEarningsGrowthRatio",
        "priceToBookRatio",
        "priceToSalesRatio",
        "priceToFreeCashFlowRatio",
        "priceToOperatingCashFlowRatio",
        "debtToAssetsRatio",
        "debtToEquityRatio",
        "debtToCapitalRatio",
        "longTermDebtToCapitalRatio",
        "financialLeverageRatio",
        "workingCapitalTurnoverRatio",
        "operatingCashFlowRatio",
        "operatingCashFlowSalesRatio",
        "freeCashFlowOperatingCashFlowRatio",
        "debtServiceCoverageRatio",
        "interestCoverageRatio",
        "shortTermOperatingCashFlowCoverageRatio",
        "operatingCashFlowCoverageRatio",
        "capitalExpenditureCoverageRatio",
        "dividendPaidAndCapexCoverageRatio"]


def add_to_metric_map_current_calculation(
        revenue_last_for_years: list,
        total_employee_number_last_four_years: list,
        total_equity_last_four_years: list,
        total_liabilities_last_four_years: list,
        total_current_liabilities_last_four_years: list,
        cash_and_cash_equivalents_last_four_years: list,
        total_current_assets_last_four_years: list,
        total_non_current_assets_last_four_years: list,
        total_assets_last_four_years: list,
        good_will_last_four_years: list,
        financial_metric_map: dict,
        financial_metric_name: str,
):
    if financial_metric_name == "revenue_per_employee":
        financial_metric_map = calculate_revenue_per_employee(
            revenue_last_four_years=revenue_last_for_years,
            employee_amount_last_four_years=total_employee_number_last_four_years,
            financial_metric_map=financial_metric_map,
        )
        return financial_metric_map
    elif financial_metric_name == "gearing":
        financial_metric_map = calculate_gearing(
            company_equity_last_for_years=total_equity_last_four_years,
            total_liabilities_last_for_years=total_liabilities_last_four_years,
            cash_and_cash_equivalents_last_for_years=cash_and_cash_equivalents_last_four_years,
            financial_metric_map=financial_metric_map,
        )
        return financial_metric_map

    elif financial_metric_name == "dynamic debt degree":
        financial_metric_map = calculate_dynamic_debt_degree(
            company_equity_last_for_years=total_equity_last_four_years,
            total_liabilities_last_for_years=total_liabilities_last_four_years,
            cash_and_cash_equivalents_last_for_years=cash_and_cash_equivalents_last_four_years,
            financial_metric_map=financial_metric_map,
        )
        return financial_metric_map

    elif financial_metric_name == "current_asset_intensity":
        financial_metric_map = calculate_current_asset_intensity(
            total_assets_last_four_years=total_assets_last_four_years,
            total_current_assets_last_four_years=total_current_assets_last_four_years,
            financial_metric_map=financial_metric_map,
        )
        return financial_metric_map
    elif financial_metric_name == "non_current_asset_intensity":
        financial_metric_map = calculate_non_current_asset_intensity(
            total_assets_last_four_years=total_assets_last_four_years,
            total_non_current_assets_last_four_years=total_non_current_assets_last_four_years,
            financial_metric_map=financial_metric_map,
        )
        return financial_metric_map
    elif financial_metric_name == "asset_cover_ratio_one":
        financial_metric_map = calculate_asset_coverage_ratio_one(
            company_equity_last_four_years=total_equity_last_four_years,
            total_assets_last_four_years=total_assets_last_four_years,
            financial_metric_map=financial_metric_map,
        )
        return financial_metric_map
    elif financial_metric_name == "asset_cover_ratio_two":
        financial_metric_map = calculate_asset_coverage_ratio_two(
            company_equity_last_four_years=total_equity_last_four_years,
            total_assets_last_four_years=total_assets_last_four_years,
            total_liabilities_last_four_years=total_liabilities_last_four_years,
            total_current_liabilities_last_for_years=total_current_liabilities_last_four_years,
            financial_metric_map=financial_metric_map,
        )
        return financial_metric_map
    elif financial_metric_name == "good_will_ratio":
        financial_metric_map = calculate_good_will_ratio(
            company_equity_last_four_years=total_equity_last_four_years,
            total_goodwill_last_four_years=good_will_last_four_years,
            financial_metric_map=financial_metric_map,
        )
        return financial_metric_map
    else:
        return financial_metric_map



def calculate_revenue_per_employee(revenue_last_four_years, employee_amount_last_four_years, financial_metric_map):
    for idx, employee_number in enumerate(employee_amount_last_four_years):
        revenue = revenue_last_four_years[idx]
        value = revenue / employee_number
        financial_metric_map.setdefault("revenue_per_employee", []).append(value)
    return financial_metric_map


def calculate_gearing(company_equity_last_for_years,
                      total_liabilities_last_for_years,
                      cash_and_cash_equivalents_last_for_years,
                      financial_metric_map
                      ):
    for idx, current_equity_in_year in enumerate(company_equity_last_for_years):
        current_total_liability = total_liabilities_last_for_years[idx]
        current_cash_and_cash_equivalent = cash_and_cash_equivalents_last_for_years[idx]
        net_debt = current_total_liability - current_cash_and_cash_equivalent
        value = net_debt / current_equity_in_year
        financial_metric_map.setdefault("gearing", []).append(value)
    return financial_metric_map


def calculate_dynamic_debt_degree(company_equity_last_for_years,
                                  total_liabilities_last_for_years,
                                  cash_and_cash_equivalents_last_for_years,
                                  financial_metric_map):
    for idx, current_equity_in_year in enumerate(company_equity_last_for_years):
        current_total_liability = total_liabilities_last_for_years[idx]
        current_cash_and_cash_equivalent = cash_and_cash_equivalents_last_for_years[idx]
        net_debt = current_total_liability - current_cash_and_cash_equivalent
        value = net_debt / current_equity_in_year
        financial_metric_map.setdefault("dynamic debt degree", []).append(value)

    return financial_metric_map


def calculate_current_asset_intensity(total_assets_last_four_years,
                                      total_current_assets_last_four_years,
                                      financial_metric_map):
    for idx, current_total_asset in enumerate(total_assets_last_four_years):
        current_current_asset = total_current_assets_last_four_years[idx]
        value = current_current_asset / current_total_asset
        financial_metric_map.setdefault("current_asset_intensity", []).append(value)
    return financial_metric_map


def calculate_non_current_asset_intensity(total_assets_last_four_years,
                                          total_non_current_assets_last_four_years,
                                          financial_metric_map):
    for idx, current_total_asset in enumerate(total_assets_last_four_years):
        current_non_current_asset = total_non_current_assets_last_four_years[idx]
        value = current_non_current_asset / current_total_asset
        financial_metric_map.setdefault("non_current_asset_intensity", []).append(value)
    return financial_metric_map


def calculate_asset_coverage_ratio_one(company_equity_last_four_years,
                                       total_assets_last_four_years,
                                       financial_metric_map):
    for idx, current_equity_in_year in enumerate(company_equity_last_four_years):
        current_total_asset = total_assets_last_four_years[idx]
        value = current_equity_in_year / current_total_asset
        financial_metric_map.setdefault("asset_cover_ratio_one", []).append(value)
    return financial_metric_map


def calculate_asset_coverage_ratio_two(company_equity_last_four_years,
                                       total_assets_last_four_years,
                                       total_liabilities_last_four_years,
                                       total_current_liabilities_last_for_years,
                                       financial_metric_map):
    for idx, current_equity_in_year in enumerate(company_equity_last_four_years):
        current_total_asset = total_assets_last_four_years[idx]
        current_long_term_liabilities = total_liabilities_last_four_years[idx] - \
                                        total_current_liabilities_last_for_years[idx]
        value = (current_equity_in_year + current_long_term_liabilities) / current_total_asset
        financial_metric_map.setdefault("asset_cover_ratio_two", []).append(value)
    return financial_metric_map


def calculate_good_will_ratio(
        company_equity_last_four_years,
        total_goodwill_last_four_years,
        financial_metric_map):
    for idx, current_equity_in_year in enumerate(company_equity_last_four_years):
        current_good_will = total_goodwill_last_four_years[idx]
        value = current_good_will / current_equity_in_year
        financial_metric_map.setdefault("good_will_ratio", []).append(value)
    return financial_metric_map


async def group_financial_metrics_map_by_category(
            financial_metrics_map: dict,
            db: AsyncSession,
    ) -> List[dict]:
        try:
            if not financial_metrics_map:
                return []
            metric_names = list(financial_metrics_map.keys())
            stmt = (
                select(FinancialMetric)
                .options(joinedload(FinancialMetric.category_rel))
                .where(FinancialMetric.name.in_(metric_names))
            )

            result = await db.execute(stmt)
            rows = result.scalars().all()
            name_to_category = {
                r.name: r.category_name for r in rows
            }
            groups: dict[str, dict] = defaultdict(dict)
            for name, values in financial_metrics_map.items():
                cat_key = name_to_category.get(name, "")
                groups[cat_key][name] = values
            ordered_keys = sorted(
                groups.keys(),
                key=lambda k: (1 if k == "" else 0, k.casefold()),
            )
            out: List[dict] = []
            for k in ordered_keys:
                inner = groups[k]
                sorted_metrics = {
                    n: inner[n] for n in sorted(inner.keys(), key=str.casefold)
                }
                out.append(
                    {
                        "category": k if k else "Ohne Kategorie",
                        "metrics": sorted_metrics,
                    }
                )
            return out
        except Exception as e:
            return []


async def group_metric_names_by_category(
            metric_names: List[str],
            db: AsyncSession,
    ) -> List[Tuple[str, List[str]]]:
        try:
            if not metric_names:
                return []
            names = list(metric_names)
            stmt = (
                select(FinancialMetric)
                .options(joinedload(FinancialMetric.category_rel))
                .where(FinancialMetric.name.in_(set(names)))
            )

            result = await db.execute(stmt)
            rows = list(result.scalars().all())
            name_to_category = {
                r.name: r.category_name for r in rows
            }
            groups: dict[str, List[str]] = defaultdict(list)
            for n in names:
                cat = name_to_category.get(n, "")
                groups[cat].append(n)
            for k in groups:
                groups[k].sort(key=str.casefold)
            ordered_keys = sorted(
                groups.keys(),
                key=lambda k: (1 if k == "" else 0, k.casefold()),
            )
            return [(k if k else "Ohne Kategorie", groups[k]) for k in ordered_keys]
        except Exception as e:
            return []

def merge_financial_summary_triples(
            combined: List[dict],
            benchmark: List[dict],
            development: List[dict],
    ) -> List[dict]:
        def to_map(rows: List[dict]) -> dict:
            return {r["category"]: dict(r) for r in rows}

        def enrich(row: Optional[dict]) -> dict:
            base = {"satisfied": 0, "unsatisfied": 0, "total": 0}
            if row:
                base.update(
                    {
                        "satisfied": int(row.get("satisfied", 0)),
                        "unsatisfied": int(row.get("unsatisfied", 0)),
                        "total": int(row.get("total", 0)),
                    }
                )
            t = base["total"]
            s, u = base["satisfied"], base["unsatisfied"]
            base["satisfied_pct"] = round(100.0 * s / t, 1) if t else None
            base["unsatisfied_pct"] = round(100.0 * u / t, 1) if t else None
            return base

        c_map = to_map(combined)
        b_map = to_map(benchmark)
        d_map = to_map(development)
        all_labels = set(c_map) | set(b_map) | set(d_map)
        ordered = sorted(
            all_labels,
            key=lambda L: (1 if L == "Ohne Kategorie" else 0, L.casefold()),
        )
        out: List[dict] = []
        for L in ordered:
            out.append(
                {
                    "category": L,
                    "combined": enrich(c_map.get(L)),
                    "benchmark": enrich(b_map.get(L)),
                    "development": enrich(d_map.get(L)),
                }
            )
        return out

def build_category_pair_summary(
            satisfied_by_category: List[Tuple[str, List[str]]],
            unsatisfied_by_category: List[Tuple[str, List[str]]],
    ) -> List[dict]:
        try:
            sat_map = {label: len(names) for label, names in satisfied_by_category}
            unsat_map = {label: len(names) for label, names in unsatisfied_by_category}
            all_labels = set(sat_map) | set(unsat_map)
            ordered = sorted(
                all_labels,
                key=lambda L: (1 if L == "Ohne Kategorie" else 0, L.casefold()),
            )
            rows: List[dict] = []
            for L in ordered:
                s = sat_map.get(L, 0)
                u = unsat_map.get(L, 0)
                rows.append(
                    {
                        "category": L,
                        "satisfied": s,
                        "unsatisfied": u,
                        "total": s + u,
                    }
                )
            return rows
        except Exception as e:
            return []


def metric_ids_for_branch_profile_from_form(form) -> List[int]:
        hidden = form.get("profile_selected_metric_ids")
        if hidden is not None and str(hidden).strip():
            parts = [x.strip() for x in str(hidden).split(",") if x.strip()]
            try:
                return sorted({int(x) for x in parts})
            except ValueError:
                pass
        listed = form.getlist("metric_ids")
        if listed:
            try:
                return sorted({int(x) for x in listed})
            except ValueError:
                pass
        found = set()
        for key, _ in form.multi_items():
            m = re.match(r"^is_active_(\d+)$", str(key))
            if m:
                found.add(int(m.group(1)))
        return sorted(found)


def group_financial_metrics_by_category(
            metrics: List[FinancialMetric],
    ) -> List[Tuple[str, List[FinancialMetric]]]:
        try:
            groups: dict[str, List[FinancialMetric]] = defaultdict(list)
            for m in metrics:
                raw = m.category_name
                key = raw if raw else ""
                groups[key].append(m)
            ordered_keys = sorted(
                groups.keys(),
                key=lambda k: (1 if k == "" else 0, k.casefold()),
            )
            return [
                (
                    k if k else "Ohne Kategorie",
                    sorted(groups[k], key=lambda m: (m.name or "").casefold()),
                )
                for k in ordered_keys
            ]
        except Exception as e:
            return []
