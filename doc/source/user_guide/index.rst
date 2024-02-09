.. _user_guide:

User guide
==========

This section walks you through the basics of how to interact with HPS.
For more elaborate examples, see :ref:`Examples <examples>`. For descriptions
of PyHPS endpoints, see :ref:`API reference <api_reference>`.

To reproduce the code samples provided in this section, you must have these
prerequisites:

- A running Ansys HPS installation. For more information, see the
  `Ansys HPC Platform Services Guide <https://ansyshelp.ansys.com/account/secured?returnurl=/Views/Secured/prod_page.html?pn=Ansys%20HPC%20Platform%20Services&pid=HpcPlatformServices&lang=en>`_
  in the Ansys Help.
- A Python shell with PyHPS installed. For more information, see :ref:`getting_started`.

..
   This toctreemust be a top level index to get it to show up in
   pydata_sphinx_theme

.. toctree::
   :maxdepth: 1
   :hidden:

   query_parameters
   exceptions
   dcs_migration

Connect to an HPS deployment
----------------------------

You start by connecting to an HPS deployment running on the localhost with the default username and password:

.. code-block:: python

    from ansys.hps.client import Client
    from ansys.hps.client.jms import JmsApi, ProjectApi
    
    client = Client(url="https://localhost:8443/hps", username="repuser", password="repuser")  

    # check which JMS version the server is running    
    jms_api = JmsApi(client)
    print(jms_api.get_api_info()['build']['version'])

    # get all projects
    projects = jms_api.get_projects()

Once connected, you can query project statistics to find out how many jobs are currently running:

.. code-block:: python

    projects = jms_api.get_projects(statistics=True)
    num_running_jobs = sum(p.statistics["eval_status"]["running"] for p in projects)

Create a project
----------------

The MAPDL motorbike frame example consists of an Ansys Mechanical APDL beam model of a
tubular steel trellis motorbike frame. This example is more fully described in the :ref:`example_mapdl_motorbike_frame`
example.

#. Download the :download:`ZIP file <../../../build/mapdl_motorbike_frame.zip>` for the MAPDL motorbike frame example.

   This file contains the project setup script for creating the project and the project's data files.

#. Use a tool like 7-Zip to extract the files.

#. To create the project, run the ``project_setup.py`` script::

    $ python path_to_download_folder\mapdl_motorbike_frame\project_setup.py

.. note::
    By default, the script tries to connect to the HPS server running on the localhost with the default
    username and password. If your HPS server is hosted at a different URL or you want to specify different
    credentials, adjust the script before running it. 


Objects versus dictionaries
---------------------------

By setting ``as_objects=False``, most ``get``, ``create``, and ``update`` functions can return
dictionaries rather than class objects. This is especially useful when the returned data needs
to be further manipulated by popular packages such as `NumPy <https://numpy.org/>`_ and
`pandas <https://pandas.pydata.org/>`_.  

.. code-block:: python
    
    import pandas

    project = jms_api.get_project_by_name(name="Mapdl Motorbike Frame") 

    # Get parameter values for all evaluated jobs
    jobs = project_api.get_jobs(fields=["id", "values"], eval_status="evaluated", as_objects=False)

    # Import jobs data into a flat dataframe
    df = pandas.json_normalize(jobs)

    # Output
    #                         id  values.mapdl_cp_time  values.mapdl_elapsed_time  values.mapdl_elapsed_time_obtain_license  values.max_stress  ...  values.tube6 values.tube7 values.tube8 values.tube9 values.weight
    # 0   02qoqedl8QCjkuLcqCi10Q                 0.500                       24.0                                      21.9        1010.256091  ...             3            1            1            2      3.027799
    # 1   02qoqedlDMO1LrSGoHQqnT                 0.406                       23.0                                      21.5         227.249112  ...             2            3            3            2     11.257201
    # 2   02qoqedlApzJZd7fQSQIJg                 0.438                       24.0                                      21.2         553.839050  ...             3            2            1            2      6.358393
    # 3   02qoqedlGMYZi7YBive78D                 0.469                       25.0                                      22.9         162.944726  ...             1            1            1            3      9.919099
    # 4   02qoqedlKBzRz939iDCCex                 0.391                       25.0                                      22.6         218.976121  ...             3            2            2            2      6.884490
    # 5   02qoqedlLfvwuA4uaf5GKR                 0.406                       24.0                                      22.4         455.888101  ...             1            3            1            2      7.346944
    # 6   02qoqedlLvoSgPoLxla8F9                 0.391                       27.0                                      25.2         292.885562  ...             1            1            1            3      6.759635
    # 7   02qoqedlOKg8Vg5AlTrji6                 0.484                       28.0                                      26.2         377.721100  ...             1            1            3            2      5.952097
    # 8   02qoqedlRtDwuw2uTQ99Vq                 0.469                       28.0                                      25.9         332.336753  ...             1            3            2            2      7.463696
    # 9   02qoqedlPYyGRTivqB5vxf                 0.453                       27.0                                      25.5         340.147675  ...             3            2            2            3      6.631538
    # 10  02qoqedlN1ebRV77zuUVYd                 0.453                       28.0                                      25.5         270.691391  ...             2            2            1            3      8.077236


