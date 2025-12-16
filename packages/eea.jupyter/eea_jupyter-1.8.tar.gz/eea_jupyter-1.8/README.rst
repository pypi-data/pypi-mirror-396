==========================
eea.jupyter
==========================
.. image:: https://ci.eionet.europa.eu/buildStatus/icon?job=eea/eea.jupyter/develop
  :target: https://ci.eionet.europa.eu/job/eea/job/eea.jupyter/job/develop/display/redirect
  :alt: Develop
.. image:: https://ci.eionet.europa.eu/buildStatus/icon?job=eea/eea.jupyter/master
  :target: https://ci.eionet.europa.eu/job/eea/job/eea.jupyter/job/master/display/redirect
  :alt: Master

The eea.jupyter is a jupyter utility package for EEA.

.. contents::


Installation
============
.. code-block:: console

  pip install eea.jupyter


Usage
=====

.. code-block:: python

  from eea.jupyter import upload_plotly

Uploads or creates a `Chart (interactive)` to a specified `url`. This function accepts any number of keyword arguments.

Parameters:

- :code:`url` (required): The URL of the visualization to be updated or created, e.g. :code:`https://eea.europa.eu/en/sandbox/chart-1`. Default: :code:`None`
- :code:`fig` (required): The figure to be used as part of the visualization. Can accept a :code:`plotly.graph_objs.Figure` or a :code:`dict`. Default: :code:`None`
- :code:`api_url` (optional): The base URL of the plone API, e.g., :code:`https://eea.europa.eu/admin/++api++`. Default:  :code:`/++api++` concatenated to the hostname of the visualization URL, e.g.: if the :code:`url` is :code:`https://biodiversity.eea.europa.eu/en/sandbox/chart-1` then the default value for :code:`api_url` will be :code:`https://biodiversity.eea.europa.eu/admin/++api++`
- :code:`auth_provider` (optional): Provider to be used for authentication. Allowed values: `basic`, `microsoft`. Default: `basic`
- :code:`auth_token` (optional): Token to be used instead of allways authenticating. Default: :code:`None`
- :code:`__ac__key` (optional): Key to be used in cookies if :code:`microsoft` auth_provider is used. Default: :code:`__ac`
- :code:`**metadata` (optional): Any :code:`Chart (interactive)` metadata desired to be customized, e.g., `title`, `description`, `topics`

**Example 1**: how to use it with basic authentication

.. code-block:: python

  # Cell 1 will have some logic to generate a fig
  # Cell 2
  from eea.jupyter import upload_plotly

  url = "https://www.eea.europa.eu/en/sandbox/miu-test/chart-1"

  metadata = {
    "title": "Chart 1 example",
    "description": "This exemplifies how to use upload_plotly"
  }

  upload_plotly(url=url, fig=fig, **metadata)

In this example you specify the visualization that you want to update, if it already exists, or where you want to create it. In case the visualization doesn't exists it will be created inside of :code:`https://www.eea.europa.eu/en/sandbox/miu-test` with the id of :code:`chart-1`.
After calling :code:`upload_plotly` you will be prompted with :code:`username` and :code:`password` inputs.

**Example 2**: how to use it with microsoft authentication

.. code-block:: python

  # Cell 1 will have some logic to generate a fig
  # Cell 2
  from eea.jupyter import upload_plotly

  url = "https://www.eea.europa.eu/en/sandbox/miu-test/chart-1"

  metadata = {
    "title": "Chart 1 example",
    "description": "This exemplifies how to use upload_plotly"
  }

  upload_plotly(url=url, fig=fig, auth_provider="microsoft", __ac__key="__ac__eea", **metadata)

In this example you specify the microsoft auth_provider and also the key of __ac.

After calling :code:`upload_plotly` you will be prompted with :code:`auth_token` input which expects a valid :code:`__ac` token. To get the :code:`__ac` you will need to authenticate on https://www.eea.europa.eu/admin and get the value of :code:`__ac__eea` cookie. You can use a cookie chrome extension to retrive the value of the cookie.

**Example 3**: initialize :code:`auth_token` so that you can pass the authentication input

.. code-block:: python

  # Cell 1 will have some logic to generate a fig
  # Cell 2
  auth_token = input()
  # Cell 3
  from eea.jupyter import upload_plotly

  url = "https://www.eea.europa.eu/en/sandbox/miu-test/chart-1"

  metadata = {
    "title": "Chart 1 example",
    "description": "This exemplifies how to use upload_plotly"
  }

  upload_plotly(url=url, fig=fig, auth_provider="microsoft", __ac__key="__ac__eea", auth_token=auth_token, **metadata)

In this example, firstly, you will be prompted with specifying the value of :code:`auth_token`, which will then be added as a parameter to :code:`upload_plotly`. This allows you to initialize the value of :code:`auth_token` only once, then you can run cell 3 as many times as you like.

Same behaviour regardless of the :code:`auth_provider`.

**Example 4**: passing multiple types of metadata

.. code-block:: python

  # Cell 1 will have some logic to generate a fig
  # Cell 2
  auth_token = input()
  # Cell 3
  from eea.jupyter import upload_plotly

  url = "https://www.eea.europa.eu/en/sandbox/miu-test/chart-1"

  metadata = {
    "title": "Chart 1 example",
    "description": "This exemplifies how to use upload_plotly",
    "topics": ["Agriculture and food"],
    "temporal_coverage": [2011, 2020],
    "geo_coverage": ["Italy"],
    "subjects": ["tag 1"],
    "data_provenance": [
        {"title": "European Environment Agency", "organisation": "EEA", "link": "https://eea.europa.eu"}
    ]
  }

  upload_plotly(url=url, fig=fig, auth_provider="microsoft", __ac__key="__ac__eea", auth_token=auth_token, **metadata)

Metadata
========
In this section you will learn about various metadata that can be specified when calling :code:`upload_plotly`.

- :code:`figure_note` (slate): sets the figure note
- :code:`topics` (list): sets the list of strings for topics (e.g., ["Agriculture and food", "Bathing water quality"])
- :code:`temporal_coverage` (list): sets the list of years for temporal coverage (e.g., [2022, 2023, 2024])
- :code:`geo_coverage` (list): sets the list of strings for geographical coverage (e.g., ["Italy", "Romania"])
- :code:`subjects` (list): sets the list of strings for tags (e.g., ["tag 1", "tag 2"])
- :code:`data_provenance` (list) sets the list of data provenance (e.g., [{ "title": "European Environment Agency", "organization": "EEA", "link": "https://eea.europa.eu"}])

If any of these doesn't meet the required format, you will get an error explaining what is wrong.

If, for example, you specify :code:`topics = ["Agriculture and fod"]` with a typo, you will get an error because the topic is not in the topics vocabulary and a list with the available topics will be printed.

Eggs repository
===============

- https://pypi.python.org/pypi/eea.jupyter
- http://eggrepo.eea.europa.eu/simple


How to contribute
=================
See the `contribution guidelines (CONTRIBUTING.md) <https://github.com/eea/eea.jupyter/blob/main/CONTRIBUTING.md>`_.


Copyright and license
=====================

eea.jupyter (the Original Code) is free software; you can
redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc., 59
Temple Place, Suite 330, Boston, MA 02111-1307 USA.

The Initial Owner of the Original Code is European Environment Agency (EEA).
Portions created by Eau de Web are Copyright (C) 2009 by
European Environment Agency. All Rights Reserved.


Funding
=======

EEA_ - European Environment Agency (EU)

.. _EEA: https://www.eea.europa.eu/
.. _`EEA Web Systems Training`: http://www.youtube.com/user/eeacms/videos?view=1
