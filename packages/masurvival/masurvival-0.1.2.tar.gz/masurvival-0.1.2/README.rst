***************
MASurvival
***************

MASurvival (Missingness-Avoiding Survival Forest) is a Python module for survival analysis
built on top of `scikit-learn <https://scikit-learn.org/>`_ and based on `scikit-survival <https://github.com/sebp/scikit-survival>`_.
It extends scikit-survival with missingness-avoidance regularization, allowing survival analysis
models to better handle missing data by penalizing splits on features with missing values.

**Key Feature**: The `alpha` parameter in `RandomSurvivalForest` penalizes splits on features with missing values,
making the model more robust to missing data without requiring imputation.

=======================
About Survival Analysis
=======================

The objective in survival analysis (also referred to as time-to-event or reliability analysis)
is to establish a connection between covariates and the time of an event.
What makes survival analysis differ from traditional machine learning is the fact that
parts of the training data can only be partially observed – they are *censored*.

For instance, in a clinical study, patients are often monitored for a particular time period,
and events occurring in this particular period are recorded.
If a patient experiences an event, the exact time of the event can
be recorded – the patient’s record is uncensored. In contrast, right censored records
refer to patients that remained event-free during the study period and
it is unknown whether an event has or has not occurred after the study ended.
Consequently, survival analysis demands for models that take
this unique characteristic of such a dataset into account.

============
Requirements
============

- Python 3.10 or later
- ecos
- joblib
- numexpr
- numpy
- osqp
- pandas 2.0.0 or later
- scikit-learn 1.6 or 1.7
- scipy
- C/C++ compiler

============
Installation
============

Install MASurvival from PyPI::

  pip install masurvival

Or install from source::

  git clone https://github.com/anli66/masurvival
  cd masurvival
  pip install -e .

========
Examples
========

MASurvival provides a drop-in replacement for `RandomSurvivalForest` from scikit-survival with
an additional `alpha` parameter for missingness-avoidance regularization::

  from masurvival.ensemble import RandomSurvivalForest
  from masurvival.metrics import concordance_index_censored

  # Create model with missingness-avoidance regularization
  rsf = RandomSurvivalForest(
      n_estimators=100,
      alpha=1.0,  # Penalty for splits on features with missing values
      random_state=42
  )

  rsf.fit(X_train, y_train)
  predictions = rsf.predict(X_test)

================
Help and Support
================

**Documentation**

- Based on scikit-survival documentation: https://scikit-survival.readthedocs.io/
- For MASurvival-specific features, see the source code and examples.



==========
References
==========

MASurvival is based on scikit-survival. Please cite the original scikit-survival paper:

  S. Pölsterl, "scikit-survival: A Library for Time-to-Event Analysis Built on Top of scikit-learn,"
  Journal of Machine Learning Research, vol. 21, no. 212, pp. 1–6, 2020.

.. code::

  @article{sksurv,
    author  = {Sebastian P{\"o}lsterl},
    title   = {scikit-survival: A Library for Time-to-Event Analysis Built on Top of scikit-learn},
    journal = {Journal of Machine Learning Research},
    year    = {2020},
    volume  = {21},
    number  = {212},
    pages   = {1-6},
    url     = {http://jmlr.org/papers/v21/20-729.html}
  }

**Note**: MASurvival extends scikit-survival with missingness-avoidance regularization.
If you use MASurvival in your research, please also cite this work appropriately.

.. code::

  @article{masurvival,
    author  = {Aneta Lisowska},
    title   = {MASurvival: Missingness-Avoiding Survival Forest},
    year    = {2025},
  }


