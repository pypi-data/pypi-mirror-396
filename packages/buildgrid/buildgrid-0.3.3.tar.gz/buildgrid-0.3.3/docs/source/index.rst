BuildGrid 
=========

.. _what-is-buildgrid:

What is BuildGrid?
------------------

BuildGrid is a remote execution and caching service which implements Google's
`Remote Execution API`_ and the `Remote Workers API`_.

The project's goal is to be able to execute build jobs remotely on a grid of
computers in order to massively speed up build times. Worker machines on the
grid should be able to run with different environments.

BuildGrid works with clients such as `Bazel`_, `BuildStream`_, and `RECC`_, and
is designed to be able to work with any client that conforms to the above API
protocols.

Worker machines connect to the grid via bot processes which implement the
`Remote Workers API`_ specification. These bots actually execute the jobs on
the backend whilst BuildGrid is responsible for scheduling and storage. The
`BuildBox`_ ecosystem provides a suite of bots and sandboxing tools that work
with the Workers API and can be used with BuildGrid.

.. _Remote Execution API: https://github.com/bazelbuild/remote-apis
.. _Remote Workers API: https://docs.google.com/document/d/1s_AzRRD2mdyktKUj2HWBn99rMg_3tcPvdjx3MPbFidU/edit#heading=h.1u2taqr2h940
.. _BuildStream: https://buildstream.build
.. _Bazel: https://bazel.build
.. _RECC: https://gitlab.com/BuildGrid/buildbox/buildbox/-/tree/master/recc
.. _Trexe: https://gitlab.com/BuildGrid/buildbox/buildbox/-/tree/master/trexe
.. _BuildBox: https://buildgrid.gitlab.io/buildbox/buildbox-home/

.. _quickstart:

Quickstart
----------

To quickly try out BuildGrid, we provide pre-built container images, and a
simple ``docker compose`` configuration example which starts up BuildGrid's
services at ``localhost:50051``.

.. code-block:: shell

    git clone https://gitlab.com/BuildGrid/buildgrid
    cd buildgrid
    docker compose -f docker-compose-examples/all-in-one.yml up

.. _contents:

.. toctree::
   :maxdepth: 1
   :caption: Deploying BuildGrid

   operation/architecture.rst
   operation/configuration.rst
   operation/monitoring.rst
   operation/workers.rst
   operation/auth.rst
   operation/indexed_cas.rst
   operation/cas_cleanup.rst
   operation/reference_cli.rst

.. toctree::
   :maxdepth: 1
   :caption: Using BuildGrid

   user/getting_started.rst
   user/using.rst

.. toctree::
   :maxdepth: 1
   :caption: Developing BuildGrid

   developer/installation_developer.rst
   developer/notes_for_developers.rst
   developer/reference_api.rst
   developer/contributing.rst
   developer/architecture.rst


Resources
---------

- `Homepage`_
- `GitLab repository`_
- `Bug tracking`_
- `Slack channel`_ [`invite link`_]

.. _Homepage: https://buildgrid.build
.. _GitLab repository: https://gitlab.com/BuildGrid/buildgrid
.. _Bug tracking: https://gitlab.com/BuildGrid/buildgrid/boards
.. _Slack channel: https://buildteamworld.slack.com/messages/CC9MKC203
.. _invite link: https://join.slack.com/t/buildteamworld/shared_invite/zt-3gsdqj3z6-YTwI9ZWZxvE522Nl1TU8sw
