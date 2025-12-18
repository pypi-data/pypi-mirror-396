import pytest
from requests.exceptions import ProxyError

from altimetry_downloader_aviso.catalog_client.geonetwork.models.model import (
    AvisoProduct,
)
from altimetry_downloader_aviso.catalog_client.granule_discoverer import (
    ProductLayoutConfig,
    TDSIterable,
    _load_convention_layout,
    _parse_tds_layout,
    filter_granules,
)


class Test_TDSIterable:

    @pytest.mark.parametrize(
        "filter, exp_urls",
        [
            (
                {},
                [
                    "https://tds.mock/dataset_01.nc",
                    "https://tds.mock/productA_path/cycle_02/dataset_02.nc",
                    "https://tds.mock/productA_path/cycle_02/dataset_22.nc",
                    "https://tds.mock/productA_path/cycle_03/dataset_03.nc",
                    "https://tds.mock/productA_path/cycle_03/dataset_33.nc",
                    "https://tds.mock/productB_path/cycle_04/dataset_04.nc",
                    "https://tds.mock/productB_path/cycle_04/dataset_44.nc",
                ],
            ),
            (
                {"cycle_number": [3, 4]},
                [
                    "https://tds.mock/dataset_01.nc",
                    "https://tds.mock/productA_path/cycle_03/dataset_03.nc",
                    "https://tds.mock/productA_path/cycle_03/dataset_33.nc",
                    "https://tds.mock/productB_path/cycle_04/dataset_04.nc",
                    "https://tds.mock/productB_path/cycle_04/dataset_44.nc",
                ],
            ),
            (
                {"path_filter": "A"},
                [
                    "https://tds.mock/dataset_01.nc",
                    "https://tds.mock/productA_path/cycle_02/dataset_02.nc",
                    "https://tds.mock/productA_path/cycle_02/dataset_22.nc",
                    "https://tds.mock/productA_path/cycle_03/dataset_03.nc",
                    "https://tds.mock/productA_path/cycle_03/dataset_33.nc",
                ],
            ),
            (
                {"path_filter": "A", "cycle_number": 3},
                [
                    "https://tds.mock/dataset_01.nc",
                    "https://tds.mock/productA_path/cycle_03/dataset_03.nc",
                    "https://tds.mock/productA_path/cycle_03/dataset_33.nc",
                ],
            ),
            (
                {"path_filter": "B"},
                [
                    "https://tds.mock/dataset_01.nc",
                    "https://tds.mock/productB_path/cycle_04/dataset_04.nc",
                    "https://tds.mock/productB_path/cycle_04/dataset_44.nc",
                ],
            ),
            (
                {"path_filter": "C"},
                [
                    "https://tds.mock/dataset_01.nc",
                ],
            ),
            (
                {"cycle_number": "6"},
                [
                    "https://tds.mock/dataset_01.nc",
                ],
            ),
        ],
    )
    def test_find(self, tds_iterable, filter, exp_urls):
        urls = tds_iterable.find("https://tds.mock/catalog.xml", **filter)

        assert urls == exp_urls

    def test_find_not_layout(self):
        urls = TDSIterable().find("https://tds.mock/catalog.xml", {"filter1": 12})

        assert urls == [
            "https://tds.mock/dataset_01.nc",
            "https://tds.mock/productA_path/cycle_02/dataset_02.nc",
            "https://tds.mock/productA_path/cycle_02/dataset_22.nc",
            "https://tds.mock/productA_path/cycle_03/dataset_03.nc",
            "https://tds.mock/productA_path/cycle_03/dataset_33.nc",
            "https://tds.mock/productB_path/cycle_04/dataset_04.nc",
            "https://tds.mock/productB_path/cycle_04/dataset_44.nc",
        ]

    @pytest.mark.parametrize(
        "filter, exp_urls",
        [
            (
                {"bad_filter": "B"},
                [
                    "https://tds.mock/dataset_01.nc",
                    "https://tds.mock/productA_path/cycle_02/dataset_02.nc",
                    "https://tds.mock/productA_path/cycle_02/dataset_22.nc",
                    "https://tds.mock/productA_path/cycle_03/dataset_03.nc",
                    "https://tds.mock/productA_path/cycle_03/dataset_33.nc",
                    "https://tds.mock/productB_path/cycle_04/dataset_04.nc",
                    "https://tds.mock/productB_path/cycle_04/dataset_44.nc",
                ],
            )
        ],
    )
    def test_find_bad_filter(self, tds_iterable, filter, exp_urls):
        with pytest.warns(
            UserWarning,
            match=(
                "Layout has been configured with unknown"
                " references '{'bad_filter'}'. They will be ignored."
            ),
        ):
            urls = tds_iterable.find("https://tds.mock/catalog.xml", **filter)
            assert urls == exp_urls

    def test_find_bad_url(self, tds_iterable):
        with pytest.raises(ProxyError) as exc_info:
            tds_iterable.find("https://bad_url/catalog.xml")

        assert (
            "HTTPSConnectionPool(host='https://bad_url/catalog.xml', port=443): "
            "Max retries exceeded with url: /L2-SWOT.html (Caused by ProxyError"
            "('Unable to connect to proxy', OSError('Tunnel connection failed: 503 "
            "Service Unavailable'))"
        ) in str(exc_info.value)


