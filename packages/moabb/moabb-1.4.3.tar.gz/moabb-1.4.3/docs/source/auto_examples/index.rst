:orphan:

MOABB Examples
----------------

Explore quick, practical examples that demonstrate MOABB’s key modules and techniques.

Use these concise code samples as inspiration for your own analysis tasks.

For additional details, see the Getting Started tutorials or API reference.

The rest of the MOABB documentation pages are shown in the navigation menu,
including the :doc:`list of example datasets<../dataset_summary>`, :doc:`how to cite MOABB <../cite>`, and explanations of the
external library dependencies that MOABB uses, including Deep Learning, Code Carbon,
Docs and others.

.. toctree::
   :hidden:



.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. thumbnail-parent-div-close

.. raw:: html

    </div>

Getting Started!
-----------------
Tutorials: Step-by-step introductions to MOABB’s usage and concepts. These cover getting started with MOABB, using multiple datasets,
benchmarking pipelines, and adding custom datasets in line with best practices for reproducible research.

Each tutorial focuses on a fundamental workflow for using moabb in your research!

.. toctree::
   :hidden:



.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This tutorial takes you through a basic working example of how to use this codebase, including all the different components, up to the results generation. If you&#x27;d like to know about the statistics and plotting, see the next tutorial.">

.. only:: html

  .. image:: /auto_examples/tutorials/images/thumb/sphx_glr_tutorial_0_plot_getting_started_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_tutorials_tutorial_0_plot_getting_started.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Tutorial 0: Getting Started</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="In this example, we will go through all the steps to make a simple BCI classification task, downloading a dataset and using a standard classifier. We choose the dataset 2a from BCI Competition IV, a motor imagery task. We will use a CSP to enhance the signal-to-noise ratio of the EEG epochs and a LDA to classify these signals.">

.. only:: html

  .. image:: /auto_examples/tutorials/images/thumb/sphx_glr_tutorial_1_simple_example_motor_imagery_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_tutorials_tutorial_1_simple_example_motor_imagery.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Tutorial 1: Simple Motor Imagery</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="We extend the previous example to a case where we want to analyze the score of a classifier with three different MI datasets instead of just one. As before, we begin by importing all relevant libraries.">

.. only:: html

  .. image:: /auto_examples/tutorials/images/thumb/sphx_glr_tutorial_2_using_mulitple_datasets_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_tutorials_tutorial_2_using_mulitple_datasets.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Tutorial 2: Using multiple datasets</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="In this last part, we extend the previous example by assessing the classification score of not one but three classification pipelines.">

.. only:: html

  .. image:: /auto_examples/tutorials/images/thumb/sphx_glr_tutorial_3_benchmarking_multiple_pipelines_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_tutorials_tutorial_3_benchmarking_multiple_pipelines.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Tutorial 3: Benchmarking multiple pipelines</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="Tutorial 4: Creating a dataset class">

.. only:: html

  .. image:: /auto_examples/tutorials/images/thumb/sphx_glr_tutorial_4_adding_a_dataset_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_tutorials_tutorial_4_adding_a_dataset.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Tutorial 4: Creating a dataset class</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="Tutorial 5: Creating a dataset class">

.. only:: html

  .. image:: /auto_examples/tutorials/images/thumb/sphx_glr_tutorial_5_build_a_custom_dataset_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_tutorials_tutorial_5_build_a_custom_dataset.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Tutorial 5: Creating a dataset class</div>
    </div>


.. thumbnail-parent-div-close

.. raw:: html

    </div>

Paradigm-Specific Evaluation Examples (Within- & Cross-Session)
---------------------------------------------------------------

These examples demonstrate how to evaluate BCI algorithms on different paradigms (Motor Imagery, P300, SSVEP), covering within-session (training and testing on the same session) and
transfer scenarios like cross-session or cross-subject evaluations.
They reflect best practices in assessing model generalization across sessions and subjects in EEG research.

.. toctree::
   :hidden:



.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example show how to perform a cross session motor imagery analysis on the very popular dataset 2a from the BCI competition IV.">

