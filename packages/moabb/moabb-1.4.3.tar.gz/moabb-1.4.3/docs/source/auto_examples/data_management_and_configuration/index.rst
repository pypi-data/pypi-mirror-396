

.. _sphx_glr_auto_examples_data_management_and_configuration:

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


.. toctree::
   :hidden:

   /auto_examples/data_management_and_configuration/noplot_load_model
   /auto_examples/data_management_and_configuration/plot_bids_conversion
   /auto_examples/data_management_and_configuration/plot_changing_download_directory
   /auto_examples/data_management_and_configuration/plot_disk_cache
   /auto_examples/data_management_and_configuration/plot_explore_paradigm
   /auto_examples/data_management_and_configuration/plot_fixed_interval_windows

