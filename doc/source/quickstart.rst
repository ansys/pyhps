.. _quickstart:

Quickstart
===============

This guide will walk you through the basics of interacting with a REP server. More elaborated examples are available in the :ref:`Examples <examples>` chapter, 
while detailed documentation can be found in the :ref:`Code Documentation <api_reference>`.

To reproduce the code samples provided below, you will need:

- A running REP server, see TODO :strike:`the DPS Startup page in the ANSYS Help for detailed instructions`.
- A Python shell with ``ansys-rep-client`` installed. If you haven't installed it yet, please refer to the :ref:`Installation <installation>` guide.


Connect to a REP Server 
--------------------------

Let's start by connecting to a REP server running on the localhost with default username and password.

.. code-block:: python

    from ansys.rep.client import Client
    from ansys.rep.client.jms import JmsApi
    
    client = Client(rep_url="https://localhost:8443/rep", username="repadmin", password="repadmin")  

    # check which JMS version the server is running    
    jms_api = JmsApi(client)
    print(jms_api.get_api_info()['build']['external_version'])

    # get all projects
    projects = jms_api.get_projects()

Query projects statistics to find out how many design points are currently running

.. code-block:: python

    projects = jms_api.get_projects(statistics=True)
    num_running_jobs = sum(p.statistics["eval_status"]["running"] for p in projects)

Create a demo project: the MAPDL motorbike frame example
---------------------------------------------------------

Create a project consisting of an Ansys APDL beam model 
of a tubular steel trellis motorbike-frame. 

.. only:: builder_html

     The project setup script as well as the data files can be downloaded here :download:`MAPDL Motorbike Frame Project <../../mapdl_motorbike_frame.zip>`.
     To create the project you only need to run the `project_setup` script:

::

    $ python path_to_download_folder\mapdl_motorbike_frame\project_setup.py

.. note::
    By default, the script tries to connect to the REP server running on the localhost with default username and password.
    If your REP server is hosted at a different URL or you want to specify different credentials,
    please adjust the script before running it. 


See :ref:`example_mapdl_motorbike_frame` for a detailed description of this example.

Query parameters
-----------------------------------

Most ``get`` functions support filtering by query parameters.

.. code-block:: python
    
    project = jms_api.get_project(id="mapdl_motorbike_frame") 

    # Get all design points with all fields
    jobs = project.get_jobs()

    # Get id and parameter values for all evaluated design points
    jobs = project.get_jobs(fields=["id", "values"], eval_status="evaluated")

    # Get name and elapsed time of max 5 evaluated design points
    jobs = project.get_jobs(fields=["name", "elapsed_time"], 
                        eval_status="evaluated", limit=5)

    # Get all design points sorted by fitness value in ascending order
    jobs = project.get_jobs(sort="fitness")

    # Get all design points sorted by fitness value in descending order
    jobs = project.get_jobs(sort="-fitness")

    # Get all design points sorted by the parameters tube1 and weight
    jobs = project.get_jobs(sort=["values.tube1", "values.weight"])
    print([(dp.values["tube1"], dp.values["weight"]) for dp in jobs])

In general, query parameters support the following operators: ``lt`` (less than), ``le`` (less or equal), 
``=`` (equal), ``ne`` (not equal), ``ge`` (greater or equal), ``gt`` (greater than),  ``in`` (value found in list) and
``contains`` (property contains the given string). 

.. code-block:: python
    
    # Equal
    jobs = project.get_jobs(eval_status="evaluated")

    # In
    jobs = project.get_jobs(eval_status=["prolog", "running"])

    # Contains
    query_params = {"note.contains": "search_string"}
    jobs = project.get_jobs(**query_params)

    # Less than
    query_params = {"fitness.lt": 1.8}
    jobs = project.get_jobs(**query_params)

Objects vs dictionaries
-----------------------------------

Most ``get``, ``create`` and ``update`` functions can optionally return dictionaries rather than class objects by setting ``as_objects=True``.
This is especially useful when the returned data needs to be further manipulated by popular packages 
such as ``Numpy``, ``Pandas``, etc.  

