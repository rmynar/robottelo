"""Tests For Disconnected Satellite Installation

:Requirement: Installer (disconnected satellite installation)

:CaseAutomation: Automated

:CaseLevel: Acceptance

:CaseComponent: Installer

:Assignee: rmynar

:TestType: Functional

:CaseImportance: High

:Upstream: No
"""
import pytest
from broker import VMBroker
from broker.hosts import Host

from robottelo.config import settings
from robottelo.helpers import InstallerCommand

installer_params = {
    'scenario': "satellite",
    'foreman-initial-organization': '"Default Organization"',
    'foreman-initial-location': '"Default Location"',
    'foreman-initial-admin-username': settings.server.admin_username,
    'foreman-initial-admin-password': settings.server.admin_password,
}


def host_conf(request):
    """A function that returns arguments for VMBroker host deployment"""
    conf = {}
    conf['workflow'] = "deploy-base-rhel"
    conf['rhel_version'] = "7.9"
    return conf


def _enable_sat_ports_fw(host):
    # enable incomming connections to Sat serivces
    host.execute(
        'firewall-cmd --permanent --zone=public'
        ' --add-port 80/tcp --add-port 443/tcp --add-port 5646/tcp'
        ' --add-port 5647/tcp --add-port 5671/tcp --add-port 8000/tcp'
        ' --add-port 8140/tcp --add-port 8443/tcp --add-port 9090/tcp'
        ' --add-port 22/tcp --add-port 2375/tcp --add-port 5000/tcp'
        ' --add-port 16509/tcp --add-port 53/udp --add-port 69/udp'
        ' && firewall-cmd --reload'
    )


@pytest.fixture
def rhel_host_disconnected(request):
    """A function-level fixture that provides a host which is ready for disconnected installation"""
    with VMBroker(**host_conf(request), host_classes={'host': Host}) as host:
        # download RHEL and Satellite ISOs
        host.execute(f'curl -O {settings.installer.rhel_iso_url}', timeout="7m")
        host.execute(f'curl -O {settings.installer.sat_iso_url}', timeout="5m")
        # mount ISOs and configure yum repos
        host.execute('mkdir /media/rhel7-server')
        host.execute('mount -o loop $(ls RHEL*.iso) /media/rhel7-server')
        host.execute('cp /media/rhel7-server/media.repo /etc/yum.repos.d/rhel7-server.repo')
        host.execute(
            'echo "baseurl=file:///media/rhel7-server/"' ' >> /etc/yum.repos.d/rhel7-server.repo'
        )
        host.execute('')
        host.execute('mkdir /media/sat6')
        host.execute('mount -o loop $(ls Satellite*.iso) /media/sat6')

        # temporary solution of too new rhel template
        # with correct rhel version this should do yum update
        host.execute(
            'yum -y downgrade '
            ' grub2 grub2-common grub2-pc grub2-pc-modules'
            ' grub2-tools grub2-tools-extra grub2-tools-minimal'
            ' glibc glibc-common'
            ' rpm rpm-libs rpm-python rpm-build-libs'
            ' libmount krb5-libs libuuid libblkid util-linux libsmartcols'
            ' nss nss-softokn nss-sysinit nss-tools nss-softokn-freebl'
            ' python python-libs'
        )
        _enable_sat_ports_fw(host)

        yield host


@pytest.fixture
def rhel_host_connected(request):
    """A function-level fixture that provides a host which is ready for connected installation"""
    with VMBroker(**host_conf(request), host_classes={'host': Host}) as host:
        # subscribe to rhn
        host.execute(
            'subscription-manager register --force'
            f' --user={settings.subscription.rhn_username}'
            f' --password={settings.subscription.rhn_password}'
        )
        host.execute(f'subscription-manager attach --pool={settings.subscription.rhn_poolid}')
        host.execute('subscription-manager repos --disable "*"')
        host.execute(
            'subscription-manager repos'
            ' --enable=rhel-7-server-rpms'
            ' --enable=rhel-7-server-satellite-6.10-rpms'
            ' --enable=rhel-7-server-satellite-maintenance-6-rpms'
            ' --enable=rhel-server-rhscl-7-rpms'
            ' --enable=rhel-7-server-ansible-2.9-rpms'
        )
        host.execute('yum -y update')
        _enable_sat_ports_fw(host)

        yield host

        host.execute('subscription-manager unregister')


# Notes for installer testing:
# Perhaps there is a convenient log analyzer library out there
# that can parse logs? It would be better (and possibly less
# error-prone) than simply grepping for ERROR/FATAL
@pytest.mark.skip_if_not_set('installer')
def test_positive_server_disconnected_installation(rhel_host_disconnected):
    """Can install product from ISO

    :id: 38c08646-9f71-48d9-a9c2-66bd94c3e5bb

    :expectedresults: Disconnected install from ISO is successful.

    :CaseAutomation: Automated
    """
    host = rhel_host_disconnected
    host.execute('cd /media/sat6 && ./install_packages')
    installer_obj = InstallerCommand(installer_opts=installer_params)
    command_output = host.execute(installer_obj.get_command())
    assert 'Success!' in command_output.stdout


@pytest.mark.skip_if_not_set('installer')
def test_positive_server_connected_installation(rhel_host_connected):
    """Can install product from ISO

    :id: 8a9822e8-e401-40d2-b0b6-8dc41337150e

    :expectedresults: Connected installation from CDN is successful.

    :CaseAutomation: Automated
    """
    host = rhel_host_connected
    host.execute('yum -y install satellite')
    installer_obj = InstallerCommand(installer_opts=installer_params)
    command_output = host.execute(installer_obj.get_command())
    assert 'Success!' in command_output.stdout
