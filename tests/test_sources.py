from app.services.sources import canonical_source


def test_canonical_source_groups_storefronts():
    assert canonical_source("Amazon.com") == "Amazon"
    assert canonical_source("Walmart - VEATOOL") == "Walmart"
    assert canonical_source("eBay - anker_outlet_store") == "eBay"
    assert canonical_source("Best Buy") == "Best Buy"
    assert canonical_source("Micro Center") == "其他"
