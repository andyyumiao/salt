# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Import python libs
import os

# Import third party libs
import yaml
import logging

# Import salt libs
import salt.utils

__proxyenabled__ = ['*']
log = logging.getLogger(__name__)


def shell():
    '''
    Return the default shell to use on this system
    '''
    # Provides:
    #   shell
    return {'shell': os.environ.get('SHELL', '/bin/sh')}


def config():
    '''
    Return the grains set in the grains file
    '''
    if 'conf_file' not in __opts__:
        return {}
    if os.path.isdir(__opts__['conf_file']):
        if salt.utils.is_proxy():
            gfn = os.path.join(
                    __opts__['conf_file'],
                    'proxy.d',
                    __opts__['id'],
                    'grains'
                    )
        else:
            gfn = os.path.join(
                    __opts__['conf_file'],
                    'grains'
                    )
    else:
        if salt.utils.is_proxy():
            gfn = os.path.join(
                    os.path.dirname(__opts__['conf_file']),
                    'proxy.d',
                    __opts__['id'],
                    'grains'
                    )
        else:
            gfn = os.path.join(
                    os.path.dirname(__opts__['conf_file']),
                    'grains'
                    )
    if os.path.isfile(gfn):
        log.debug('Loading static grains from %s', gfn)
        with salt.utils.fopen(gfn, 'rb') as fp_:
            try:
                return yaml.safe_load(fp_.read())
            except Exception:
                log.warning("Bad syntax in grains file! Skipping.")
                return {}
    return {}
