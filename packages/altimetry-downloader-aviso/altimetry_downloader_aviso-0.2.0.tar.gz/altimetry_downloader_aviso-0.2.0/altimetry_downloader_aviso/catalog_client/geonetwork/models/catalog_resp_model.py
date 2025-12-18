from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator


class ResourceTitleObject(BaseModel):
    default: str


class ResourceAbstractObject(BaseModel):
    default: str


class ResourceDateItem(BaseModel):
    date: datetime


class FieldSource(BaseModel):
    resourceTitleObject: ResourceTitleObject
    resourceAbstractObject: ResourceAbstractObject
    resourceDate: list[ResourceDateItem]
    url: str | None = None
    short_name: str | None = None
    doi: str | None = None

    @model_validator(mode="before")
    @classmethod
    def extract_from_links(cls, data: dict[str, Any]) -> dict[str, Any]:
        links: list[dict[str, Any]] = data.pop("link", [])

        for item in links:
            if item.get("descriptionObject", {}).get("default") == "THREDDS":
                data["url"] = item.get("urlObject", {}).get("default")
                if "nameObject" in item:
                    data["short_name"] = (
                        item.get("nameObject").get("default").replace(" ", "_")
                    )
            elif item.get("protocol") == "DOI":
                data["doi"] = item.get("urlObject", {}).get("default")

        return data


class Hit(BaseModel):
    field_id: str = Field(..., alias="_id")
    field_source: FieldSource = Field(..., alias="_source")

    def get_product_id(self) -> str:
        return self.field_id

    def get_product_title(self) -> str:
        return self.field_source.resourceTitleObject.default

    def get_product_keywords(self) -> str:
        return self.field_source.resourceAbstractObject.default

    def get_product_tds_catalog_url(self) -> str:
        return self.field_source.url

    def get_product_short_name(self) -> str:
        return self.field_source.short_name

    def get_product_doi(self) -> str:
        return self.field_source.doi

    def get_product_last_update(self) -> datetime:
        return self.field_source.resourceDate[-1].date


class Hits(BaseModel):
    hits: list[Hit]


class AvisoCatalogModel(BaseModel):
    hits: Hits
