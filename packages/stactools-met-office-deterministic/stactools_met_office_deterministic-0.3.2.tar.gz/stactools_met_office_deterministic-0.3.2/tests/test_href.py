from stactools.met_office_deterministic.href import Href


def test_hrefs(hrefs: list[str]) -> None:
    for raw_href in hrefs:
        href = Href.parse(raw_href)
        href.item_id.startswith("20250614T")
