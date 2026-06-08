import random


def select_products_for_bundle(ctx, bundle_type, allowed_categories, buy_quantity):
    """
    Select products for bundle generation.

    Rules:
    - Set bundles span multiple categories
    - Other bundle types use a single category
    - Quantity logic depends on promotion type
    """
    products_df = ctx.products.products_df

    selected_products = []
    selected_categories = []

    if bundle_type == "Set":
        for category in allowed_categories:
            category_products = products_df.loc[
                products_df["category"] == category, "product_id"
            ].tolist()
            if category_products:
                product_id = random.choice(category_products)
                qty = random.randint(1, 3)
                selected_products.append((product_id, qty))
                selected_categories.append(category)

    else:  # BOGO, 2 for X, buy N save X
        category = allowed_categories[0]
        category_products = products_df.loc[
            products_df["category"] == category, "product_id"
        ].tolist()
        if category_products:
            product_id = random.choice(category_products)
            selected_products.append((product_id, buy_quantity))
            selected_categories.append(category)

    return selected_products, selected_categories
