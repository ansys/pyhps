Migrate DCS Python Client scripts
===================================

Few words about HPS being the successor of DCS, similarly pyHPS is the successor of the DCS Python Client.

DCS Python client doc: https://storage.ansys.com/dcs_python_client/v241/index.html


Key Terminology and API Changes
-------------------------------


The Design Points Service (DPS) from DCS has evolved into the Job Management Service (JMS) as part of HPS.
Some key entities that were part of the DPS API have been renamed in JMS:

* Design Point -> Job
* Configuration -> Job Definition
* Process Step -> Task Definition
* Parameter Location -> Parameter Mapping

Other key changes that impact the Python client and existing scripts: 

* All resource IDs are string now (as opposed to integers)
* In DCS, the client specifies the ID of the project when creating it. 
  In HPS, the client only specifies the name of the project. The ID is assigned server-side.
* Some nested endpoints have been removed, for instance:
  
  .. code::

     GET /dps/api/projects/{project_id}/configurations/{configuration_id}/design_points
     GET /dps/api/projects/{project_id}/design_points/{design_point_id}/tasks

  do not have a counterpart in the JMS API.
* In the DPS API, the Configuration resource (now Job Definition) used to include Process Steps, Parameter Definitions and Parameter Locations.
  These are now separate resources (with corresponding endpoints) in the JMS API, namely Task Definitions, Parameter Definitions and Parameter Mappings.
* Within a Task Definition (previously Process Step), you can now also specify:
  
    - Multiple software requirements
    - Environment variables
    - An execution context
    - Custom resource requirements
    - HPC resource requirements

  The field ``cpu_core_usage`` has been renamed to ``num_cores``.
  ``memory`` and ``disk_space`` are now expressed in bytes (MB before).


Python Client Changes
---------------------

Installation
~~~~~~~~~~~~

The DCS Python client used to be distributed as a wheel part of the Ansys installation.
PyHPS can instead be installed following [ref to how to install]. 


Client and API objects
~~~~~~~~~~~~~~~~~~~~~~

Besides obvious changes to reflect the API changes, we have also done some work to streamline the structure of the package. 
The main ``Client`` object now only stores the connection, without exposing any service API.
Similarly, resources like Projects and Jobs do not expose anymore API endpoints. 
Instead objects like the ``JmsApi``, the ``ProjectApi`` and the ``RmsApi`` wrap around HPS REST APIs.

For instance, this is how you instantiate a Client object and retrieve projects:

.. .. list-table::
..    :widths: 1 1
..    :header-rows: 1

..    *  -  DCS Client
..       -  PyHPS

..    *  -  .. code-block:: python
  
..             from ansys.dcs.client.dps import Client

..             client = Client(
..                 dcs_url="https://localhost/dcs",
..                 username="dcadmin",
..                 password="dcadmin"
..             )
..             projects = client.get_projects()

..       -  .. code-block:: python

..             from ansys.rep.client import Client, JmsApi

..             client = Client(
..                 url="https://localhost:8443/hps",
..                 username="repadmin",
..                 password="repadmin"
..             )
..             jms_api = JmsApi(client)
..             projects = jms_api.get_projects()

.. tabs::

   .. code-tab:: python DCS Client
  
        from ansys.dcs.client.dps import Client

        client = Client(
            dcs_url="https://localhost/dcs",
            username="dcadmin",
            password="dcadmin"
        )
        projects = client.get_projects()

   .. code-tab:: python PyHPS

        from ansys.rep.client import Client, JmsApi

        client = Client(
            url="https://localhost:8443/hps",
            username="repadmin",
            password="repadmin"
        )
        jms_api = JmsApi(client)
        projects = jms_api.get_projects()

Project ID
~~~~~~~~~~

As mentioned above, in HPS the client only specifies the name of the project.
The project ID is assigned server-side. This is how you create a project in the two cases:

.. tabs::

   .. code-tab:: python DCS Client
  
        from ansys.dcs.client.dps import Client, Project

        client = Client(...)

        proj = Project(
            id="my_new_project",
            display_name="My New Project"
        )
        proj = client.create_project(proj)

   .. code-tab:: python PyHPS

        from ansys.hps.client import Client
        from ansys.hps.client.jms import JmsApi, Project

        client = Client(...)

        jms_api = JmsApi(client)
        proj = Project(name="My New Project")
        proj = jms_api.create_project(proj)

Removed Nested Endpoints
~~~~~~~~~~~~~~~~~~~~~~~~

Following the changes in the API, nested endpoints are removed.

Exceptions
~~~~~~~~~~

Exceptions handling works the same. The ``DCSError`` has been renamed to ``HPSError``. 

