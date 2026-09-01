{% test bundle_item_quantity_matches_type(model, bundle_model) %}

select
    bi.bundle_id,
    b.bundle_type,
    bi.product_id,
    bi.quantity

from {{ model }} bi

join {{ bundle_model }} b
    on bi.bundle_id = b.bundle_id

where
    (
        b.bundle_type in ('Buy One, Get One', '2 For X')
        and bi.quantity != 2
    )

    or

    (
        b.bundle_type = 'Buy N Save X'
        and bi.quantity != cast(
            regexp_extract(b.bundle_name, r'Buy ([0-9]+)') as int64
        )
    )

{% endtest %}
