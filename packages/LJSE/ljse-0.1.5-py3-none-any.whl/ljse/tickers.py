# Copyright (c) 2025 Janez Bučar
# All rights reserved.

import pandas as pd

URL_LISTING = (
    "https://rest.ljse.si/web/Bvt9fe2peQ7pwpyYqODM/"
    "securities/XLJU/csv?status=LISTED_SECURITIES&model=ALL&type=EQTY&language=SI"
)

def get_tickers():
    """
    Fetch the list of all currently listed equities on the Ljubljana Stock Exchange (LJSE).

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing essential metadata for all listed LJSE equities.
        Returned columns:
            - symbol : str
                The trading symbol of the security (e.g., "KRKG", "TLSG").
            - isin : str
                The ISIN code uniquely identifying the security.
            - name : str
                The full name of the company or instrument.
            - segment_listing_date : str
                The date when the security was listed on the relevant market segment.

        Example:
               symbol       isin               name     segment_listing_date
        0       KRKG  SI0031102120   KRKA d.d., Novo Mesto     1997-05-12
        1       TLSG  SI0031110083  Telekom Slovenije d.d.     2006-10-09

    Notes
    -----
    - Data is fetched directly from the official LJSE REST API.
    - The dataset includes only securities with type `EQTY` (equities).
    - The function performs no filtering; raw listing data is returned.
    """

    df = pd.read_csv(URL_LISTING, sep=";")
    return df