.. code-block:: python
    
    import pandas

    project = client.get_project(id="mapdl_motorbike_frame") 

    # Get parameter values for all evaluated design points
    jobs = project.get_jobs(fields=["id", "values"], eval_status="evaluated", as_objects=False)

    # Import jobs data into a flat DataFrame
    df = pandas.io.json.json_normalize(jobs)

    # Output
    #    id  values.tube1_radius  values.tube1_thickness  values.tube2_radius  values.tube2_thickness  values.tube3_radius  values.tube3_thickness  ... values.tube15 values.tube16 values.tube17 values.tube18 values.tube19 values.tube20 values.tube21
    # 0      1             7.055903                0.728247            17.677894                0.512761            13.342691                0.718970  ...             1             3             2             3             1             1             1
    # 1      2            18.172368                2.407453             9.216933                0.818597            11.789593                1.439845  ...             3             1             3             2             3             3             2
    # 2      3            14.832407                2.380437             7.484620                1.601617            19.742424                0.816099  ...             2             1             1             1             2             2             3
    # 3      4            10.254875                2.420485            10.429973                2.241802            14.647943                0.501836  ...             1             3             2             1             3             3             3
    # 4      5            14.601405                1.657524            10.056457                1.743385             8.821876                2.200616  ...             1             2             3             3             2             1             2
    # 5      6            10.393178                2.155777             8.043999                2.036772            11.605410                2.426192  ...             3             1             1             1             2             1             1
    # 6      7            10.415530                1.675479             4.570576                1.461735            16.915658                1.822555  ...             3             3             3             2             1             1             2
    # 7      8            12.841433                1.322097             6.142197                1.659299             6.275559                2.312346  ...             3             2             2             3             1             1             3
    # 8      9            18.394536                2.446091            12.882719                0.939273            15.167834                1.683604  ...             3             1             2             3             2             2             1
    # 9     10            12.414343                1.699816             6.128372                1.314386            18.783781                1.736996  ...             1             3             2             1             3             1             2


Set failed design points to pending 
-----------------------------------

Query a specific project and set its failed design points (if any) to pending.

.. code-block:: python
    
    project = client.get_project(id="mapdl_motorbike_frame") 
    jobs = project.get_jobs() 

    failed_dps = [dp for dp in jobs if dp.eval_status == "failed"]
    
    for dp in failed_dps:
        dp.eval_status = "pending"
    failed_dps = project.update_jobs(failed_dps)
  

Modify a project job_definition  
-----------------------------------

Query an existing project job_definition, modify it and send it back to the server.

.. code-block:: python

    project = client.get_project(id="mapdl_motorbike_frame") 

    # get currently active job_definition
    job_def = project.get_job_definitions(active=True)[0]
    
    # Update the lower limit of a parameter
    parameter = job_def.parameter_definitions[0]
    parameter.lower_limit = 2.5

    # send the updated job_definition to the server
    job_def = project.update_job_definitions([job_def])[0]


Delete some design points  
-----------------------------------

Query and then delete all design points that timed out.

.. code-block:: python

    project = client.get_project(id="mapdl_motorbike_frame") 

    jobs = project.get_jobs(fields=['id'], eval_status="timeout") 
    project.delete_jobs(jobs)


Query the number of evaluators
------------------------------

.. code-block:: python
    
    evaluators = client.get_evaluators()

    # print number of Windows and Linux evaluators connected to the DCS server
    print( len([e for e in evaluators if e.platform == "Windows" ]) )
    print( len([e for e in evaluators if e.platform == "Linux" ]) )


Replace a file in a project
------------------------------------------

Get file definitions from an existing project job_definition and replace the first one.

.. code-block:: python

  job_def = project.get_job_definitions(active=True)[0]
  files = project.get_files()
  file = files[0]
  file.src = r"D:\local_folder\my_project\workbench_archive.wbpz"
  files = project.update_files([file])

For instructions on how to add a new file to an existing project job_definition, see :ref:`Adding a file to a project <example_adding_files>`.

Modify and create users
------------------------------------------

Users with admin rights (such as the default ``repadmin`` user) can create new users as well as modify or delete existing ones. 

.. code-block:: python

    from ansys.rep.client import Client
    from ansys.rep.client.auth import AuthApi, User
    
    client = Client(rep_url="https://127.0.0.1/dcs/", username="repadmin", password="repadmin")
    auth_api = AuthApi(client)

    # modify the default password of the repadmin user
    default_user = auth_api.get_users()[0]
    default_user.password = 'new_password'
    auth_api.update_user(default_user)

    # create a new non-admin user
    new_user = User(username='test_user', password='dummy', 
                    email='test_user@test.com', fullname='Test User', 
                    is_admin=False)
    new_user = auth_api.create_user(new_user)


Exception handling
------------------------------------------

All exceptions that the Ansys DCS clients explicitly raise inherit from :exc:`ansys.rep.client.REPError`.
Client Errors are raised for 4xx HTTP status codes, while API Errors are raised for 5xx HTTP status codes (server side errors).

For example, instantiating a client with invalid credentials will return a 400 Client Error.

.. code-block:: python

    from ansys.rep.client import REPError
    from ansys.rep.client.jms import Client

    try:
        client = Client(rep_url="https://127.0.0.1/dcs/", username="repadmin",  password="wrong_psw")
    except REPError as e:
        print(e)

    #Output:
    #400 Client Error: invalid_grant for: POST https://127.0.0.1/dcs/auth/api/oauth/token
    #Invalid "username" or "password" in request.

A *get* call  on a non-existing resource will return a 404 Client Error.

.. code-block:: python

    try:
        client.get_project(id="non_existing_project")
    except REPError as e:
        print(e)

    #Output:
    #404 Client Error: Not Found for: GET https://127.0.0.1/dcs/dps/api//projects/non_existing_project