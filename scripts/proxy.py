from typing import Any, Optional

from pydantic import BaseModel

from better_web3 import Proxy as _Proxy


class ProxyInfo(BaseModel):
    ip: Optional[str] = None
    network: Optional[str] = None
    version: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    region_code: Optional[str] = None
    country: Optional[str] = None
    country_name: Optional[str] = None
    country_code: Optional[str] = None
    country_code_iso3: Optional[str] = None
    country_capital: Optional[str] = None
    country_tld: Optional[str] = None
    continent_code: Optional[str] = None
    in_eu: Optional[bool] = None
    postal: Optional[Any] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None
    utc_offset: Optional[str] = None
    country_calling_code: Optional[str] = None
    currency: Optional[str] = None
    currency_name: Optional[str] = None
    languages: Optional[str] = None
    country_area: Optional[float] = None
    country_population: Optional[int] = None
    asn: Optional[str] = None
    org: Optional[str] = None


class Proxy(_Proxy):
    def __init__(self, *args, **kwargs):
        self.info: ProxyInfo | None = None
        super().__init__(*args, **kwargs)
