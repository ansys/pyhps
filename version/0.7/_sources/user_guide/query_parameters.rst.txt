
Query parameters
----------------

Most ``get`` functions support filtering by query parameters.

Query by property values
^^^^^^^^^^^^^^^^^^^^^^^^

You can query resources by the value of their properties:

.. code-block:: python

    project = jms_api.get_project_by_name(name="Mapdl Motorbike Frame") 
    project_api = ProjectApi(client, project.id)

    # Get all jobs
    jobs = project_api.get_jobs()

    # Get all evaluated jobs
    jobs = project_api.get_jobs(eval_status="evaluated")


In general, query parameters support these operators:

- ``lt``: Less than
- ``le``: Less than or equal to 
- ``=``: Equal to
- ``ne``: Not equal to
- ``ge``: Greater than or equal to
- ``gt``: Greater than
- ``in``: Value found in list
- ``contains``: Property contains the given string 

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


Query by fields
^^^^^^^^^^^^^^^

When you query a resource, the REST API returns a set of fields by default. You can specify which fields
you want returned by using the ``fields`` query parameter. (The query returns all specified fields in
addition to the ID of the resource, which is always returned.) To request that all fields be returned,
use ``fields="all"``.

.. code-block:: python
    
    # Get ID and parameter values for all evaluated jobs
    jobs = project_api.get_jobs(fields=["id", "values"], eval_status="evaluated")

    # Get all jobs with all fields
    jobs = project_api.get_jobs(fields="all")

Sorting by property values
^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can sort resource collections by the values of their properties.
Prefixing with ``-`` (minus) denotes descending order.

.. code-block:: python
    
    # Get all jobs sorted by fitness value in ascending order
    jobs = project_api.get_jobs(sort="fitness")

    # Get all jobs sorted by fitness value in descending order
    jobs = project_api.get_jobs(sort="-fitness")

    # Get all jobs sorted by 'tube1' and 'weight' parameters
    jobs = project_api.get_jobs(sort=["values.tube1", "values.weight"])
    print([(job.values["tube1"], job.values["weight"]) for job in jobs])

Paginating items in a collection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can use the ``offset`` and ``limit`` query parameters to paginate items in a collection.

.. code-block:: python
    
    # Get the name and elapsed time of a maximum of 5 evaluated jobs, sorted by creation time
    jobs = project_api.get_jobs(fields=["name", "elapsed_time"], sort="-creation_time",
                eval_status="evaluated", limit=5)

    # Query the next 10 jobs
    jobs = project_api.get_jobs(fields=["name", "elapsed_time"], sort="-creation_time",
                eval_status="evaluated", limit=10, offset=5)