.. tabs::

   .. code-tab:: python DCS Client
  
        from ansys.dcs.client import DCSError
        from ansys.dcs.client.dps import Client

        try:
            client = Client(
                dcs_url="https://localhost/dcs/",
                username="dcadmin", 
                password="wrong_psw"
            )
        except DCSError as e:
            print(e)

   .. code-tab:: python PyHPS

        from ansys.hps.client import Client, HPSError

        try:
            client = Client(
                url="https://localhost:8443/hps",
                username="repuser",
                password="wrong_psw"
            )
        except HPSError as e:
            print(e)

Evaluators
~~~~~~~~~~

The evaluators resources and corresponding endpoints have been moved to the new Resource Management Service (RMS).
This is reflected in PyHPS accordingly.

.. tabs::

   .. code-tab:: python DCS Client
  
    from ansys.dcs.client.dps import Client

    client = Client(...)

    evaluators = client.get_evaluators()

   .. code-tab:: python PyHPS

        from ansys.hps.client import Client, RmsApi

        client = Client(...)

        rms_api = RmsApi(client)
        evaluators = rms_api.get_evaluators()


Example Project
---------------

Import modules and instantiate the client.

.. tabs::

   .. code-tab:: python DCS Client
  
        import os

        from ansys.dcs.client.dps import Client
        from ansys.dcs.client.dps.resource import (
            Configuration,
            DesignPoint,
            File,
            FitnessDefinition,
            Project,
            SuccessCriteria
        )

        client = Client(
            dcs_url="https://127.0.0.1/dcs",
            username="dcadmin",
            password="dcadmin"
        )

   .. code-tab:: python PyHPS

        import os

        from ansys.hps.client import Client, JmsApi
        from ansys.hps.client.jms import (
            File,
            FitnessDefinition,
            FloatParameterDefinition,
            Job,
            JobDefinition,
            ParameterMapping,
            Project,
            ProjectApi,
            ResourceRequirements,
            Software,
            StringParameterDefinition,
            SuccessCriteria,
            TaskDefinition,
        )
        
        client = Client(
            url="https://localhost:8443/hps",
            username="repuser",
            password="repuser"
        )


Create an empty project and a job definition

.. tabs::

   .. code-tab:: python DCS Client
  
        proj = Project(
            id="mapdl_motorbike_frame",
            display_name="MAPDL Motorbike Frame",
            priority=1,
            active=True
        )
        proj = client.create_project(proj, replace=True)

        cfg = Configuration(name="Configuration.1", active=True)

   .. code-tab:: python PyHPS

        jms_api = JmsApi(client)
        proj = Project(name="MAPDL Motorbike Frame", priority=1, active=True)
        proj = jms_api.create_project(proj)

        project_api = ProjectApi(client, proj.id)

        job_def = JobDefinition(name="JobDefinition.1", active=True)

File resources

.. tabs::

   .. code-tab:: python DCS Client
  
        cwd = os.path.dirname(__file__)
        files = []

        # Input File
        files.append(
            File(
                name="mac", 
                evaluation_path="motorbike_frame.mac",
                type="text/plain",
                src=os.path.join(cwd, "motorbike_frame.mac") 
            )
        )

        # Output Files
        files.append( File( name="results", evaluation_path="motorbike_frame_results.txt", type="text/plain" ) )
        files.append( File( name="img", evaluation_path="file000.jpg", type="image/jpeg", collect=True) )
        files.append( File( name="img2", evaluation_path="file001.jpg", type="image/jpeg", collect=True) )
        files.append( File( name="out", evaluation_path="file.out", type="text/plain", collect=True) )

        # create file resources on the server
        files = proj.create_files(files)

        # For convenience, we keep a reference to the input and result files.
        mac_file = files[0]
        result_file = files[1]

   .. code-tab:: python PyHPS

        cwd = os.path.dirname(__file__)
        files = []

        # Input File
        files.append(
            File(
                name="mac",
                evaluation_path="motorbike_frame.mac",
                type="text/plain",
                src=os.path.join(cwd, "motorbike_frame.mac"),
            )
        )

        # Output Files
        files.append(
            File(
                name="results",
                evaluation_path="motorbike_frame_results.txt",
                type="text/plain",
                src=os.path.join(cwd, "motorbike_frame_results.txt"),
            )
        )
        files.append(File(name="img", evaluation_path="file000.jpg", type="image/jpeg", collect=True))
        files.append(File(name="img2", evaluation_path="file001.jpg", type="image/jpeg", collect=True))
        files.append(
            File(name="out", evaluation_path="file.out", type="text/plain", collect=True, monitor=True)
        )

        # create file resources on the server
        files = project_api.create_files(files)

        # For convenience, we keep a reference to the input and result files.
        mac_file = files[0]
        result_file = files[1]


