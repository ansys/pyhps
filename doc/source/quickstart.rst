.. _quickstart:

Quickstart
==========

This guide will walk you through the basics of interacting with a REP server. More elaborated examples are available in the :ref:`Examples <examples>` chapter, 
while detailed documentation can be found in the :ref:`Code Documentation <api_reference>`.

To reproduce the code samples provided below, you will need:

- A running REP server, go to the `REP repository <https://github.com/ansys/rep>`_ for instructions.
- A Python shell with ``ansys-rep-client`` installed. If you haven't installed it yet, please refer to the :ref:`Installation <installation>` guide.


Connect to a REP Server 
--------------------------

Let's start by connecting to a REP server running on the localhost with default username and password.

.. code-block:: python

    from ansys.rep.client import Client
    from ansys.rep.client.jms import JmsApi, ProjectApi
    
    client = Client(rep_url="https://localhost:8443/rep", username="repuser", password="repuser")  

    # check which JMS version the server is running    
    jms_api = JmsApi(client)
    print(jms_api.get_api_info()['build']['external_version'])

    # get all projects
    projects = jms_api.get_projects()

Query projects statistics to find out how many jobs are currently running

.. code-block:: python

    projects = jms_api.get_projects(statistics=True)
    num_running_jobs = sum(p.statistics["eval_status"]["running"] for p in projects)

Create a demo project: the MAPDL motorbike frame example
---------------------------------------------------------

Create a project consisting of an Ansys Mechanical APDL beam model 
of a tubular steel trellis motorbike-frame. 

.. only:: builder_html

     The project setup script as well as the data files can be downloaded here :download:`MAPDL Motorbike Frame Project <../../build/mapdl_motorbike_frame.zip>`.
     To create the project you only need to run the `project_setup` script:

::

    $ python path_to_download_folder\mapdl_motorbike_frame\project_setup.py

.. note::
    By default, the script tries to connect to the REP server running on the localhost with default username and password.
    If your REP server is hosted at a different URL or you want to specify different credentials,
    please adjust the script before running it. 


See :ref:`example_mapdl_motorbike_frame` for a detailed description of this example.

Query parameters
----------------

Most ``get`` functions support filtering by query parameters.

Properties
^^^^^^^^^^

You can query resources by the value of their properties.

.. code-block:: python

    project = jms_api.get_project_by_name(name="Mapdl Motorbike Frame") 
    project_api = ProjectApi(client, project.id)

    # Get all jobs
    jobs = project_api.get_jobs()

    # Get all evaluated jobs
    jobs = project_api.get_jobs(eval_status="evaluated")


In general, query parameters support the following operators: ``lt`` (less than), ``le`` (less or equal), 
``=`` (equal), ``ne`` (not equal), ``ge`` (greater or equal), ``gt`` (greater than),  ``in`` (value found in list) and
``contains`` (property contains the given string). 

.. code-block:: python
    
    # Equal
    jobs = project_api.get_jobs(eval_status="evaluated")

    # In
    jobs = project_api.get_jobs(eval_status=["prolog", "running"])

    # Contains
    query_params = {"note.contains": "search_string"}
    jobs = project_api.get_jobs(**query_params)

    # Less than
    query_params = {"fitness.lt": 1.8}
    jobs = project_api.get_jobs(**query_params)


Fields
^^^^^^

When you query a resource, the REST API returns a set of fields by default. You can specify which fields
you want returned by using the ``fields`` query parameter (this returns only the fields you specify, 
and the ID of the resource, which is always returned).
Moreover, you can request all fields to be returned by specifying ``fields="all"``.

.. code-block:: python
    
    # Get all jobs with all fields
    jobs = project_api.get_jobs(fields="all")

    # Get id and parameter values for all evaluated jobs
    jobs = project_api.get_jobs(fields=["id", "values"], eval_status="evaluated")

Sorting
^^^^^^^

You can sort resource collections by their properties.
Prefixing with ``-`` (minus) denotes descending order.

.. code-block:: python
    
    # Get all jobs sorted by fitness value in ascending order
    jobs = project_api.get_jobs(sort="fitness")

    # Get all jobs sorted by fitness value in descending order
    jobs = project_api.get_jobs(sort="-fitness")

    # Get all jobs sorted by the parameters tube1 and weight
    jobs = project_api.get_jobs(sort=["values.tube1", "values.weight"])
    print([(job.values["tube1"], job.values["weight"]) for job in jobs])

