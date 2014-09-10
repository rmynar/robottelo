# -*- encoding: utf-8 -*-
# vim: ts=4 sw=4 expandtab ai
"""Test class for SSO (CLI)"""

import sys

from robottelo.common.constants import NOT_IMPLEMENTED
from robottelo.test import CLITestCase

if sys.hexversion >= 0x2070000:
    import unittest
else:
    import unittest2 as unittest


class TestSSOCLI(CLITestCase):

    # Notes for SSO testing:
    # Of interest... In some testcases I've placed a few comments prefaced with
    # "devnote:" These are -- obviously -- notes from developers that might
    # help reiterate something important or a reminder of way(s) to test
    # something.

    # There may well be more cases that I have missed for this feature, and
    # possibly other LDAP types. These (in particular, the LDAP variations)
    # can be easily added later.

    @unittest.skip(NOT_IMPLEMENTED)
    def test_sso_kerberos_cli(self):
        """@test: kerberos user can login to CLI

        @feature: SSO

        @setup: kerberos configured against foreman.

        @assert: Log in to hammer cli successfully

        @status: Manual

        """
        pass

    @unittest.skip(NOT_IMPLEMENTED)
    def test_sso_ipa_cli(self):
        """@test: IPA user can login to CLI

        @feature: SSO

        @setup: IPA configured against foreman.

        @assert: Log in to hammer cli successfully

        @status: Manual

        """
        pass

    @unittest.skip(NOT_IMPLEMENTED)
    def test_sso_openldap_cli(self):
        """@test: OpenLDAP user can login to CLI

        @feature: SSO

        @setup: OpenLDAP configured against foreman.

        @assert: Log in to hammer cli successfully

        @status: Manual

        """
        pass
