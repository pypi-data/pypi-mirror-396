

.. _sphx_glr_auto_examples_learning_curve:

Evaluation with learning curve
------------------------------

These examples demonstrate how to make evaluations using only a subset of
available example. For example, if you consider a dataset with 100 trials for
each class, you could evaluate several pipelines by using only a fraction of
these trials. To ensure the robustness of the results, you need to specify the
number of permutations. If you use 10 trials per class and 20 permutations,
each pipeline will be evaluated on a subset of 10 trials chosen randomly, that
will be repeated 20 times with different trial subsets.

.. toctree::
   :hidden:



.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to perform a within session analysis while also creating learning curves for a P300 dataset. Additionally, we will evaluate external code. Make sure to have tdlda installed , which can be pip install git+https://github.com/jsosulski/tdlda.git.">

.. only:: html

  .. image:: /auto_examples/learning_curve/images/thumb/sphx_glr_noplot_learning_curve_p300_external_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_learning_curve_noplot_learning_curve_p300_external.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Within Session P300 with Learning Curve</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to perform a within session motor imagery analysis on the very popular dataset 2a from the BCI competition IV.">

.. only:: html

  .. image:: /auto_examples/learning_curve/images/thumb/sphx_glr_plot_learning_curve_motor_imagery_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_learning_curve_plot_learning_curve_motor_imagery.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Within Session Motor Imagery with Learning Curve</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to perform a within session analysis while also creating learning curves for a P300 dataset.">

.. only:: html

  .. image:: /auto_examples/learning_curve/images/thumb/sphx_glr_plot_learning_curve_p300_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_learning_curve_plot_learning_curve_p300.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Within Session P300 with Learning Curve</div>
    </div>


.. thumbnail-parent-div-close

.. raw:: html

    </div>


.. toctree::
   :hidden:

   /auto_examples/learning_curve/noplot_learning_curve_p300_external
   /auto_examples/learning_curve/plot_learning_curve_motor_imagery
   /auto_examples/learning_curve/plot_learning_curve_p300

