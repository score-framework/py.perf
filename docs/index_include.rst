.. module:: score.perf
.. role:: faint
.. role:: confkey

**********
score.perf
**********

This module will help you identify bottle-necks in your applications. It
operates by capturing a snapshot of the current stack and rendering it to an
interactive SVG file using the external `flamegraph`_ binary. This clever
method was found in `Eben Freeman's post on Nylas' blog`__.

.. _flamegraph: https://github.com/brendangregg/FlameGraph
__ https://nylas.com/blog/performance

Quickstart
==========

Add this module to your modules list and it will generate an SVG file in the
current folder, which you can inspect in a modern browser. That's it.

API
===

Configuration
-------------

.. autofunction:: score.perf.init
