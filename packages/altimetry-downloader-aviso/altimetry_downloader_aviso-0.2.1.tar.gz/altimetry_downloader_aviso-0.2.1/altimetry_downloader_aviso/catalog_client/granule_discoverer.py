import logging
import typing as tp
import warnings
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin

import yaml
from fcollections.core import FileDiscoverer, FileNameConvention, ITreeIterable, Layout
from siphon.catalog import TDSCatalog

from .geonetwork import AvisoProduct

with warnings.catch_warnings():
    # ImportWarning is raised when the geographical functionalities are disabled. We do
    # not need these functionalities, so we can ignore this warning
    warnings.simplefilter("ignore", category=ImportWarning)
    import fcollections.implementations

logger = logging.getLogger(__name__)

TDS_CATALOG_BASE_URL = "https://tds-odatis.aviso.altimetry.fr/thredds/catalog/"

TDS_LAYOUT_CONFIG = Path(__file__).parent / "resources" / "tds_layout.yaml"


class TDSIterable(ITreeIterable):
    """List files or links in a TDS Server.

    Parameters
    ----------
    layout
        Layout allowing to guess the tree structure and eventually discard some
        branches along the search
    """

    def __init__(self, layout: Layout | None = None):
        super().__init__(layout)

    def find(
        self, root: str, detail: bool = False, **filters: tp.Any
    ) -> tp.Iterator[str | dict[str, str]]:

        if self.layout is not None:
            self.layout.set_filters(**filters)

        logger.debug("Browsing TDS layout with filters: %s", filters)

        return self._find(root, **filters)

    def _find(self, url: str, level: int = 0, **filters):
        cat = TDSCatalog(url)

        results = [d.access_urls["HTTPServer"] for d in cat.datasets.values()]

        for folder, ref in cat.catalog_refs.items():
            # If name doesn't correspond to filters, continue
            if self.layout is not None and not self.layout.test(level, folder):
                logger.debug("Ignore folder %s", folder)
                continue

            next_level = level + 1

            # Each `catalog_refs` should have (name, ref), and it should be possible
            # to follow `ref` with `child = ref.follow()`. But there is a "name"
            # marker missing somewhere in the Odatis TDS catalog.xml, so it's not
            # possible to follow the ref directly.
            # Instead, we use the `href` and create a new TDSCatalog object with it.
            # Example:
            #   ref.href = https://tds-odatis.aviso.altimetry.fr/thredds/catalog/
            #              dataset-l3-swot-karin-nadir-validated/l3_lr_ssh/v1_0_1/Unsmoothed/
            #              cycle_001/catalog.xml

            results += self._find(ref.href, next_level, **filters)

        return results


def filter_granules(product: AvisoProduct, **filters) -> list[str]:
    """Filter granules of a product in AVISO's Thredds Data Server.

    Parameters
    ----------
    product
        the aviso product
    **filters
        filters for files selection

    Returns
    -------
    list[str]
        the urls of the granules corresponding to the provided filters
    """
    logger.info(
        "Filtering %s product with filters %s...",
        product.short_name,
        (lambda d: str(d))(filters),
    )

    # Get TDS product layout
    product_layout_conf = _parse_tds_layout(product)

    # Build TDS catalog URL
    tds_url = urljoin(
        TDS_CATALOG_BASE_URL,
        str(Path(product_layout_conf.catalog_path) / "catalog.xml"),
    )

    # Create the file discoverer for this TDS catalog
    file_discoverer = FileDiscoverer(
        parser=product_layout_conf.convention,
        iterable=TDSIterable(layout=product_layout_conf.layout),
    )

    filters = {**product_layout_conf.default_filters, **filters}

    granules = file_discoverer.list(path=tds_url, **filters)

    return granules.filename


def _load_convention_layout(
    granule_discovery: dict, data_type: str
) -> tuple[FileNameConvention, Layout]:
    """Load the fcollections convention and layout objects from a data type."""
    if data_type not in granule_discovery:
        msg = (
            f"The data type {data_type} is missing from the "
            "tds_layout|granule_discovery configuration."
        )
        raise KeyError(msg)
    convention, layout = granule_discovery[data_type]

    convention_obj, layout_obj = getattr(
        fcollections.implementations, convention
    )(), getattr(fcollections.implementations, layout)
    return convention_obj, layout_obj


@dataclass
class ProductLayoutConfig:
    """Configuration of a product layout.

    Defines how a product is named, organized, and stored in the catalog.

    Attributes
    ----------
    id: str
        Unique identifier of the product layout.
    short_name: str
        Short name of the product (used as reference in CLI or metadata).
    convention: FileNameConvention
        Convention used for naming files related to the product.
    layout: Layout
        Layout structure used to organize the product files and directories.
    catalog_path: str
        Relative or absolute path to the product catalog location.
    default_filters: dict
        Default filters applied when querying or displaying the product.
    """

    id: str
    short_name: str
    convention: FileNameConvention
    layout: Layout
    catalog_path: str
    default_filters: dict


def _parse_tds_layout(product: AvisoProduct) -> ProductLayoutConfig:
    """Parse resources/tds_layout.yaml to retrieve the layout information.

    The yaml should have a 'products' and a 'granule_discovery'
    sections.
    """
    with open(TDS_LAYOUT_CONFIG) as f:

        tds_layout = yaml.safe_load(f)

        products_tds_layout = tds_layout["products"]
        if product.id not in products_tds_layout:
            msg = (
                f"The product {product.id} is missing from the "
                "tds_layout configuration file."
            )
            raise KeyError(msg)
        product_layout = products_tds_layout[product.id]

        granule_discovery = tds_layout["granule_discovery"]
        data_type = product_layout["data_type"]
        convention_obj, layout_obj = _load_convention_layout(
            granule_discovery, data_type
        )

        if "filters" not in product_layout:
            product_layout["filters"] = {}

        return ProductLayoutConfig(
            id=product.id,
            short_name=product_layout["short_name"],
            convention=convention_obj,
            layout=layout_obj,
            catalog_path=product_layout["catalog_path"],
            default_filters=product_layout["filters"],
        )