Parameters definition

.. tabs::

   .. code-tab:: python DCS Client
  
        # Input params: Dimensions of three custom tubes
        float_input_params=[]
        for i in range(1,4):
            pd = cfg.add_float_parameter_definition(
                name='tube%i_radius' %i,
                lower_limit=4.0,
                upper_limit=20.0,default=12.0
            )
            cfg.add_parameter_location(
                key_string='radius(%i)' % i,
                tokenizer="=",
                parameter_definition_name=pd.name,
                file_id=mac_file.id
            )
            float_input_params.append(pd)
            pd = cfg.add_float_parameter_definition(
                name='tube%i_thickness' %i,
                lower_limit=0.5,
                upper_limit=2.5,
                default=1.0 )
            cfg.add_parameter_location(
                key_string='thickness(%i)' % i,
                tokenizer="=",
                parameter_definition_name=pd.name,
                file_id=mac_file.id
            )
            float_input_params.append(pd)

        # Input params: Custom types used for all the different tubes of the frame
        str_input_params=[]
        for i in range(1,22):
            pd = cfg.add_string_parameter_definition(
                name="tube%s" %i,
                default="1",
                value_list=["1","2","3"]
            )
            cfg.add_parameter_location(
                key_string='tubes(%i)' % i,
                tokenizer="=",
                parameter_definition_name=pd.name,
                file_id=mac_file.id
            )
            str_input_params.append(pd)

        # Output Parames
        for pname in ["weight", "torsion_stiffness", "max_stress"]:
            pd = cfg.add_float_parameter_definition(name=pname)
            cfg.add_parameter_location(
                key_string=pname,
                tokenizer="=",
                parameter_definition_name=pd.name,
                file_id=result_file.id
            )

   .. code-tab:: python PyHPS

        # Input params: Dimensions of three custom tubes
        float_input_params = []
        for i in range(1, 4):
            float_input_params.extend(
                [
                    FloatParameterDefinition(
                        name="tube%i_radius" % i, lower_limit=4.0, upper_limit=20.0, default=12.0
                    ),
                    FloatParameterDefinition(
                        name="tube%i_thickness" % i, lower_limit=0.5, upper_limit=2.5, default=1.0
                    ),
                ]
            )

        float_input_params = project_api.create_parameter_definitions(float_input_params)
        param_mappings = []
        pi = 0
        for i in range(1, 4):
            param_mappings.append(
                ParameterMapping(
                    key_string="radius(%i)" % i,
                    tokenizer="=",
                    parameter_definition_id=float_input_params[pi].id,
                    file_id=mac_file.id,
                )
            )
            pi += 1
            param_mappings.append(
                ParameterMapping(
                    key_string="thickness(%i)" % i,
                    tokenizer="=",
                    parameter_definition_id=float_input_params[pi].id,
                    file_id=mac_file.id,
                )
            )
            pi += 1

        # Input params: Custom types used for all the different tubes of the frame
        str_input_params = []
        for i in range(1, 22):
            str_input_params.append(
                StringParameterDefinition(name="tube%s" % i, default="1", value_list=["1", "2", "3"])
            )
        str_input_params = project_api.create_parameter_definitions(str_input_params)

        for i in range(1, 22):
            param_mappings.append(
                ParameterMapping(
                    key_string="tubes(%i)" % i,
                    tokenizer="=",
                    parameter_definition_id=str_input_params[i - 1].id,
                    file_id=mac_file.id,
                )
            )

        # Output Params
        output_params = []
        for pname in ["weight", "torsion_stiffness", "max_stress"]:
            output_params.append(FloatParameterDefinition(name=pname))
        output_params = project_api.create_parameter_definitions(output_params)
        for pd in output_params:
            param_mappings.append(
                ParameterMapping(
                    key_string=pd.name,
                    tokenizer="=",
                    parameter_definition_id=pd.id,
                    file_id=result_file.id,
                )
            )

Process Step

