"""Secret tests"""

import json
import os
from getpass import getpass

from oauthlib.oauth2.rfc6749.tokens import OAuth2Token

from nic_api import DnsApi, pprint
from nic_api.exceptions import ExpiredToken, ZoneAlreadyExists
from nic_api.models import (
    AAAARecord,
    ARecord,
    CNAMERecord,
    DNAMERecord,
    HINFORecord,
    MXRecord,
    NAPTRRecord,
    NICZoneRevision,
    NSRecord,
    PTRRecord,
    RPRecord,
    SRVRecord,
    TXTRecord,
)

APP_LOGIN = "deb79b35e6ea73a91f0926ca1f7761fa"
APP_PASSWORD = "9SJktB5rK12YczBiORq2yf8YJWMNwVFpl9I_UBAKVLI"
DEFAULT_SERVICE = "DP2512077571"
DEFAULT_ZONE = "werylabs.tech"

TOKEN_CACHE_FILE = os.path.join(os.path.expanduser("~"), ".nic_api_token.json")


def test_add_zone():
    api = DnsApi(APP_LOGIN, APP_PASSWORD, _load_token(), _save_token)
    try:
        api.add_zone(zone=DEFAULT_ZONE, service=DEFAULT_SERVICE)
    except ZoneAlreadyExists:
        pass
    zones = api.zones(DEFAULT_SERVICE)
    assert DEFAULT_ZONE in [zone.name for zone in zones]


def test_delete_zone():
    api = DnsApi(APP_LOGIN, APP_PASSWORD, _load_token(), _save_token)
    api.delete_zone(zone=DEFAULT_ZONE, service=DEFAULT_SERVICE)
    zones = api.zones(DEFAULT_SERVICE)
    assert DEFAULT_ZONE not in [zone.name for zone in zones]


def test_add_zone_second():
    api = DnsApi(APP_LOGIN, APP_PASSWORD, _load_token(), _save_token)
    api.default_service = DEFAULT_SERVICE
    api.add_zone(zone=DEFAULT_ZONE)
    zones = api.zones()
    assert DEFAULT_ZONE in [zone.name for zone in zones]


def test_add_print_rollback():
    api = DnsApi(APP_LOGIN, APP_PASSWORD, _load_token(), _save_token)
    api.default_service = DEFAULT_SERVICE
    api.default_zone = DEFAULT_ZONE
    records = [
        NSRecord(ns="dnsa.google.com.", name="@"),
        ARecord("1.1.1.1", name="foobar"),
        ARecord("8.8.8.8", name="тест-кириллицы".encode("idna").decode()),
        AAAARecord("cafe:dead:beef::1", name="foobar"),
        CNAMERecord("foo", name="bar"),
        MXRecord(50, "mx.foobar.ru", name="@"),
        TXTRecord("my name is Sergey", name="foobar"),
        TXTRecord("testing TTL", name="foobar", ttl=7200),
        SRVRecord(
            priority=0,
            weight=5,
            port=5060,
            target="sipserver.test.ru.",
            name="_sip._tcp",
        ),
        PTRRecord(ptr="1.0.168.192.in-addr.arpa."),
        DNAMERecord(dname="nic-api-test-2.com."),
        HINFORecord(hardware="IBM-PC/XT", os="OS/2"),
        NAPTRRecord(
            order=1,
            preference=100,
            flags="S",
            service="sip+D2U",
            replacement="_sip._udp.nic-api-test.com.",
        ),
        RPRecord(mbox="info.andrian.ninja.", txt="."),
    ]

    # Ensure there are no changes
    my_zones = [zone for zone in api.zones() if zone.name == DEFAULT_ZONE]
    assert len(my_zones) == 1 and not my_zones[0].has_changes

    # Add records
    added_records = api.add_record(records)

    assert added_records[2].idn_name == "тест-кириллицы"

    # Ensure changes are there
    my_zones = [zone for zone in api.zones() if zone.name == DEFAULT_ZONE]
    assert len(my_zones) == 1 and my_zones[0].has_changes

    try:
        all_records = api.records()
        for record in all_records:
            pprint(record)
    finally:
        api.rollback()

    # Ensure there are no changes again
    my_zones = [zone for zone in api.zones() if zone.name == DEFAULT_ZONE]
    assert len(my_zones) == 1 and not my_zones[0].has_changes


def test_add_delete_commit():
    api = DnsApi(APP_LOGIN, APP_PASSWORD, _load_token(), _save_token)
    api.default_service = DEFAULT_SERVICE
    api.default_zone = DEFAULT_ZONE

    # Ensure there are no changes
    my_zones = [zone for zone in api.zones() if zone.name == DEFAULT_ZONE]
    assert len(my_zones) == 1 and not my_zones[0].has_changes

    rec_1 = ARecord("1.1.1.1", name="foobar")
    added = api.add_record(rec_1)

    # Ensure changes are there
    my_zones = [zone for zone in api.zones() if zone.name == DEFAULT_ZONE]
    assert len(my_zones) == 1 and my_zones[0].has_changes

    api.delete_record(added[0].id)

    # Ensure changes are there
    my_zones = [zone for zone in api.zones() if zone.name == DEFAULT_ZONE]
    assert len(my_zones) == 1 and my_zones[0].has_changes

    api.commit()

    # Ensure there are no changes
    my_zones = [zone for zone in api.zones() if zone.name == DEFAULT_ZONE]
    assert len(my_zones) == 1 and not my_zones[0].has_changes


def test_get_add_zonefile():
    api = DnsApi(APP_LOGIN, APP_PASSWORD, _load_token(), _save_token)
    api.default_service = DEFAULT_SERVICE
    api.default_zone = DEFAULT_ZONE
    zonefile = api.zonefile()
    api.set_zonefile(zonefile=zonefile)


def test_set_get_default_ttl():
    api = DnsApi(APP_LOGIN, APP_PASSWORD, _load_token(), _save_token)
    api.default_service = DEFAULT_SERVICE
    api.default_zone = DEFAULT_ZONE
    api.set_default_ttl(ttl=7200)
    assert api.get_default_ttl() == 7200


def test_revisions():
    api = DnsApi(APP_LOGIN, APP_PASSWORD, _load_token(), _save_token)
    api.default_service = DEFAULT_SERVICE
    api.default_zone = DEFAULT_ZONE
    revisions = api.list_revisions()
    assert len(revisions) > 1
    for revision in revisions:
        assert isinstance(revision, NICZoneRevision)
    assert len(api.get_revision(revisions[0].number)) > 0
    api.set_revision(revisions[-1].number)


def _load_token():
    with open(TOKEN_CACHE_FILE, "r") as fp_token:
        token_data = json.load(fp_token)
    return OAuth2Token(token_data)


def _save_token(token):
    with open(TOKEN_CACHE_FILE, "w") as fp_token:
        json.dump(token, fp_token)


def main():
    api = None
    try:
        token = _load_token()
        api = DnsApi(APP_LOGIN, APP_PASSWORD, token, _save_token)
        services = api.services()
        print(services)
    except (ValueError, ExpiredToken) as exc_info:
        print(exc_info)
        username = input("Login: ")
        password = getpass("Password: ")
        if api is None:
            api = DnsApi(
                APP_LOGIN,
                APP_PASSWORD,
                token_updater_clb=_save_token,
            )
        api.get_token(username, password)
        services = api.services()
        print(services)


if __name__ == "__main__":
    main()
