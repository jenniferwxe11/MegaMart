from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd


@dataclass(frozen=True)
class AppConfig:
    DATA_START_DATE: pd.Timestamp
    DATA_END_DATE: pd.Timestamp
    SIMULATION_DATE: pd.Timestamp


@dataclass(frozen=True)
class RegionAreaContext:
    area_region_map: Dict[str, str]
    areas: List[str]
    regions: List[str]


@dataclass(frozen=True)
class ReferenceDataContext:
    search_terms: list[str]


@dataclass(frozen=True)
class CustomerContext:
    customers_df: pd.DataFrame
    customer_ids: List[str]
    customer_type_to_ids_map: Dict[str, List[str]]
    customer_type_map: Dict[str, str]
    customer_segment_map: Dict[str, str]
    customer_area_map: Dict[str, str]
    customer_region_map: Dict[str, str]


@dataclass(frozen=True)
class StoreContext:
    stores_df: pd.DataFrame
    store_ids: List[str]
    store_area_map: Dict[str, str]
    store_region_map: Dict[str, str]
    online_store_id: str
    retail_store_ids: List[str]


@dataclass(frozen=True)
class ProductContext:
    products_df: pd.DataFrame
    product_ids: List[str]
    essential_product_ids: List[str]
    non_essential_product_ids: List[str]
    product_map: Dict[str, Dict]
    product_name_map: Dict[str, str]
    product_price_map: Dict[str, float]
    product_category_map: Dict[str, str]
    product_cost_map: Dict[str, float]
    category_to_products: Dict[str, List[str]]


@dataclass(frozen=True)
class StoreCatalogueContext:
    store_catalogues_df: pd.DataFrame
    store_product_price_map: Dict[Tuple[str, str], float]
    store_product_name_map: Dict[Tuple[str, str], str]
    store_product_category_map: Dict[Tuple[str, str], str]


@dataclass(frozen=True)
class ProductLifecycleContext:
    product_lifecycles_df: pd.DataFrame
    product_discontinuation_map: Dict[str, datetime]
    product_launch_map: Dict[str, datetime]
    product_with_lifecycle_df: pd.DataFrame


@dataclass(frozen=True)
class ProductContentQualityContext:
    product_content_quality_df: pd.DataFrame


@dataclass(frozen=True)
class StockoutEventContext:
    stockout_events_df: pd.DataFrame
    stockout_event_map: dict[tuple[str, str], pd.DataFrame]


@dataclass(frozen=True)
class StockSnapshotContext:
    stock_snapshots_df: pd.DataFrame


@dataclass(frozen=True)
class CompetitorProductContext:
    competitor_products_df: pd.DataFrame
    competitor_price_history_df: pd.DataFrame


@dataclass(frozen=True)
class CampaignContext:
    campaigns_df: pd.DataFrame


@dataclass(frozen=True)
class CampaignAssignmentContext:
    campaign_assignments_df: pd.DataFrame
    campaign_exposures_df: pd.DataFrame


@dataclass(frozen=True)
class BundleContext:
    bundle_items_df: pd.DataFrame
    bundle_pricings_df: pd.DataFrame
    bundles_df: pd.DataFrame
    bundle_dict: Dict[str, List[str]]
    bundle_full_df: pd.DataFrame


@dataclass(frozen=True)
class PromotionContext:
    promotions_df: pd.DataFrame


@dataclass(frozen=True)
class ClickstreamContext:
    clickstreams_df: pd.DataFrame
    payment_success: pd.DataFrame


@dataclass(frozen=True)
class TransactionContext:
    transactions_df: pd.DataFrame
    transaction_items_df: pd.DataFrame
    valid_transactions: pd.DataFrame


@dataclass(frozen=True)
class ProductReviewContext:
    product_reviews_df: pd.DataFrame


@dataclass
class GenerationContext:
    config: AppConfig
    region_areas: RegionAreaContext
    reference_data: ReferenceDataContext
    customers: CustomerContext
    stores: StoreContext
    products: ProductContext
    store_catalogues: Optional[StoreCatalogueContext] = None
    product_lifecycles: Optional[ProductLifecycleContext] = None
    product_content_quality: Optional[ProductContentQualityContext] = None
    stockout_events: Optional[StockoutEventContext] = None
    stock_snapshots: Optional[StockSnapshotContext] = None
    competitor_products: Optional[CompetitorProductContext] = None
    campaigns: Optional[CampaignContext] = None
    campaign_assignments: Optional[CampaignAssignmentContext] = None
    bundles: Optional[BundleContext] = None
    promotions: Optional[PromotionContext] = None
    clickstreams: Optional[ClickstreamContext] = None
    transactions: Optional[TransactionContext] = None
    product_reviews: Optional[ProductReviewContext] = None
