from typing import Any, Optional, TypedDict

import ldclient
from flask import current_app
from ldclient import Config, Context


class UserContext(TypedDict):
    user_id: int
    name: str
    email: str
    organization: str
    brands: dict[str, Any]


class FeatureFlags:
    _ld_client = None

    @classmethod
    def _initialize_client(cls) -> None:
        if not cls._ld_client:
            ldclient.set_config(
                Config(
                    sdk_key=current_app.config['DH_POTLUCK_LAUNCHDARKLY_TOKEN'],
                    stream_uri=current_app.config['DH_POTLUCK_LAUNCHDARKLY_RELAY_URL'],
                    base_uri=current_app.config['DH_POTLUCK_LAUNCHDARKLY_RELAY_URL'],
                    events_uri=current_app.config['DH_POTLUCK_LAUNCHDARKLY_RELAY_URL'],
                )
            )
            cls._ld_client = ldclient.get()

    @staticmethod
    def _get_current_user():
        try:
            return current_app.extensions['dh-potluck'].current_user
        except (AttributeError, KeyError):
            return None

    @classmethod
    def _get_user_context(cls) -> UserContext:
        user = cls._get_current_user()
        assert user is not None
        return {
            'user_id': user.id,
            'name': f'{user.first_name} {user.last_name}',
            'email': user.email,
            'organization': user.organization['label'],
            'brands': user.brands or {},
        }

    @classmethod
    def has_feature_flag(cls, feature_flag: str, brand_id: int) -> bool:
        try:
            cls._initialize_client()
            if cls._ld_client is None:
                return False

            return cls._ld_client.variation(
                feature_flag,
                cls._get_ld_context(brand_id, cls._get_user_context()),
                False,
            )
        except Exception:
            return False

    @classmethod
    def any_accessible_brand_has_feature_flag(cls, feature_flag: str) -> bool:
        user = cls._get_current_user()
        if not user or not hasattr(user, 'accessible_brands'):
            return False

        cls._initialize_client()
        if cls._ld_client is None:
            return False

        has_access = any(
            [
                cls._ld_client.variation(feature_flag, cls._get_ld_context(brand_id), False)
                for brand_id in user.accessible_brands
            ]
        )
        return has_access

    @classmethod
    def _get_ld_context(cls, brand_id: int, user: Optional[UserContext] = None) -> Context:
        if user is None:
            user = cls._get_user_context()

        builder = Context.builder(f'{user["user_id"]}')
        builder.name(user['name'])
        builder.set('email', user['email'])
        builder.set('organization', user['organization'])
        for brand in user['brands'].values():
            if brand['id'] == brand_id:
                builder.set('brand', brand['label'])
                break
        return builder.build()
