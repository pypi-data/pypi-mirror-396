==================
pytest-texts-score
==================

.. image:: https://img.shields.io/pypi/v/pytest-texts-score.svg
    :target: https://pypi.org/project/pytest-texts-score
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-texts-score.svg
    :target: https://pypi.org/project/pytest-texts-score
    :alt: Python versions

.. image:: https://github.com/VodilaPat/pytest-texts-score/actions/workflows/pypi.yml/badge.svg
    :target: https://github.com/VodilaPat/pytest-texts-score/actions/workflows/pypi.yml
    :alt: Build Status

A **pytest plugin for semantic text similarity scoring** using Large Language Models (LLMs).

It enables robust assertions over *meaning*, not surface text, making it ideal for validating
LLM outputs, RAG systems, summaries, and other generated content.

The plugin evaluates similarity by prompting an LLM to extract and answer factual questions,
producing **Precision (Completeness)**, **Recall (Correctness)**, and **F1** scores.

----

Features
--------

* ✔ **Semantic comparison** beyond keyword matching  
* ✔ **Standard IR metrics**: F1, Precision, Recall  
* ✔ **Azure OpenAI support** via pytest configuration  
* ✔ **Readable aliases**: *completeness* ↔ precision, *correctness* ↔ recall  
* ✔ **CI-friendly aggregation** to reduce LLM variance  

----

Requirements
------------

* Python ``>=3.10,<4.0``
* pytest ``>=8.4.2``
* Azure OpenAI subscription with a deployed model (e.g., GPT-4)

----

Installation
------------

Install from PyPI:

::

    pip install pytest-texts-score

----

Configuration
-------------

Configuration is provided via ``pytest.ini`` or overridden with CLI arguments.

Required settings
~~~~~~~~~~~~~~~~~

* ``llm-api-key`` — Azure OpenAI API key
* ``llm-endpoint`` — Azure OpenAI resource endpoint
* ``llm-api-version`` — API version (e.g. ``2024-05-01``)
* ``llm-deployment`` — Deployment name
* ``llm-model`` — Model identifier (e.g. ``gpt-4``)

Optional settings
~~~~~~~~~~~~~~~~~

* ``llm-max-tokens`` — Maximum response tokens (default: ``8192``)

Example ``pytest.ini``
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

    [pytest]
    llm_api_key = YOUR_API_KEY
    llm_endpoint = https://your-resource.openai.azure.com/
    llm_api_version = 2024-05-01
    llm_deployment = your-deployment
    llm_model = gpt-4
    llm_max_tokens = 8192

Override any value via CLI:

::

    pytest --llm-temperature=0.5

----

Usage
-----

You can use the plugin either by **direct imports** or via the **``texts_score`` fixture**.

Direct import
~~~~~~~~~~~~~

.. code-block:: python

    from pytest_texts_score import texts_expect_f1_equal

    def test_similarity():
        expected = "The quick brown fox jumps over a dog."
        actual = "A fast brown fox leaps over a dog."

       exts_expect_f1_equal(expected, actual, 1.0)

Fixture-based usage
~~~~~~~~~~~~~~~~~~~

The ``texts_score`` fixture exposes all assertion helpers in a dictionary.

.. code-block:: python

    def test_similarity(texts_score):
        expected = "The quick brown fox jumps over a dog."
        actual = "A fast brown fox leaps over a dog."

       texts_score["expect_f1_equal"](expected, actual, 1.0)

----


Documentation
-------------
Documentation is availbe at `documentation`_


----


Available Assertions
--------------------

Metrics overview
~~~~~~~~~~~~~~~~

• **Recall (Correctness)**  
  Measures how much information from the *expected* text is present in the *given* text.

• **Precision (Completeness)**  
  Measures how much information in the *given* text is supported by the *expected* text.

• **F1 score**  
  Harmonic mean of precision and recall.

----

Single-run assertions
~~~~~~~~~~~~~~~~~~~~~

These execute **one LLM evaluation**.  
``*_equal`` variants are convenience wrappers around ``*_range``.

▶ F1 score
^^^^^^^^^^

* ``texts_expect_f1_equal``
* ``texts_expect_f1_range``

▶ Precision / Completeness
^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``texts_expect_precision_equal``
* ``texts_expect_precision_range``
* ``texts_expect_completeness_equal`` *(alias)*
* ``texts_expect_completeness_range`` *(alias)*

▶ Recall / Correctness
^^^^^^^^^^^^^^^^^^^^^^

* ``texts_expect_recall_equal``
* ``texts_expect_recall_range``
* ``texts_expect_correctness_equal`` *(alias)*
* ``texts_expect_correctness_range`` *(alias)*

----

Aggregated assertions
~~~~~~~~~~~~~~~~~~~~~

These perform **multiple evaluations** and aggregate the result.
Recommended for CI/CD pipelines to reduce LLM nondeterminism.

Supported aggregations: ``min``, ``max``, ``median``, ``mean`` / ``average``.

▶ F1 score
^^^^^^^^^^

* ``texts_agg_f1_min``
* ``texts_agg_f1_max``
* ``texts_agg_f1_median``
* ``texts_agg_f1_mean``
* ``texts_agg_f1_average``

▶ Precision / Completeness
^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``texts_agg_precision_min``
* ``texts_agg_precision_max``
* ``texts_agg_precision_median``
* ``texts_agg_precision_mean``
* ``texts_agg_precision_average``

* ``texts_agg_completeness_min``
* ``texts_agg_completeness_max``
* ``texts_agg_completeness_median``
* ``texts_agg_completeness_mean``
* ``texts_agg_completeness_average``

▶ Recall / Correctness
^^^^^^^^^^^^^^^^^^^^^^

* ``texts_agg_recall_min``
* ``texts_agg_recall_max``
* ``texts_agg_recall_median``
* ``texts_agg_recall_mean``
* ``texts_agg_recall_average``

* ``texts_agg_correctness_min``
* ``texts_agg_correctness_max``
* ``texts_agg_correctness_median``
* ``texts_agg_correctness_mean``
* ``texts_agg_correctness_average``

----

License
-------

Distributed under the terms of the `MIT`_ license.

----

Issues & Support
----------------

Please report bugs or feature requests via the GitHub issue tracker:
`file an issue`_

----

.. _`MIT`: https://opensource.org/licenses/MIT
.. _`documentation`: https://vodilapat.github.io/pytest-texts-score/html/index.html
.. _`file an issue`: https://github.com/VodilaPat/pytest-texts-score/issues
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
