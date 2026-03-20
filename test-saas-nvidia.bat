cd dev_env
cd Scripts
call activate.bat
cd ..
cd ..

REM python -m pip install "ansys-rep-common @ git+https://github.com/ansys-internal/rep-common-py.git@main#egg=ansys-rep-common"

set BASE_PROD_URL=https://hps.ansys.com/hps
set BASE_URL=https://test-jms.awsansys11np.onscale.com/hps
set ACCOUNT_BURST=30b226d7-aa1b-4001-b763-f88525abde4d
set ACCOUNT_BURST_2=72670e8c-43fe-4ec3-bcf8-20be821d91c1
set ACCOUNT_TOASTER=0fea8f1b-0f0f-4998-938a-37a62db59481
set ACCOUNT_PROD=e8cfbf84-058c-43cf-9eb4-9917b1ab2e9f
set ACCOUNT_ANYWHERE=becd2b05-9e2b-4325-bc57-ab0225d6b5b5

for /f "delims=" %%a in ('python oidc_pkce.py -u %BASE_URL%') do @set TOKEN=%%a
REM for /f "delims=" %%a in ('python oidc_pkce.py -u %BASE_PROD_URL%') do @set TOKEN_PROD=%%a

echo %TOKEN%


REM python examples/mapdl_tyre_performance/project_setup.py --name "Burst Account tests jon" -v "2024_R1" --use-exec-script True --url "%BASE_URL%" --num-jobs=1 --account="%ACCOUNT_TOASTER%" --token="%TOKEN%" --queue="H100:GCP.GPU.H100_1x:nvcf-dgxc-k8s-gcp-euw4-prd1" --signing_key="D:/ansysDev/signing.key"
REM python examples/fluent_nozzle/project_setup.py --name "Fluent Test Jon" -v "2025 R1" --url "%BASE_URL%" --num-jobs=1 --account="%ACCOUNT_TOASTER%" --token="%TOKEN%" --queue="H100:GCP.GPU.H100_1x:nvcf-dgxc-k8s-gcp-euw4-prd1"
python examples/fluent_nozzle/project_setup.py --name "Fluent Study Group" -v "2025 R2" --url "%BASE_URL%" --num-jobs=1 --account="%ACCOUNT_ANYWHERE%" --token="%TOKEN%"

REM --queue="nvcr.io/0689451191675035/evaluator-fluent:25.2.5"
REM --queue="H100:GCP.GPU.H100_8x:nvcf-dgxc-k8s-gcp-euw4-prd1"

pause