# flake8: noqa

if __import__("typing").TYPE_CHECKING:
    # import apis into api package
    from circle.web3.user_controlled_wallets.api.pin_authentication_api import PINAuthenticationApi
    from circle.web3.user_controlled_wallets.api.signing_api import SigningApi
    from circle.web3.user_controlled_wallets.api.social_email_authentication_api import SocialEmailAuthenticationApi
    from circle.web3.user_controlled_wallets.api.token_lookup_api import TokenLookupApi
    from circle.web3.user_controlled_wallets.api.transactions_api import TransactionsApi
    from circle.web3.user_controlled_wallets.api.users_api import UsersApi
    from circle.web3.user_controlled_wallets.api.wallets_api import WalletsApi
    
else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import apis into api package
from circle.web3.user_controlled_wallets.api.pin_authentication_api import PINAuthenticationApi
from circle.web3.user_controlled_wallets.api.signing_api import SigningApi
from circle.web3.user_controlled_wallets.api.social_email_authentication_api import SocialEmailAuthenticationApi
from circle.web3.user_controlled_wallets.api.token_lookup_api import TokenLookupApi
from circle.web3.user_controlled_wallets.api.transactions_api import TransactionsApi
from circle.web3.user_controlled_wallets.api.users_api import UsersApi
from circle.web3.user_controlled_wallets.api.wallets_api import WalletsApi

""",
            name=__name__,
            doc=__doc__,
        )
    )