.. tabs::

   .. code-tab:: python DCS Client
  
        cfg.add_process_step(
            name="MAPDL_run",
            application_name="ANSYS Mechanical APDL",
            application_version="2024 R1",
            execution_command="%executable% -b -i %file:mac% -o file.out",
            max_execution_time=20.0,
            cpu_core_usage=1,
            execution_level=0,
            memory=250,
            disk_space=5,
            input_file_ids=[f.id for f in files[:1]],
            output_file_ids=[f.id for f in files[1:]],
            success_criteria= SuccessCriteria(
                return_code=0,
                expressions= ["values['tube1_radius']>=4.0", "values['tube1_thickness']>=0.5"],
                required_output_file_ids=[ f.id for f in files[2:] ],
                require_all_output_files=False,
                required_output_parameter_names=["weight", "torsion_stiffness", "max_stress"],
                require_all_output_parameters=False
            )
        )
   .. code-tab:: python PyHPS

        task_def = TaskDefinition(
            name="MAPDL_run",
            software_requirements=[
                Software(name="Ansys Mechanical APDL", version="2024 R1"),
            ],
            execution_command="%executable% -b -i %file:mac% -o file.out -np %resource:num_cores%",
            max_execution_time=20.0,
            resource_requirements=ResourceRequirements(
                num_cores=1.0,
                memory=250 * 1024 * 1024,  # 250 MB
                disk_space=5 * 1024 * 1024,  # 5 MB
            ),
            execution_level=0,
            num_trials=1,
            input_file_ids=[f.id for f in files[:1]],
            output_file_ids=[f.id for f in files[1:]],
            success_criteria=SuccessCriteria(
                return_code=0,
                expressions=["values['tube1_radius']>=4.0", "values['tube1_thickness']>=0.5"],
                required_output_file_ids=[ f.id for f in files[2:] ],
                require_all_output_files=False,
                required_output_parameter_names=["weight", "torsion_stiffness", "max_stress"],
                require_all_output_parameters=True,
            ),
        )


Fitness definition

.. tabs::

   .. code-tab:: python DCS Client

        fd = FitnessDefinition(error_fitness=10.0)
        fd.add_fitness_term(name="weight", type="design_objective", weighting_factor=1.0,
                            expression="map_design_objective( values['weight'], 7.5, 5.5)")
        fd.add_fitness_term(name="torsional_stiffness", type="target_constraint", weighting_factor=1.0,
                        expression="map_target_constraint( values['torsion_stiffness'], 1313.0, 5.0, 30.0 )" )
        fd.add_fitness_term(name="max_stress", type="limit_constraint", weighting_factor=1.0,
                        expression="map_limit_constraint( values['max_stress'], 451.0, 50.0 )")
        cfg.fitness_definition =fd

   .. code-tab:: python PyHPS

        fd = FitnessDefinition(error_fitness=10.0)
        fd.add_fitness_term(
            name="weight",
            type="design_objective",
            weighting_factor=1.0,
            expression="map_design_objective( values['weight'], 7.5, 5.5)",
        )
        fd.add_fitness_term(
            name="torsional_stiffness",
            type="target_constraint",
            weighting_factor=1.0,
            expression="map_target_constraint( values['torsion_stiffness'], 1313.0, 5.0, 30.0 )",
        )
        fd.add_fitness_term(
            name="max_stress",
            type="limit_constraint",
            weighting_factor=1.0,
            expression="map_limit_constraint( values['max_stress'], 451.0, 50.0 )",
        )
        job_def.fitness_definition = fd

Create the job definition

.. tabs::

   .. code-tab:: python DCS Client

        cfg = proj.create_configurations([cfg])[0]

   .. code-tab:: python PyHPS

        task_defs = [task_def]

        task_defs = project_api.create_task_definitions(task_defs)
        param_mappings = project_api.create_parameter_mappings(param_mappings)

        job_def.parameter_definition_ids = [
            pd.id for pd in float_input_params + str_input_params + output_params
        ]
        job_def.parameter_mapping_ids = [pm.id for pm in param_mappings]
        job_def.task_definition_ids = [td.id for td in task_defs]

        job_def = project_api.create_job_definitions([job_def])[0]

Design Points

.. tabs::

   .. code-tab:: python DCS Client

        import random

        dps = []
        for i in range(10):
            values = {
                p.name: p.lower_limit + random.random() * (p.upper_limit - p.lower_limit)
                for p in float_input_params
            }
            values.update({ p.name: random.choice(p.value_list) for p in str_input_params})
            dps.append( DesignPoint( name=f"DesignPoint.{i}", values=values, eval_status="pending") )

        dps = cfg.create_design_points(dps)

   .. code-tab:: python PyHPS

        import random

        jobs = []
        for i in range(10):
            values = {
                p.name: p.lower_limit + random.random() * (p.upper_limit - p.lower_limit)
                for p in float_input_params
            }
            values.update({p.name: random.choice(p.value_list) for p in str_input_params})
            jobs.append(
                Job(name=f"Job.{i}", values=values, eval_status="pending", job_definition_id=job_def.id)
            )
        jobs = project_api.create_jobs(jobs)