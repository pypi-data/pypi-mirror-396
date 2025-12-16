

.. _sphx_glr_auto_examples_advanced_examples:

Advanced examples
-----------------

These examples show various advanced topics:

- using scikit-learn pipeline with MNE inputs
- selecting electrodes or resampling signal
- using filterbank approach in motor imagery
- apply statistics for meta-analysis
- using a gridsearch in within-subject decoding

.. toctree::
   :hidden:



.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This tutorial shows how to use the moabb.analysis.plotting.dataset_bubble_plot function to visualize, at a glance, the number of subjects and sessions in each dataset and the number of trials per session.">

.. only:: html

  .. image:: /auto_examples/advanced_examples/images/thumb/sphx_glr_plot_dataset_bubbles_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_advanced_examples_plot_dataset_bubbles.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Dataset bubble plot</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to plot Dreyer2023A Left-Right Imagery ROC AUC scores obtained with CSP+LDA pipeline versus demographic information of the examined subjects (gender and age) and experimenters (gender).">

.. only:: html

  .. image:: /auto_examples/advanced_examples/images/thumb/sphx_glr_plot_dreyer_clf_scores_vs_subj_info_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_advanced_examples_plot_dreyer_clf_scores_vs_subj_info.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Examples of analysis of a Dreyer2023 A dataset.</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example show a comparison of CSP versus FilterBank CSP on the very popular dataset 2a from the BCI competition IV.">

.. only:: html

  .. image:: /auto_examples/advanced_examples/images/thumb/sphx_glr_plot_filterbank_csp_vs_csp_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_advanced_examples_plot_filterbank_csp_vs_csp.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">FilterBank CSP versus CSP</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example demonstrates how to make a model selection in pipelines for finding the best model parameter, using grid search. Two models are compared, one &quot;vanilla&quot; model with model tuned via grid search.">

.. only:: html

  .. image:: /auto_examples/advanced_examples/images/thumb/sphx_glr_plot_grid_search_withinsession_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_advanced_examples_plot_grid_search_withinsession.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">GridSearch within a session</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to use the Hinss2021 dataset with the resting state paradigm.">

.. only:: html

  .. image:: /auto_examples/advanced_examples/images/thumb/sphx_glr_plot_hinss2021_classification_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_advanced_examples_plot_hinss2021_classification.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Hinss2021 classification example</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to use machine learning pipeline based on MNE Epochs instead of Numpy arrays. This is useful to make the most of the MNE code base and to embed EEG specific code inside sklearn pipelines.">

.. only:: html

  .. image:: /auto_examples/advanced_examples/images/thumb/sphx_glr_plot_mne_and_scikit_estimators_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_advanced_examples_plot_mne_and_scikit_estimators.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">MNE Epochs-based pipelines</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to evaluate a pipeline constructed using the mne-features library [1]_. This library provides sklearn compatible feature extractors for M/EEG data. These features can be used directly in your pipelines.">

.. only:: html

  .. image:: /auto_examples/advanced_examples/images/thumb/sphx_glr_plot_mne_features_pipeline_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_advanced_examples_plot_mne_features_pipeline.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Pipelines using the mne-features library</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example demonstrates how to perform spectral analysis on epochs extracted from a specific subject within the moabb.datasets.Cattan2019_PHMD  dataset.">

.. only:: html

  .. image:: /auto_examples/advanced_examples/images/thumb/sphx_glr_plot_phmd_ml_spectrum_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_advanced_examples_plot_phmd_ml_spectrum.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Spectral analysis of the trials</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="Behind the curtains, these steps are defined in a scikit-learn Pipeline. This pipeline receives raw signals and applies various signal processing steps to construct the final array object and class labels, which will be used to train and evaluate the classifiers.">

.. only:: html

  .. image:: /auto_examples/advanced_examples/images/thumb/sphx_glr_plot_pre_processing_steps_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_advanced_examples_plot_pre_processing_steps.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Playing with the pre-processing steps</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="Within paradigm, it is possible to restrict analysis only to a subset of electrodes and to resample to a specific sampling rate. There is also a utility function to select common electrodes shared between datasets. This tutorial demonstrates how to use this functionality.">

.. only:: html

  .. image:: /auto_examples/advanced_examples/images/thumb/sphx_glr_plot_select_electrodes_resample_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_advanced_examples_plot_select_electrodes_resample.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Select Electrodes and Resampling</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="The MOABB codebase comes with convenience plotting utilities and some statistical testing. This tutorial focuses on what those exactly are and how they can be used.">

.. only:: html

  .. image:: /auto_examples/advanced_examples/images/thumb/sphx_glr_plot_statistical_analysis_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_advanced_examples_plot_statistical_analysis.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Statistical Analysis</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="The following tutorial creates a dataset that contains data in the form of epochs. A special paradigm is provided, which calls an additional method on the dataset so that MOABB can process it correctly. After this, a standard classification is performed.">

.. only:: html

  .. image:: /auto_examples/advanced_examples/images/thumb/sphx_glr_plot_use_an_X_y_dataset_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_advanced_examples_plot_use_an_X_y_dataset.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Using X y data (epoched data) instead of continuous signal</div>
    </div>


.. thumbnail-parent-div-close

.. raw:: html

    </div>


.. toctree::
   :hidden:

   /auto_examples/advanced_examples/plot_dataset_bubbles
   /auto_examples/advanced_examples/plot_dreyer_clf_scores_vs_subj_info
   /auto_examples/advanced_examples/plot_filterbank_csp_vs_csp
   /auto_examples/advanced_examples/plot_grid_search_withinsession
   /auto_examples/advanced_examples/plot_hinss2021_classification
   /auto_examples/advanced_examples/plot_mne_and_scikit_estimators
   /auto_examples/advanced_examples/plot_mne_features_pipeline
   /auto_examples/advanced_examples/plot_phmd_ml_spectrum
   /auto_examples/advanced_examples/plot_pre_processing_steps
   /auto_examples/advanced_examples/plot_select_electrodes_resample
   /auto_examples/advanced_examples/plot_statistical_analysis
   /auto_examples/advanced_examples/plot_use_an_X_y_dataset

