from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AvisoProduct:
    """Product of the catalog.

    Contains the product metadata.

    Parameters
    ----------
    id: str
        Product ID.
    title: str
        Full title of the product.
    short_name: str
        Short name (used as identifier).
    keywords: str
        Comma-separated list of keywords.
    abstract: str
        Description or summary of the product.
    processing_level: str
        Processing level (e.g., L2, L3).
    tds_catalog_url: str
        URL to the THREDDS catalog.
    doi: str
        Digital Object Identifier of the product.
    last_update: datetime
        Last update of the product.
    last_version: str
        Version identifier of the product.
    credit: str
        Data provider or credit information.
    organisation: str
        Responsible organisation.
    contact: str
        Contact email or name.
    resolution: str
        Spatial resolution of the dataset.
    temporal_extent: tuple[datetime, datetime]
        Start and end dates of the data coverage.
    geographic_extent: tuple[float, float, float, float]
        Bounding box as (west, east, south, north).
    """

    id: str = field(metadata={"label": "Id"})
    title: str | None = field(default=None, metadata={"label": "Title"})
    short_name: str | None = field(default=None, metadata={"label": "Short Name"})
    keywords: str | None = field(default=None, metadata={"label": "Keywords"})
    abstract: str | None = field(default=None, metadata={"label": "Abstract"})
    processing_level: str | None = field(default=None, metadata={"label": "Level"})
    tds_catalog_url: str | None = field(default=None, metadata={"label": "URL"})
    doi: str | None = field(default=None, metadata={"label": "DOI"})
    last_update: datetime | None = field(
        default=None, metadata={"label": "Last Update"}
    )
    last_version: str | None = field(default=None, metadata={"label": "Last Version"})
    credit: str | None = field(default=None, metadata={"label": "Credit"})
    organisation: str | None = field(default=None, metadata={"label": "Organisation"})
    contact: str | None = field(default=None, metadata={"label": "Contact"})
    resolution: str | None = field(default=None, metadata={"label": "Resolution"})
    temporal_extent: tuple[datetime, datetime] | None = field(
        default=(None, None), metadata={"label": "Temporal extent"}
    )
    geographic_extent: tuple[float, float, float, float] | None = field(
        default=(None, None, None, None), metadata={"label": "Geographic extent"}
    )


@dataclass
class AvisoCatalog:
    """Catalog of the AVISO/ODATIS service.

    Contains a list of available products parsed from the metadata catalog.

    Parameters
    ----------
    products : list[AvisoProduct]
        List of available products in the catalog.
    """

    products: list[AvisoProduct]
