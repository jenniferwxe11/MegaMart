# dirty_data_generation/generators/transactions_dirty.py

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.corruption_rules.transaction_items_rules import (
    duplicate_product_in_transaction,
    final_item_price_reconciliation_error,
    invalid_final_item_price,
    invalid_item_discount,
    invalid_item_subtotal,
    invalid_quantity,
    invalid_unit_price,
    item_discount_exceeds_subtotal,
    item_subtotal_calculation_error,
    missing_category,
    missing_final_item_price,
    missing_item_discount,
    missing_item_subtotal,
    missing_product_id,
    missing_product_name,
    missing_quantity,
)
from dirty_data_generation.corruption_rules.transaction_items_rules import (
    missing_transaction_id as missing_transaction_item_id,
)
from dirty_data_generation.corruption_rules.transaction_items_rules import (
    missing_unit_price,
    orphaned_transaction_item,
    product_information_mismatch,
)
from dirty_data_generation.corruption_rules.transactions_rules import (
    applied_promotion_type_mismatch,
    applied_promotions_discount_mismatch,
    basket_size_mismatch,
    duplicate_applied_promotion,
    duplicate_transaction,
    duplicate_transaction_id,
    future_transaction_time,
    invalid_applied_promotion_amount,
    invalid_basket_size,
    invalid_cart_subtotal,
    invalid_num_unique_items,
    invalid_payment_method,
    invalid_shipping_discount,
    invalid_shipping_fee,
    invalid_total_discount,
    invalid_transaction_id_format,
    invalid_transaction_total,
    missing_applied_promotion_amount,
    missing_applied_promotion_id,
    missing_applied_promotion_type,
    missing_basket_size,
    missing_cart_subtotal,
    missing_customer_id,
    missing_num_unique_items,
    missing_payment_method,
    missing_shipping_discount,
    missing_shipping_fee,
    missing_store_id,
    missing_total_discount,
    missing_transaction_id,
    missing_transaction_time,
    missing_transaction_total,
    num_unique_items_mismatch,
    shipping_discount_not_equal_fee,
    shipping_discount_without_fee,
    total_discount_exceeds_subtotal,
    transaction_discount_mismatch,
    transaction_total_reconciliation_error,
    transaction_without_items,
    unique_items_exceed_basket_size,
)
from dirty_data_generation.helpers.dirty_utils import apply_corruption
from dirty_data_generation.registry import register
from dirty_data_generation.utils.io_utils import save

TRANSACTIONS_RULES = [
    # Missing Values
    (0.03, missing_transaction_id),
    (0.03, missing_customer_id),
    (0.03, missing_store_id),
    (0.03, missing_transaction_time),
    (0.03, missing_cart_subtotal),
    (0.03, missing_total_discount),
    (0.03, missing_shipping_fee),
    (0.03, missing_shipping_discount),
    (0.03, missing_transaction_total),
    (0.03, missing_payment_method),
    (0.03, missing_basket_size),
    (0.03, missing_num_unique_items),
    # Formatting
    (0.02, invalid_transaction_id_format),
    # Range Validation
    (0.02, invalid_cart_subtotal),
    (0.02, invalid_total_discount),
    (0.02, invalid_shipping_fee),
    (0.02, invalid_shipping_discount),
    (0.02, invalid_transaction_total),
    (0.02, invalid_basket_size),
    (0.02, invalid_num_unique_items),
    # Data Quality
    (0.02, invalid_payment_method),
    # Date Issues
    (0.02, future_transaction_time),
    # Business Rule Violations
    (0.02, duplicate_transaction_id),
    (0.02, duplicate_transaction),
    (0.02, transaction_without_items),
    (0.02, basket_size_mismatch),
    (0.02, num_unique_items_mismatch),
    (0.02, transaction_discount_mismatch),
    (0.02, total_discount_exceeds_subtotal),
    (0.02, shipping_discount_without_fee),
    (0.02, shipping_discount_not_equal_fee),
    (0.02, applied_promotions_discount_mismatch),
    (0.02, transaction_total_reconciliation_error),
    (0.02, unique_items_exceed_basket_size),
    # Applied Promotions
    (0.03, missing_applied_promotion_id),
    (0.03, missing_applied_promotion_type),
    (0.03, missing_applied_promotion_amount),
    (0.02, invalid_applied_promotion_amount),
    (0.02, duplicate_applied_promotion),
    (0.02, applied_promotion_type_mismatch),
]


TRANSACTION_ITEMS_RULES = [
    # Missing Values
    (0.03, missing_transaction_item_id),
    (0.03, missing_product_id),
    (0.03, missing_product_name),
    (0.03, missing_category),
    (0.03, missing_quantity),
    (0.03, missing_unit_price),
    (0.03, missing_item_subtotal),
    (0.03, missing_item_discount),
    (0.03, missing_final_item_price),
    # Range Validation
    (0.02, invalid_quantity),
    (0.02, invalid_unit_price),
    (0.02, invalid_item_subtotal),
    (0.02, invalid_item_discount),
    (0.02, invalid_final_item_price),
    # Business Rule Violations
    (0.02, duplicate_product_in_transaction),
    (0.02, item_subtotal_calculation_error),
    (0.02, item_discount_exceeds_subtotal),
    (0.02, final_item_price_reconciliation_error),
    (0.02, product_information_mismatch),
    (0.02, orphaned_transaction_item),
]


@register("dirty_transactions")
def dirty_transactions(ctx: GenerationContext):

    df = ctx.transactions.transactions_df.copy()

    for rate, rule in TRANSACTIONS_RULES:
        apply_corruption(
            df=df,
            rate=rate,
            corruption=rule,
            ctx=ctx,
        )

    return save(df, "transactions_dirty.csv")


@register("dirty_transaction_items")
def dirty_transaction_items(ctx: GenerationContext):

    df = ctx.transactions.transaction_items_df.copy()

    for rate, rule in TRANSACTION_ITEMS_RULES:
        apply_corruption(
            df=df,
            rate=rate,
            corruption=rule,
            ctx=ctx,
        )

    return save(df, "transaction_items_dirty.csv")