.. only:: html

  .. image:: /auto_examples/paradigm_examples/images/thumb/sphx_glr_plot_cross_session_motor_imagery_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_paradigm_examples_plot_cross_session_motor_imagery.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Cross-Session Motor Imagery</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to perform a cross-session analysis on two MI datasets using a CSP+LDA pipeline">

.. only:: html

  .. image:: /auto_examples/paradigm_examples/images/thumb/sphx_glr_plot_cross_session_multiple_datasets_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_paradigm_examples_plot_cross_session_multiple_datasets.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Cross-Session on Multiple Datasets</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="- Riemannian Geometry - CCA - TRCA - MsetCCA">

.. only:: html

  .. image:: /auto_examples/paradigm_examples/images/thumb/sphx_glr_plot_cross_subject_ssvep_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_paradigm_examples_plot_cross_subject_ssvep.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Cross-Subject SSVEP</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to extract the epochs from the P300-VR dataset of a given subject and then classify them using Riemannian Geometry framework for BCI. We compare the scores in the VR and PC conditions, using different epoch size.">

.. only:: html

  .. image:: /auto_examples/paradigm_examples/images/thumb/sphx_glr_plot_vr_pc_p300_different_epoch_size_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_paradigm_examples_plot_vr_pc_p300_different_epoch_size.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Changing epoch size in P300 VR dataset</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to perform a within session analysis on three different P300 datasets.">

.. only:: html

  .. image:: /auto_examples/paradigm_examples/images/thumb/sphx_glr_plot_within_session_p300_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_paradigm_examples_plot_within_session_p300.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Within Session P300</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This Example shows how to perform a within-session SSVEP analysis on the MAMEM dataset 3, using a CCA pipeline.">

.. only:: html

  .. image:: /auto_examples/paradigm_examples/images/thumb/sphx_glr_plot_within_session_ssvep_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_paradigm_examples_plot_within_session_ssvep.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Within Session SSVEP</div>
    </div>


.. thumbnail-parent-div-close

.. raw:: html

    </div>

Data Management and Configuration
---------------------------------

Utility examples focused on data handling, configuration, and environment setup in MOABB. These scripts help ensure reproducible research through proper data management (download directories, standard formats) and optimized processing.

.. toctree::
   :hidden:



.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to use load the pretrained pipeline in MOABB.">

.. only:: html

  .. image:: /auto_examples/data_management_and_configuration/images/thumb/sphx_glr_noplot_load_model_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_data_management_and_configuration_noplot_load_model.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Load Model (Scikit) with MOABB</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="The Brain Imaging Data Structure (BIDS) format is standard for storing neuroimaging data. It follows fixed principles to facilitate the sharing of neuroimaging data between researchers.">

.. only:: html

  .. image:: /auto_examples/data_management_and_configuration/images/thumb/sphx_glr_plot_bids_conversion_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_data_management_and_configuration_plot_bids_conversion.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Convert a MOABB dataset to BIDS</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This is a minimal example to demonstrate how to change the default data download directory to a custom path/location.">

.. only:: html

  .. image:: /auto_examples/data_management_and_configuration/images/thumb/sphx_glr_plot_changing_download_directory_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_data_management_and_configuration_plot_changing_download_directory.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Change Download Directory</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how intermediate data processing states can be cached on disk to speed up the loading of this data in subsequent calls.">

.. only:: html

  .. image:: /auto_examples/data_management_and_configuration/images/thumb/sphx_glr_plot_disk_cache_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_data_management_and_configuration_plot_disk_cache.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Cache on disk intermediate data processing states</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="A paradigm defines how the raw data will be converted to trials ready to be processed by a decoding algorithm. This is a function of the paradigm used, i.e. in motor imagery one can have two-class, multi-class, or continuous paradigms; similarly, different preprocessing is necessary for ERP vs ERD paradigms.">

