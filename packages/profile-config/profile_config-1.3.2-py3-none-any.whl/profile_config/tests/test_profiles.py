"""
Tests for profile resolution with inheritance.
"""

import pytest

from profile_config.exceptions import CircularInheritanceError, ProfileNotFoundError
from profile_config.profiles import ProfileResolver


class TestProfileResolver:
    """Test profile resolution functionality."""

    def test_init_default_inherit_key(self):
        """Test initialization with default inherit key."""
        resolver = ProfileResolver()
        assert resolver.inherit_key == "inherits"

    def test_init_custom_inherit_key(self):
        """Test initialization with custom inherit key."""
        resolver = ProfileResolver(inherit_key="extends")
        assert resolver.inherit_key == "extends"

    def test_resolve_profile_no_profiles_section(self):
        """Test resolving when no profiles section exists."""
        config_data = {"defaults": {"key1": "default_value"}, "key2": "root_value"}

        resolver = ProfileResolver()
        result = resolver.resolve_profile(config_data, "any_profile")

        expected = {"key1": "default_value", "key2": "root_value"}
        assert result == expected

    def test_resolve_simple_profile(self):
        """Test resolving a simple profile without inheritance."""
        config_data = {
            "defaults": {"key1": "default_value"},
            "profiles": {"dev": {"key1": "dev_value", "key2": "dev_only"}},
        }

        resolver = ProfileResolver()
        result = resolver.resolve_profile(config_data, "dev")

        expected = {
            "key1": "dev_value",  # Profile overrides default
            "key2": "dev_only",  # Profile-specific value
        }
        assert result == expected

    def test_resolve_profile_with_inheritance(self):
        """Test resolving a profile with single-level inheritance."""
        config_data = {
            "defaults": {"key1": "default_value"},
            "profiles": {
                "base": {"key1": "base_value", "key2": "base_only"},
                "dev": {
                    "inherits": "base",
                    "key1": "dev_value",  # Override parent
                    "key3": "dev_only",  # New key
                },
            },
        }

        resolver = ProfileResolver()
        result = resolver.resolve_profile(config_data, "dev")

        expected = {
            "key1": "dev_value",  # Dev overrides base
            "key2": "base_only",  # Inherited from base
            "key3": "dev_only",  # Dev-specific
        }
        assert result == expected

    def test_resolve_profile_multi_level_inheritance(self):
        """Test resolving a profile with multi-level inheritance."""
        config_data = {
            "defaults": {"key1": "default_value"},
            "profiles": {
                "base": {"key1": "base_value", "key2": "base_only"},
                "staging": {
                    "inherits": "base",
                    "key2": "staging_value",
                    "key3": "staging_only",
                },
                "prod": {
                    "inherits": "staging",
                    "key3": "prod_value",
                    "key4": "prod_only",
                },
            },
        }

        resolver = ProfileResolver()
        result = resolver.resolve_profile(config_data, "prod")

        expected = {
            "key1": "base_value",  # From base
            "key2": "staging_value",  # From staging
            "key3": "prod_value",  # Prod overrides staging
            "key4": "prod_only",  # Prod-specific
        }
        assert result == expected

    def test_resolve_nonexistent_profile(self):
        """Test resolving a profile that doesn't exist."""
        config_data = {"profiles": {"dev": {"key": "value"}}}

        resolver = ProfileResolver()

        with pytest.raises(ProfileNotFoundError) as exc_info:
            resolver.resolve_profile(config_data, "nonexistent")

        assert "Profile 'nonexistent' not found" in str(exc_info.value)
        assert "Available profiles: ['dev']" in str(exc_info.value)

    def test_resolve_fallback_to_default_profile(self):
        """Test fallback to default profile when requested profile doesn't exist."""
        config_data = {
            "profiles": {
                "default": {"key": "default_value"},
                "dev": {"key": "dev_value"},
            }
        }

        resolver = ProfileResolver()
        result = resolver.resolve_profile(config_data, "nonexistent", "default")

        expected = {"key": "default_value"}
        assert result == expected

    def test_circular_inheritance_detection(self):
        """Test detection of circular inheritance."""
        config_data = {
            "profiles": {
                "a": {"inherits": "b", "key": "a_value"},
                "b": {"inherits": "c", "key": "b_value"},
                "c": {"inherits": "a", "key": "c_value"},  # Creates cycle
            }
        }

        resolver = ProfileResolver()

        with pytest.raises(CircularInheritanceError) as exc_info:
            resolver.resolve_profile(config_data, "a")

        assert "Circular inheritance detected" in str(exc_info.value)

    def test_self_inheritance_detection(self):
        """Test detection of self-inheritance."""
        config_data = {
            "profiles": {"self_ref": {"inherits": "self_ref", "key": "value"}}
        }

        resolver = ProfileResolver()

        with pytest.raises(CircularInheritanceError) as exc_info:
            resolver.resolve_profile(config_data, "self_ref")

        assert "Circular inheritance detected" in str(exc_info.value)

    def test_inherit_key_not_removed_from_result(self):
        """Test that inherit key is removed from final result."""
        config_data = {
            "profiles": {
                "base": {"key1": "base_value"},
                "dev": {"inherits": "base", "key2": "dev_value"},
            }
        }

        resolver = ProfileResolver()
        result = resolver.resolve_profile(config_data, "dev")

        # The 'inherits' key should not be in the final result
        assert "inherits" not in result
        assert result == {"key1": "base_value", "key2": "dev_value"}

    def test_custom_inherit_key(self):
        """Test using a custom inheritance key."""
        config_data = {
            "profiles": {
                "base": {"key1": "base_value"},
                "dev": {"extends": "base", "key2": "dev_value"},  # Custom inherit key
            }
        }

        resolver = ProfileResolver(inherit_key="extends")
        result = resolver.resolve_profile(config_data, "dev")

        assert "extends" not in result
        assert result == {"key1": "base_value", "key2": "dev_value"}

    def test_list_profiles(self):
        """Test listing available profiles."""
        config_data = {
            "profiles": {
                "dev": {"key": "dev_value"},
                "staging": {"key": "staging_value"},
                "prod": {"key": "prod_value"},
            }
        }

        resolver = ProfileResolver()
        profiles = resolver.list_profiles(config_data)

        assert set(profiles) == {"dev", "staging", "prod"}

    def test_list_profiles_no_profiles_section(self):
        """Test listing profiles when no profiles section exists."""
        config_data = {"defaults": {"key": "value"}}

        resolver = ProfileResolver()
        profiles = resolver.list_profiles(config_data)

        assert profiles == []

    def test_get_default_profile(self):
        """Test getting default profile name."""
        config_data = {"default_profile": "production"}

        resolver = ProfileResolver()
        default = resolver.get_default_profile(config_data)

        assert default == "production"

    def test_get_default_profile_fallback(self):
        """Test getting default profile name with fallback."""
        config_data = {}

        resolver = ProfileResolver()
        default = resolver.get_default_profile(config_data)

        assert default == "default"

    # BUGFIX TESTS: Deep merge for nested dicts in profile inheritance

    def test_resolve_nested_dict_deep_merge_with_defaults(self):
        """Test that nested dicts are deep merged with defaults, not shallow replaced."""
        config_data = {
            "defaults": {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "options": {"timeout": 30, "pool_size": 10},
                }
            },
            "profiles": {
                "prod": {
                    "database": {
                        "host": "prod.example.com",
                        "options": {"timeout": 60},  # Should merge, not replace
                    }
                }
            },
        }

        resolver = ProfileResolver()
        result = resolver.resolve_profile(config_data, "prod")

        # With deep merge, nested values should be preserved
        expected = {
            "database": {
                "host": "prod.example.com",  # Overridden
                "port": 5432,  # Preserved from defaults
                "options": {
                    "timeout": 60,  # Overridden
                    "pool_size": 10,  # Preserved from defaults
                },
            }
        }
        assert result == expected

    def test_resolve_nested_dict_deep_merge_with_inheritance(self):
        """Test that nested dicts are deep merged in profile inheritance chain."""
        config_data = {
            "profiles": {
                "base": {
                    "server": {
                        "host": "0.0.0.0",
                        "port": 8000,
                        "ssl": {"enabled": False, "cert": None},
                    }
                },
                "prod": {
                    "inherits": "base",
                    "server": {
                        "host": "prod.example.com",
                        "ssl": {"enabled": True},  # Should merge, not replace
                    },
                },
            }
        }

        resolver = ProfileResolver()
        result = resolver.resolve_profile(config_data, "prod")

        # With deep merge, nested values should be preserved
        expected = {
            "server": {
                "host": "prod.example.com",  # Overridden
                "port": 8000,  # Preserved from base
                "ssl": {
                    "enabled": True,  # Overridden
                    "cert": None,  # Preserved from base
                },
            }
        }
        assert result == expected

    def test_resolve_nested_dict_multi_level_deep_merge(self):
        """Test deep merge across multiple inheritance levels."""
        config_data = {
            "defaults": {
                "config": {"level0": "default", "nested": {"level0": "default"}}
            },
            "profiles": {
                "base": {"config": {"level1": "base", "nested": {"level1": "base"}}},
                "staging": {
                    "inherits": "base",
                    "config": {"level2": "staging", "nested": {"level2": "staging"}},
                },
                "prod": {
                    "inherits": "staging",
                    "config": {"level3": "prod", "nested": {"level3": "prod"}},
                },
            },
        }

        resolver = ProfileResolver()
        result = resolver.resolve_profile(config_data, "prod")

        # All levels should be merged, not replaced
        expected = {
            "config": {
                "level0": "default",
                "level1": "base",
                "level2": "staging",
                "level3": "prod",
                "nested": {
                    "level0": "default",
                    "level1": "base",
                    "level2": "staging",
                    "level3": "prod",
                },
            }
        }
        assert result == expected

    def test_resolve_nested_list_replacement(self):
        """Test that lists are replaced, not merged (expected behavior)."""
        config_data = {
            "defaults": {"items": [1, 2, 3]},
            "profiles": {"dev": {"items": [4, 5]}},
        }

        resolver = ProfileResolver()
        result = resolver.resolve_profile(config_data, "dev")

        # Lists should be replaced, not merged
        expected = {"items": [4, 5]}
        assert result == expected
