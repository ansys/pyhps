.. _example_download_files:

Download of output files
==================================

This example shows how to download the output files of design points. 
We assume you have already completed the :ref:`example_mapdl_motorbike_frame` tutorial and have the MAPDL Motorbike Frame project at hand.

To begin with, we connect to a DCS server running on the localhost with default username and password
and specify the local path where the files are going to be saved. 

.. warning::
    Before executing the code, make sure to adjust the ``download_path`` variable.

.. code-block:: python

    import os
    from ansys.rep.client.jms import Client

    # Connect to the DCS server and query the project
    client = Client(rep_url="https://127.0.0.1/dcs", username="repadmin", password="repadmin")
    proj = client.get_project(id="mapdl_motorbike_frame") 

    # Specify the base path where to download files
    download_path = #e.g. 'C:\\Users\\your_username\\Documents\\mapdl_motorbike_frame\\download' 
    if not os.path.exists(download_path): 
        os.makedirs(download_path) 


Log files
------------------------------

We first show how to download the log files. To this end, let's first get all evaluated and failed design points.  
Note that we specify the ``fields`` query parameter to restrict the returned fields to the ones we actually need for this example.

.. code-block:: python

    dps = proj.get_jobs(fields=["id", "files", "eval_status"], eval_status=["evaluated", "failed"]) 

Also note that each design point holds a list of file IDs linked to it.

.. code-block:: python

    print(dps[0].file_ids)
    #Output (numbers could be different)
    #[6, 7, 8, 36, 1]

For each design point, we now download the content of its ``file.out`` log file (which contains the APDL output) and save it to disk.

.. code-block:: python

    for dp in dps: 

        print(f"Downloading log file of design point {dp.id} ...") 
        f = proj.get_files(id=dp.file_ids, evaluation_path="file.out", content=True)[0] 

        # If some content is found (it's not the case if the design point fails 
        # even before starting the simulation) we save it to disk.
        if f.content: 
            path = os.path.join(download_path, f"{f.name}_dp{dp.id}.txt") 
            print(f"Saving {f.name} to {path}") 
            with open(path, "w") as tf: 
                tf.write(f.content.decode('utf-8')) 

.. note::
    With the ``id`` and ``evaluation path`` query parameters in the ``get_files`` function we specify that we are only 
    interested in the ``file.out`` produced by the current design point.
    Moreover, by setting ``content=True`` we effectively download the file content and
    not only its metadata.

Images
-------------------------------------

Similarly, we can download the images associated to the design points. In this example, for each design point 
we download and save all JPEG images.

.. code-block:: python

    for dp in dps: 

        print(f"Downloading image files of design point {dp.id} ... ") 
        files = proj.get_files(id=dp.file_ids, type="image/jpeg", content=True)

        for f in files:
            if f.content: 
                path = os.path.join(download_path, f"{f.name}_dp{dp.id}.jpg") 
                print(f"Saving {f.name} to {path}") 
                with open(path, "wb") as bf: 
                    bf.write(f.content) 


Parsing of log files
----------------------------------

The possibility to download and parse log files can be particularly useful when design point failures need to be investigated.
Consider for instance the case where design points are submitted to DPS from a Workbench project. 
Suppose that unexpected failures are observed for different reasons. For instance, some might be due to parameter values resulting in invalid job_definitions, 
others could be related to non-convergence of some intermediate steps, some others could instead be caused by hardware failure.

To systematically investigate such cases, one could for instance download the log files of failed design points and parse the content looking for specific
failure indicators.    

Downloading the log files goes along the lines of the examples above. Note however the different query parameters
used in the ``get_files`` function. 

.. code-block:: python

    import os
    from ansys.rep.client.jms import Client

    # Connect to the DCS server and query the project
    client = Client(rep_url="https://127.0.0.1/dcs", username="repadmin", password="repadmin")
    proj = client.get_project(id="project_id") 

    # Specify the base path where to download files
    download_path = #e.g. 'C:\\Users\\your_username\\Documents\\project_id\\download' 
    if not os.path.exists(download_path): 
        os.makedirs(download_path) 

    # Get all failed design points
    failed_dps = proj.get_jobs(eval_status=['failed']) 
    print("%d failed design points" % len(failed_dps)) 

    # for each design point, download its workbench log file
    for dp in failed_dps: 

        print("Downloading log file of design point %d ... " % dp.id) 

        query_params = {"id": dp.file_ids, "name.contains": "log_Workbench_Project"}
        f = proj.get_files(**query_params, content=True)[0] 

        if f.content: 
            path = os.path.join(download_path, f"{f.name}_dp{dp.id}.txt") 
            print(f"Saving {f.name} to {path}") 
            with open(path, "w") as tf: 
                tf.write(f.content.decode('utf-8')) 

The actual parsing of the log files could be done for instance by first defining a dictionary of 
failure strings to look for. 
These could have been identified by prior knowledge of possible failure reasons or by manually inspecting some of the log files. 

.. code-block:: python

    failure_dict = [
        {
            "failure_string": "Could not find file", 
            "label": "Missing file"
        },
        {
            "failure_string": "no longer available in the geometry", 
            "label": "Missing geometry"
        },
        {
            "failure_string": "Can't initialize Addin", 
            "label": "Installation"
        },
        {
            "failure_string": "One or more entities failed to mesh",
            "label": "Meshing failure"
        },
        {
            "failure_string": "license",
            "label": "No License"
        }
    ]

For each design point, we then open the corresponding log file and test whether it contains any failure strings.
The results are collected in a ``pandas`` dataframe object which can be easily queried or exported in ``csv`` or ``xlsx`` format. 

.. code-block:: python

    import pandas
    df = pandas.DataFrame(columns=["Id", "Name", "Eval Status", "Elapsed Time", "Failures"])

    for dp in failed_dps:
        log_file_path = os.path.join(download_path, "log_Workbench_Project_dp%d.txt" % dp.id)

        errors = set()

        if os.path.exists(log_file_path):
            with open(log_file_path, 'r') as lf:
                content = lf.read()

            errors = set()
            for row in failure_dict:
                if row["failure_string"] in content:
                    errors.add(row["label"])

            if not errors:
                errors.add("Unknown")
        else:
            errors.add("Missing Log File")

        df = df.append({
             "Id": dp.id,
             "Name":  dp.name,
             "Eval Status":  dp.eval_status,
             "Elapsed Time":  dp.elapsed_time,
             "Failures": '; '.join(errors)
            }, ignore_index=True)


    # Example export to Excel or CSV 
    df.to_excel(os.path.join(download_path, "failures.xlsx"), index=False) # requires the openpyxl package to be available 
    df.to_csv(os.path.join(download_path, "failures.csv"), index=False)

The dataframe will look like this

.. code-block:: python

       Id Name Eval Status  Elapsed Time          Failures
    0   6    8      failed    137.543538  Missing geometry
    1   7    9      failed     86.561933           Unknown
    2  10   12      failed    112.935375  Missing geometry; Missing file
    3  11   13      failed    138.019429           License
    4  18   20      failed    133.204345  Missing geometry
    ...

By suitably querying the dataframe, one could then easily e.g. set to pending all design points which failed because of a specific reason.

.. code-block:: python

    from ansys.rep.client.jms import Job

    # get the ID of design points which failed because of license issues
    ids = df[df["Failures"].str.contains("License")]["Id"].to_list()

    dps_of_interest = [Job(id=id, eval_status="pending") for id in ids]
    dps_of_interest = proj.update_jobs(dps_of_interest)