.. only:: html

  .. image:: /auto_examples/data_management_and_configuration/images/thumb/sphx_glr_plot_explore_paradigm_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_data_management_and_configuration_plot_explore_paradigm.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Explore Paradigm Object</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to process a dataset using the moabb.paradigms.FixedIntervalWindowsProcessing paradigm. This paradigm creates epochs at fixed intervals, ignoring the stim channel and events of the datasets. Therefore, it is compatible with all the datasets. Unfortunately, this paradigm is not compatible with the MOABB evaluation framework. However, it can be used to process datasets for unsupervised algorithms.">

.. only:: html

  .. image:: /auto_examples/data_management_and_configuration/images/thumb/sphx_glr_plot_fixed_interval_windows_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_data_management_and_configuration_plot_fixed_interval_windows.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Fixed interval windows processing</div>
    </div>


.. thumbnail-parent-div-close

.. raw:: html

    </div>

Benchmarking and Pipeline Evaluation
------------------------------------

Examples focusing on running benchmarks and comparing multiple models or configurations, following MOABB’s evaluation
methodology.
These scripts reflect EEG decoding best practices by evaluating algorithms under consistent conditions and
tracking performance (and even resource usage).

.. toctree::
   :hidden:



.. raw:: html

    <div class="sphx-glr-thumbnails">

.. thumbnail-parent-div-open

.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to use MOABB to track the CO2 footprint using CodeCarbon library. For this example, we will use only one dataset to keep the computation time low, but this benchmark is designed to easily scale to many datasets. Due to limitation of online documentation generation, the results is computed on a local cluster but could be easily replicated on your infrastructure.">

.. only:: html

  .. image:: /auto_examples/how_to_benchmark/images/thumb/sphx_glr_example_codecarbon_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_how_to_benchmark_example_codecarbon.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Benchmarking with MOABB showing the CO2 footprint</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to use MOABB to benchmark a set of pipelines on all available datasets. For this example, we will use only one dataset to keep the computation time low, but this benchmark is designed to easily scale to many datasets.">

.. only:: html

  .. image:: /auto_examples/how_to_benchmark/images/thumb/sphx_glr_plot_benchmark_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_how_to_benchmark_plot_benchmark.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Benchmarking with MOABB</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="This example shows how to use MOABB to benchmark a set of pipelines on all available datasets. In particular we run the Gridsearch to select the best hyperparameter of some pipelines and save the gridsearch. For this example, we will use only one dataset to keep the computation time low, but this benchmark is designed to easily scale to many datasets.">

.. only:: html

  .. image:: /auto_examples/how_to_benchmark/images/thumb/sphx_glr_plot_benchmark_grid_search_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_how_to_benchmark_plot_benchmark_grid_search.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Benchmarking with MOABB with Grid Search</div>
    </div>


.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="Tutorial: Within-Session Splitting on Real MI Dataset">

.. only:: html

  .. image:: /auto_examples/how_to_benchmark/images/thumb/sphx_glr_plot_within_session_splitter_thumb.png
    :alt:

  :ref:`sphx_glr_auto_examples_how_to_benchmark_plot_within_session_splitter.py`

.. raw:: html

      <div class="sphx-glr-thumbnail-title">Tutorial: Within-Session Splitting on Real MI Dataset</div>
    </div>


.. thumbnail-parent-div-close

.. raw:: html

    </div>

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
   :includehidden:


   /auto_examples/tutorials/index.rst
   /auto_examples/paradigm_examples/index.rst
   /auto_examples/data_management_and_configuration/index.rst
   /auto_examples/how_to_benchmark/index.rst
   /auto_examples/advanced_examples/index.rst
   /auto_examples/learning_curve/index.rst


.. only:: html

  .. container:: sphx-glr-footer sphx-glr-footer-gallery

    .. container:: sphx-glr-download sphx-glr-download-python

      :download:`Download all examples in Python source code: auto_examples_python.zip </auto_examples/auto_examples_python.zip>`

    .. container:: sphx-glr-download sphx-glr-download-jupyter

      :download:`Download all examples in Jupyter notebooks: auto_examples_jupyter.zip </auto_examples/auto_examples_jupyter.zip>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_
