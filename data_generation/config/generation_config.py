DEV_MODE = True
TEST_MODE = False
PROD_MODE = False

if DEV_MODE:

    NUM_CUSTOMERS = 50
    NUM_STORES = 5
    NUM_PRODUCTS = 80
    NUM_CAMPAIGNS = 20
    NUM_BUNDLES = 20
    NUM_CLICKSTREAM_SESSIONS = 300
    NUM_TRANSACTIONS = 300

    # 5 stores × ~64 products each (80% overlap)
    LIMIT_STORE_CATALOGUES = 320

    # every product gets ~3 lifecycle events
    LIMIT_PRODUCT_LIFECYCLES = 240

    # every product gets ~3 content quality records
    LIMIT_PRODUCT_CONTENT_QUALITY = 240

    # ~32 stockout events per store
    LIMIT_STOCKOUT_EVENTS = 160

    # unchanged — already well-proportioned
    LIMIT_STOCK_SNAPSHOTS = 20000

    # 4 promos per campaign
    LIMIT_PROMOTIONS = 80

    # 50 customers × 30 campaign touches
    LIMIT_CAMPAIGN_ASSIGNMENTS = 1500

    # 3 exposures per assignment
    LIMIT_CAMPAIGN_EXPOSURES = 4500

    # 3 pricing periods per bundle
    LIMIT_BUNDLE_PRICINGS = 60

    # 3.5 items per bundle on average
    LIMIT_BUNDLE_ITEMS = 70

    # 20 events per session
    LIMIT_CLICKSTREAM_EVENTS = 6000

    # 6 items per transaction
    LIMIT_TRANSACTION_ITEMS = 1800

    # ~4 reviews per customer
    LIMIT_PRODUCT_REVIEWS = 200

    LIMIT_COMPETITOR_PRODUCTS = 350

    # 20 price updates per competitor product
    LIMIT_COMPETITOR_PRICE_HISTORY = 7000


if TEST_MODE:

    NUM_CUSTOMERS = 1000
    NUM_STORES = 50
    NUM_PRODUCTS = 800
    NUM_CAMPAIGNS = 500
    NUM_BUNDLES = 300
    NUM_CLICKSTREAM_SESSIONS = 20000
    NUM_TRANSACTIONS = 20000

    # 50 stores × 600 products each (75% overlap)
    LIMIT_STORE_CATALOGUES = 30000

    # every product gets ~5 lifecycle events
    LIMIT_PRODUCT_LIFECYCLES = 4000

    # every product gets ~5 content/quality versions
    LIMIT_PRODUCT_CONTENT_QUALITY = 4000

    # ~50 stockout events per store
    LIMIT_STOCKOUT_EVENTS = 2500

    # 50 stores × 800 products × ~6.5 active weeks sampled
    # (500k was a warehouse-lag culprit — cut to proportional)
    LIMIT_STOCK_SNAPSHOTS = 260000

    # 4 promos per campaign
    LIMIT_PROMOTIONS = 2000

    # 50 campaign touches per customer
    LIMIT_CAMPAIGN_ASSIGNMENTS = 50000

    # 3 exposures per assignment
    LIMIT_CAMPAIGN_EXPOSURES = 150000

    # 4 pricing periods per bundle
    LIMIT_BUNDLE_PRICINGS = 1200

    # 3.5 items per bundle
    LIMIT_BUNDLE_ITEMS = 1050

    # 30 events per session
    LIMIT_CLICKSTREAM_EVENTS = 600000

    # 6 items per transaction
    LIMIT_TRANSACTION_ITEMS = 120000

    # ~15 reviews per customer (was 5 — too sparse for user-level analysis)
    LIMIT_PRODUCT_REVIEWS = 15000

    LIMIT_COMPETITOR_PRODUCTS = 10000

    # 20 price updates per competitor product
    # (500k was a warehouse-lag culprit — halved)
    LIMIT_COMPETITOR_PRICE_HISTORY = 200000

if PROD_MODE:

    NUM_CUSTOMERS = 100000
    NUM_STORES = 120
    NUM_PRODUCTS = 15000

    # assortment differs heavily by store format
    LIMIT_STORE_CATALOGUES = 1200000

    # historical lifecycle state changes
    LIMIT_PRODUCT_LIFECYCLES = 200000

    # ongoing enrichment/versioning
    LIMIT_PRODUCT_CONTENT_QUALITY = 100000

    # operational disruptions
    LIMIT_STOCKOUT_EVENTS = 500000

    # extremely large time-series table
    LIMIT_STOCK_SNAPSHOTS = 50000000

    NUM_CAMPAIGNS = 10000

    # constant overlapping promotions
    LIMIT_PROMOTIONS = 100000

    # repeated targeting across years
    LIMIT_CAMPAIGN_ASSIGNMENTS = 10000000

    # opens/clicks/views/etc
    LIMIT_CAMPAIGN_EXPOSURES = 50000000

    NUM_BUNDLES = 10000

    LIMIT_BUNDLE_PRICINGS = 100000

    LIMIT_BUNDLE_ITEMS = 50000

    # online traffic scales massively
    NUM_CLICKSTREAM_SESSIONS = 5000000

    # largest behavioral table
    LIMIT_CLICKSTREAM_EVENTS = 150000000

    # multi-year transaction scale
    NUM_TRANSACTIONS = 5000000

    # avg 5–7 items/cart
    LIMIT_TRANSACTION_ITEMS = 30000000

    # sparse relative to transactions
    LIMIT_PRODUCT_REVIEWS = 1000000

    # competitor ecosystem monitoring
    LIMIT_COMPETITOR_PRODUCTS = 100000

    # scheduled longitudinal tracking
    LIMIT_COMPETITOR_PRICE_HISTORY = 50000000