Set failed jobs to pending 
--------------------------

Query a specific project and set its failed jobs (if any) to pending:

.. code-block:: python
    
    project = jms_api.get_project_by_name(name="Mapdl Motorbike Frame") 
    jobs = project_api.get_jobs() 

    failed_jobs = [job for job in jobs if job.eval_status == "failed"]
    
    for job in failed_jobs:
        job.eval_status = "pending"
    failed_jobs = project_api.update_jobs(failed_jobs)
  

Modify a job definition
-----------------------

Query an existing job definition, modify it, and send it back to the server:

.. code-block:: python

    project = jms_api.get_project_by_name(name="Mapdl Motorbike Frame") 

    # get currently active job_definition
    job_def = project_api.get_job_definitions(active=True)[0]
    
    # Update the lower limit of a parameter
    parameter_id = job_def.parameter_definition_ids[0]
    parameter_def = project_api.get_parameter_definitions(id=parameter_id)[0]
    print(parameter_def)
    # {
    #   "id": "02qoqeciKZxk3Ua4QjPwue",
    #   "name": "tube1_radius",
    #   "mode": "input",
    #   "type": "float",
    #   "default": 12.0,
    #   "lower_limit": 4.0,
    #   "upper_limit": 20.0,
    #   "cyclic": false
    # }
    parameter_def.lower_limit = 2.5

    # send the updated job_definition to the server
    project_api.update_parameter_definitions([parameter_def])


Delete some jobs
----------------

Query for all jobs that have timed out and then delete them.

.. code-block:: python

    project = jms_api.get_project_by_name(name="Mapdl Motorbike Frame") 

    jobs = project_api.get_jobs(fields=['id'], eval_status="timeout") 
    project_api.delete_jobs(jobs)


Query the number of evaluators
------------------------------

Query for the number of Windows and Linux evaluators connected to the HPS server:

.. code-block:: python
    
    rms_api = RmsApi(client)
    evaluators = rms_api.get_evaluators()

    # print number of Windows and Linux evaluators connected to the HPS server
    print( len([e for e in evaluators if e.platform == "windows" ]) )
    print( len([e for e in evaluators if e.platform == "linux" ]) )


Replace a file in a project
---------------------------

Get file definitions from an existing project's job definition and replace the first file:

.. code-block:: python

  job_def = project_api.get_job_definitions(active=True)[0]
  files = project_api.get_files()
  file = files[0]
  file.src = r"D:\local_folder\my_project\input_file.xyz"
  project.update_files([file])

Modify and create users
-----------------------

Administrative users with the Keycloak "manage-users" role can create users as well as modify or delete users: 

.. code-block:: python

    from ansys.hps.client import Client
    from ansys.hps.client.auth import AuthApi, User
    
    client = Client(url="https://localhost:8443/hps/", username="repadmin", password="repadmin")
    auth_api = AuthApi(client)

    # modify the default password of the repadmin user
    default_user = auth_api.get_users()[0]
    default_user.password = 'new_password'
    auth_api.update_user(default_user)

    # create a new non-admin user
    new_user = User(username='test_user', password='dummy', 
                    email='test_user@test.com', fullname='Test User')
    new_user = auth_api.create_user(new_user)
    print(new_user)
    # {
    #   "id": "f9e068d7-4962-45dc-92a4-2273246039da",
    #   "username": "test_user",
    #   "email": "test_user@test.com"
    # }

    new_user.password = "new_password"
    auth_api.update_user(new_user)
