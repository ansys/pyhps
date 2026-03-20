cd ..
cd dev_env
cd Scripts
call activate.bat
cd ..
cd ..


set BASE_URL=https://test-jms.awsansys11np.onscale.com/hps

set ACCOUNT_TOASTER=0fea8f1b-0f0f-4998-938a-37a62db59481

for /f "delims=" %%a in ('python oidc_pkce.py -u %BASE_URL%') do @set TOKEN=%%a

python examples/fluent_nozzle/project_setup.py --name "NVCF GPU Demo" -v "2025 R2" --url "%BASE_URL%" --num-jobs=1 --account="%ACCOUNT_TOASTER%" --token="%TOKEN%" --queue="H100:GCP.GPU.H100_8x:nvcf-dgxc-k8s-gcp-euw4-prd1"

REM --queue="nvcr.io/0689451191675035/evaluator-fluent:25.2.2"
REM --queue="H100:GCP.GPU.H100_8x:nvcf-dgxc-k8s-gcp-euw4-prd1"

pause