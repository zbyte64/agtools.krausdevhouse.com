from datetime import date, timedelta
from fastapi import Depends, FastAPI, HTTPException, status

# from geoalchemy2 import Geometry
from geoalchemy2.functions import (
    ST_Distance,
    ST_GeographyFromText,
)
from sqlalchemy import and_, select
from sqlalchemy.sql.functions import sum
from sqlalchemy.ext.asyncio import AsyncSession

from agtools.database import get_async_session
from agtools.models import CIMISDailyPoints


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/historical-eto")
async def get_historical_eto(
    lat: float,
    lon: float,
    start_date: date,
    num_of_days: int,
    db_session: AsyncSession = Depends(get_async_session),
):
    if num_of_days < 1:
        raise HTTPException(
            status=status.HTTP_400_BAD_REQUEST,
            detail="num_of_days must be positive",
        )
    end_date = start_date + timedelta(days=num_of_days)
    # assumes the geometry points are stable through time
    daily_values = (
        select(CIMISDailyPoints.value_inches)
        .where(
            and_(CIMISDailyPoints.date >= start_date, CIMISDailyPoints.date <= end_date)
        )
        .order_by(
            ST_Distance(
                CIMISDailyPoints.geometry,
                ST_GeographyFromText("POINT({} {})".format(lon, lat)),
            )
        )
        .limit(num_of_days)
    ).subquery()
    total_eto = select(sum(daily_values.c.value_inches))

    result = await db_session.execute(total_eto)
    return result.scalar_one()
