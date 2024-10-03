cd dev_env
cd Scripts
call activate.bat
cd ..
cd ..

set TOKEN=eyJhbGciOiJSUzI1NiIsImtpZCI6ImNWQWZMRlQyZS1qT1A2QmlmOUxvRGRRaC1kdC1sazlpa2Fab0EzY0U2bWsiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJkY2UyNjc3My03NTZkLTQ2NzEtYjJlNC05ZTEyZmZlZDA3ZjYiLCJpc3MiOiJodHRwczovL2EzNjVkZXYuYjJjbG9naW4uY29tL2NhNGZmNDVhLTI3MzMtNDBkNS1hNGIyLTNjMGYzMDhiYWM5MS92Mi4wLyIsImV4cCI6MTcyNzk3Mzg0NiwibmJmIjoxNzI3OTcwMjQ2LCJzdWIiOiJmZDUyZTc1ZC1mNzJlLTQyMTItYTczYy00ZjY3NGI5NWExZjciLCJlbWFpbCI6Impvbi5ub3Zha0BhbnN5cy5jb20iLCJ0aWQiOiIzNGM2Y2U2Ny0xNWI4LTRlZmYtODBlOS01MmRhOGJlODk3MDYiLCJnaXZlbl9uYW1lIjoiSm9uIiwiZmFtaWx5X25hbWUiOiJOb3ZhayIsIm5hbWUiOiJKb24gTm92YWsiLCJVSUQiOiJmZDUyZTc1ZC1mNzJlLTQyMTItYTczYy00ZjY3NGI5NWExZjciLCJub25jZSI6ImJsZC1Vak5sY0ZsYWMyNDFaa3BZY0MxeFJtdHFZVTVzUm5wNUxrZFFiV2haYzIxZmJHbDNSR05GWmxKUiIsInNjcCI6IkxpY2Vuc2luZ0FzQVNlcnZpY2UiLCJhenAiOiIwMDgzNWJjZC00MjQ1LTRkNjEtOTE5Yy1jYzhjMzdkYjdkN2YiLCJ2ZXIiOiIxLjAiLCJpYXQiOjE3Mjc5NzAyNDZ9.mhpEWOJZU3DSv6-k7If39dasDqsLfrTzNo-TjZTaJvDBXTZwIStpCKNUNz95Amz7JXEqzEtUzo7IG2s1QESlnv4CTbVTpAFyvY1-3al6U7kONVShlc0B9lJbXVgOsIf_Z_-Iu5i9sWRjVskbgrHQ3I-pXSB_pm7vQWSvSNOXFr3hmyc1bz8vN0ve149dew0HExr4e97sWgULAo8yrvGqJ6muLx9bR_tE-G1e6fuHnVH8FnnTTcbK_lxJKYgrsHkmxN7j3avhMIi-eGu0wFUWDGIPmTOJWSGpZCeq21p5kzRme3fEsW7Sw05NG6jK8VCiV12bbXF1GwcfCOdVi2FU7w

python examples/generic_api/project_setup.py --urls "https://dev-jms.awsansys11np.onscale.com/hps"  --accounts "0fea8f1b-0f0f-4998-938a-37a62db59481" --token=%TOKEN%
python examples/mapdl_tyre_performance/project_setup.py --name "New tests" -v "2025 R1" --url "https://dev-jms.awsansys11np.onscale.com/hps" --num-jobs=1 --account="0fea8f1b-0f0f-4998-938a-37a62db59481" --token=%TOKEN%
python examples/generic_api/project_setup.py --urls "https://dev-jms.awsansys11np.onscale.com/hps"  --accounts "0fea8f1b-0f0f-4998-938a-37a62db59481" --token=%TOKEN%
REM python project_setup.py --urls "https://test-jms.awsansys11np.onscale.com/hps" --accounts "onprem_account" --token=%TOKEN% REM --verbose=True
REM python project_setup.py --urls "https://dev-jms.awsansys11np.onscale.com/hps"  --accounts "30b226d7-aa1b-4001-b763-f88525abde4d" "0fea8f1b-0f0f-4998-938a-37a62db59481" --token=%TOKEN%

pause