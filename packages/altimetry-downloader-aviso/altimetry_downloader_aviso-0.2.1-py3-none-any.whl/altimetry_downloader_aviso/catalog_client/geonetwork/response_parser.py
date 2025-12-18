import logging

from pydantic import TypeAdapter, ValidationError

from .models.catalog_resp_model import AvisoCatalogModel
from .models.model import AvisoCatalog, AvisoProduct
from .models.product_resp_model import AvisoProductModel

logger = logging.getLogger(__name__)


def parse_catalog_response(results: dict) -> AvisoCatalog:
    """Parses the response of Aviso's catalog to a fetching request.

    Parameters
    ----------
    results
        the dictionary representing the json catalog's response

    Returns
    -------
        The object resulting from the parsing

    Raises
    ------
    RuntimeError
        In case an exception happens when parsing catalog response
    """
    adapter = TypeAdapter(AvisoCatalogModel)

    try:
        catalog = adapter.validate_python(results)

        return AvisoCatalog(
            products=[
                AvisoProduct(
                    id=record.get_product_id(),
                    title=record.get_product_title(),
                    keywords=record.get_product_keywords(),
                    tds_catalog_url=record.get_product_tds_catalog_url(),
                    short_name=record.get_product_short_name(),
                    doi=record.get_product_doi(),
                    last_update=record.get_product_last_update(),
                )
                for record in catalog.hits.hits
            ]
        )
    except ValidationError as e:
        logger.error(
            "A validation error happened when parsing Aviso's catalog response: %s",
            str(e),
        )
        raise RuntimeError(f"{e}")


def parse_product_response(meta: dict, aviso_product: AvisoProduct) -> AvisoProduct:
    """Parses the response of AVISO's catalog to a product request.

    Parameters
    ----------
    meta
        the json to parse
    aviso_product
        the product object to fill in

    Returns
    -------
        the object resulting from the parsing
    """
    adapter = TypeAdapter(AvisoProductModel)

    try:
        product = adapter.validate_python(meta)

        aviso_product.last_version = product.get_last_version()
        aviso_product.processing_level = product.get_processing_level()
        aviso_product.abstract = product.get_abstract()
        aviso_product.credit = product.get_credit()
        aviso_product.organisation = product.get_organisation()
        aviso_product.contact = product.get_contact_info()
        aviso_product.resolution = product.get_resolution()
        aviso_product.geographic_extent = product.get_geographic_extent()
        aviso_product.temporal_extent = product.get_temporal_extent()

    except ValidationError as e:
        for err in e.errors():
            logger.error(
                "A validation error happened when parsing Aviso's"
                " catalog response for product: %s.\n%s",
                aviso_product.id,
                err,
            )

    return aviso_product