def test_filter_granules():
    urls = filter_granules(AvisoProduct(id="productA"))
    assert list(urls) == [
        "https://tds.mock/productA_path/cycle_02/dataset_02.nc",
        "https://tds.mock/productA_path/cycle_02/dataset_22.nc",
        "https://tds.mock/productA_path/cycle_03/dataset_03.nc",
        "https://tds.mock/productA_path/cycle_03/dataset_33.nc",
    ]
    urls = filter_granules(AvisoProduct(id="productA"), pass_number=3)
    assert list(urls) == ["https://tds.mock/productA_path/cycle_03/dataset_03.nc"]


def test_load_convention_layout(patch_some, test_layout, test_filename_convention):
    conf = {"TEST_TYPE": ["FileNameConventionSwotL3", "AVISO_L3_LR_SSH_LAYOUT"]}
    with pytest.raises(
        KeyError,
        match="The data type BAD_TYPE is missing from the "
        "tds_layout|granule_discovery configuration.",
    ):
        _load_convention_layout(conf, "BAD_TYPE")

    conv, layout = _load_convention_layout(conf, "TEST_TYPE")
    assert type(conv) is type(test_filename_convention)
    assert layout == test_layout


@pytest.mark.parametrize(
    "_id, short_name, path_filter",
    [("productA", "sample_product_a", "A"), ("productB", "sample_product_b", "B")],
)
def test_parse_tds_layout(
    patch_some, test_layout, test_filename_convention, _id, short_name, path_filter
):
    pl_conf = _parse_tds_layout(AvisoProduct(id=_id))
    assert isinstance(pl_conf, ProductLayoutConfig)

    assert pl_conf.id == _id
    assert pl_conf.default_filters == {"path_filter": path_filter}
    assert pl_conf.catalog_path == f"{_id}_path"
    assert pl_conf.short_name == short_name
    assert pl_conf.layout == test_layout
    assert type(pl_conf.convention) is type(test_filename_convention)


def test_parse_tds_layout_no_filter(patch_some):
    pl_conf = _parse_tds_layout(AvisoProduct(id="productC"))
    assert isinstance(pl_conf, ProductLayoutConfig)

    assert pl_conf.default_filters == {}


def test_parse_tds_layout_bad_product():
    with pytest.raises(
        KeyError,
        match="The product bad_product_id is missing from the "
        "tds_layout configuration file.",
    ):
        _parse_tds_layout(AvisoProduct(id="bad_product_id"))
