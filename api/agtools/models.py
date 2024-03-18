from datetime import date
from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import Integer, Float, Date
from sqlalchemy.orm import Mapped, mapped_column

from agtools.database import Base


class CIMISDailyPoints(Base):
    """
    Stores CIMIS data with a "day" resolution as points on a map
    """

    __tablename__ = "cimis_daily_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[float] = mapped_column(Float)
    value_inches: Mapped[float] = mapped_column(Float)
    date: Mapped[date] = mapped_column(Date)
    # rename to centroids or geo_location?
    geometry: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True)
    )
