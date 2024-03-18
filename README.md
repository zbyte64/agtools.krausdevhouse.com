Installing
----------

`docker compose build`
`docker compose run web alembic upgrade head`


Running
-------
`docker compose run web python -m agtools.download_cimis_spatial`


Usage
-----

`curl http://localhost:8000/historical-eto?lat=36.7664498&lon=-119.8054374&start_date=2024-03-15&num_of_days=1`