# Changelog

## 1.1.0

-   \[BREAKING CHANGE\] Integrate with QPS API Instrument Templates
    1.0.11376 with following breaking changes:
    -   Added new mandatory property `underlying_spot_date` to class
        `StirFutureDefinition` in module `instrument_templates`
-   Integrate with QPS API IrSwap and Loan 1.0.11406 to support async.
    The async return model will change in next release
-   Added authentication examples in HTML documentation for service
    account, user account, user provided token and proxy server
-   Added more API fundamental and workflows examples
-   Added helper functions for Pandas DataFrame conversion in module
    `helpers`
    -   `description_to_df`
    -   `valuation_to_df`
    -   `risk_to_df`
    -   `cashflows_to_df`
-   Fixed duplicated structured products examples in HTML documentation
-   Removed unnecessary libraries in dependencies

## 1.0.0

-   Added 4 new functions `request_bond_search_async_get`,
    `request_bond_search_async_post`, `request_bond_search_sync_get` and
    `request_bond_search_sync_post` in module `yield_book_rest` for
    Yield Book Rest APIs
-   Supported sorted samples categories and sorted samples of each
    category for samples meta json file
-   Integrated with QPS API FinancialContract 1.0.11382
-   Added more fundamental and workflows samples and updated existing
    samples
-   Package created to support QPS and Yield Book Rest only APIs based
    on Python SDK 2.1.0b5
