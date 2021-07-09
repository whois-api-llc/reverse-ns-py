.. image:: https://img.shields.io/badge/License-MIT-green.svg
    :alt: reverse-ns-py license
    :target: https://opensource.org/licenses/MIT

.. image:: https://img.shields.io/pypi/v/reverse-ns.svg
    :alt: reverse-ns-py release
    :target: https://pypi.org/project/reverse-ns

.. image:: https://github.com/whois-api-llc/reverse-ns-py/workflows/Build/badge.svg
    :alt: reverse-ns-py build
    :target: https://github.com/whois-api-llc/reverse-ns-py/actions

========
Overview
========

The client library for
`Reverse NS API <https://reverse-ns.whoisxmlapi.com/>`_
in Python language.

The minimum Python version is 3.6.

Installation
============

.. code-block:: shell

    pip install reverse-ns

Examples
========

Full API documentation available `here <https://reverse-ns.whoisxmlapi.com/api/documentation/making-requests>`_

Create a new client
-------------------

.. code-block:: python

    from reversens import *

    client = Client('Your API key')

Make basic requests
-------------------

.. code-block:: python

    # Get categories for a domain name.
    response = client.get('ns.google.com')
    for row in response.result:
        print("Domain: " + row.name)

Advanced usage
-------------------

Extra request parameters

.. code-block:: python

    # Iterating over all pages
    # Specify the target name server.
    client.name_server = "ns2.google.com"

    # Now you can use the `Client` instance as an iterable object
    for page in client:
        # Precess the data:
        for row in page.result:
            print(row.name)

    # You can access the last response object via `last_result` property
    print(client.last_result.size)
    # Please note, that `client.get_raw(...)` method doesn't
    # update value of the `last_result` field.
    # Also, `iter(client)` will reset the `last_result` value to None

    # Getting raw API response in XML
    xml = client.get_raw('ns.google.com', output_format=Client.XML_FORMAT)

Using Response model reference
------------------------------

.. code-block:: python

    response = client.get('....')

    # Getting list of domains
    response.result
    # Checking the size of the domain list
    response.size
    # Checking if there is a next page
    if response.has_next():
        ....

    # `current_page` shows the `search_from` value
    ...
    r = client.get(ns='ns', search_from='last.domain.of.the.previous.page.com')
    print(r.current_page)
    # >>'last.domain.of.the.previous.page.com'
