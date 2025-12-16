import pytest
from coinmetrics._exceptions import (
    CoinMetricsClientQueryParamsException,
    CoinMetricsClientBadParameterError,
    CoinMetricsClientForbiddenError,
    CoinMetricsClientUnauthorizedError,
)
from coinmetrics.api_client import CoinMetricsClient
import os

client = CoinMetricsClient(str(os.environ.get("CM_API_KEY")))
cm_api_key_set = os.environ.get("CM_API_KEY") is not None
REASON_TO_SKIP = "Need to set CM_API_KEY as an env var in order to run this test"

print("CM_API_KEY is set - tests will run") if cm_api_key_set else print(
    "CM_API_KEY not set, tests will not run"
)


@pytest.mark.skipif(not cm_api_key_set, reason=REASON_TO_SKIP)
def test_error_400_bad_parameter() -> None:
    """
    Test that CoinMetricsClient raises CoinMetricsClientBadParameterError for 400 responses.
    """
    try:
        client.catalog_asset_metrics_v2(assets="bad_asset_name").to_list()
    except Exception as e:
        assert isinstance(e, CoinMetricsClientBadParameterError)

    CoinMetricsClient(
        api_key=str(os.environ.get("CM_API_KEY")),
        ignore_unsupported_errors=True
    ).catalog_asset_metrics_v2(assets="bad_asset_name").to_list()


@pytest.mark.skipif(not cm_api_key_set, reason=REASON_TO_SKIP)
def test_error_401_unauthorized() -> None:
    """
    Test that CoinMetricsClient raises CoinMetricsClientUnauthorizedError for 401 responses.
    """
    try:
        CoinMetricsClient(api_key="bad_api_key").get_asset_metrics("btc", "PriceUSD")
    except Exception as e:
        assert isinstance(e, CoinMetricsClientUnauthorizedError)

@pytest.mark.skipif(not cm_api_key_set, reason=REASON_TO_SKIP)
def test_error_403_forbidden() -> None:
    """
    Test that CoinMetricsClient raises CoinMetricsClientForbiddenError for 403 responses.
    """
    try:
        # community API key has no access to this metric
        next(CoinMetricsClient().get_asset_metrics(
            assets='btc',
            metrics='volume_trusted_spot_usd_1d',
            limit_per_asset=1,
            format='json',
            page_size=1
        ))
    except Exception as e:
        assert isinstance(e, CoinMetricsClientForbiddenError)

    # this should not raise an error
    _ = next(CoinMetricsClient(
        ignore_forbidden_errors=True
    ).get_asset_metrics(
        assets='btc',
        metrics='volume_trusted_spot_usd_1d',
        limit_per_asset=1,
        format='json',
        page_size=1
    ))

@pytest.mark.skipif(not cm_api_key_set, reason=REASON_TO_SKIP)
def test_error_414_too_long() -> None:
    """
    Test for CoinMetricsClientQueryParamsException hitting a 414 error.
    """
    client = CoinMetricsClient(str(os.environ.get("CM_API_KEY")))
    markets = [market["market"] for market in client.reference_data_markets(base='btc', type='future')]

    try:
        client.get_market_trades(markets=markets, limit_per_market=1).to_list()
    except Exception as e:
        assert isinstance(e, CoinMetricsClientQueryParamsException)


if __name__ == "__main__":
    pytest.main()