Pagination
^^^^^^^^^^

You can use the ``offset`` and ``limit`` query parameters to paginate items in a collection.

.. code-block:: python
    
    # Get name and elapsed time of max 5 evaluated jobs, sorted by creation time
    jobs = project_api.get_jobs(fields=["name", "elapsed_time"], sort="-creation_time",
                eval_status="evaluated", limit=5)

    # Query the next 10 jobs
    jobs = project_api.get_jobs(fields=["name", "elapsed_time"], sort="-creation_time",
                eval_status="evaluated", limit=10, offset=5)


Objects vs dictionaries
-----------------------------------

Most ``get``, ``create`` and ``update`` functions can optionally return dictionaries rather than class objects by setting ``as_objects=True``.
This is especially useful when the returned data needs to be further manipulated by popular packages 
such as ``Numpy``, ``Pandas``, etc.  

.. code-block:: python
    
    import pandas

    project = jms_api.get_project_by_name(name="Mapdl Motorbike Frame") 

    # Get parameter values for all evaluated jobs
    jobs = project_api.get_jobs(fields=["id", "values"], eval_status="evaluated", as_objects=False)

    # Import jobs data into a flat DataFrame
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
-----------------------------------

Query a specific project and set its failed jobs (if any) to pending.

.. code-block:: python
    
    project = jms_api.get_project_by_name(name="Mapdl Motorbike Frame") 
    jobs = project_api.get_jobs() 

    failed_jobs = [job for job in jobs if job.eval_status == "failed"]
    
    for job in failed_jobs:
        job.eval_status = "pending"
    failed_jobs = project_api.update_jobs(failed_jobs)
  

Modify a job definition  
-----------------------------------

Query an existing job definition, modify it and send it back to the server.

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
-----------------------------------

Query and then delete all jobs that timed out.

.. code-block:: python

    project = jms_api.get_project_by_name(name="Mapdl Motorbike Frame") 

    jobs = project_api.get_jobs(fields=['id'], eval_status="timeout") 
    project_api.delete_jobs(jobs)


Query the number of evaluators
------------------------------

.. code-block:: python
    
    evaluators = jms_api.get_evaluators()

    # print number of Windows and Linux evaluators connected to the REP server
    print( len([e for e in evaluators if e.platform == "windows" ]) )
    print( len([e for e in evaluators if e.platform == "linux" ]) )


Replace a file in a project
------------------------------------------

Get file definitions from an existing project Job Definition and replace the first one.

.. code-block:: python

  job_def = project_api.get_job_definitions(active=True)[0]
  files = project_api.get_files()
  file = files[0]
  file.src = r"D:\local_folder\my_project\input_file.xyz"
  project.update_files([file])

Modify and create users
------------------------------------------

Users with admin rights (such as the default ``repadmin`` user) can create new users as well as modify or delete existing ones. 

.. code-block:: python

    from ansys.rep.client import Client
    from ansys.rep.client.auth import AuthApi, User
    
    client = Client(rep_url="https://localhost:8443/rep/", username="repadmin", password="repadmin")
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

Exception handling
------------------------------------------

All exceptions that the Ansys REP client explicitly raise inherit from :exc:`ansys.rep.client.REPError`.
Client Errors are raised for 4xx HTTP status codes, while API Errors are raised for 5xx HTTP status codes (server side errors).

For example, instantiating a client with invalid credentials will return a 401 Client Error.

.. code-block:: python

    from ansys.rep.client import Client, REPError

    try:
        client = Client(rep_url="https://localhost:8443/rep/", username="repuser",  password="wrong_psw")
    except REPError as e:
        print(e)

    #Output:
    # 401 Client Error: invalid_grant for: POST https://localhost:8443/rep/auth/realms/rep/protocol/openid-connect/token
    # Invalid user credentials

A *get* call on a non-existing resource will return a 404 Client Error.

.. code-block:: python

    from ansys.rep.client.jms import JmsApi

    jms_api = JmsApi(client)
    try:
        jms_api.get_project(id="non_existing_project")
    except REPError as e:
        print(e)

    #Output:
    #404 Client Error: Not Found for: GET https://localhost:8443/rep//jms/api/v1/projects/non_existing_project