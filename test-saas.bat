cd dev_env
cd Scripts
call activate.bat
cd ..
cd ..

set TOKEN=eyJhbGciOiJSUzI1NiIsImtpZCI6ImNWQWZMRlQyZS1qT1A2QmlmOUxvRGRRaC1kdC1sazlpa2Fab0EzY0U2bWsiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJkY2UyNjc3My03NTZkLTQ2NzEtYjJlNC05ZTEyZmZlZDA3ZjYiLCJpc3MiOiJodHRwczovL2EzNjVkZXYuYjJjbG9naW4uY29tL2NhNGZmNDVhLTI3MzMtNDBkNS1hNGIyLTNjMGYzMDhiYWM5MS92Mi4wLyIsImV4cCI6MTcyODY2NjY3NCwibmJmIjoxNzI4NjYzMDc0LCJzdWIiOiJmZDUyZTc1ZC1mNzJlLTQyMTItYTczYy00ZjY3NGI5NWExZjciLCJlbWFpbCI6Impvbi5ub3Zha0BhbnN5cy5jb20iLCJ0aWQiOiIzNGM2Y2U2Ny0xNWI4LTRlZmYtODBlOS01MmRhOGJlODk3MDYiLCJnaXZlbl9uYW1lIjoiSm9uIiwiZmFtaWx5X25hbWUiOiJOb3ZhayIsIm5hbWUiOiJKb24gTm92YWsiLCJVSUQiOiJmZDUyZTc1ZC1mNzJlLTQyMTItYTczYy00ZjY3NGI5NWExZjciLCJub25jZSI6IlJIaEhiWGRDZFUxM0xYVmlTRmt4YTBSM2IwSTVlbGhUVlUxTVpVMVBjVVZxT1dOaGRVaG9YMVZ6YmpSNCIsInNjcCI6IkxpY2Vuc2luZ0FzQVNlcnZpY2UiLCJhenAiOiIwMDgzNWJjZC00MjQ1LTRkNjEtOTE5Yy1jYzhjMzdkYjdkN2YiLCJ2ZXIiOiIxLjAiLCJpYXQiOjE3Mjg2NjMwNzR9.XpLD-sfreesXukT0L28O5nYqbIdOLjpwAdA4z-Ir-NFG_rwZ8y78b8tIFGekGAr8wfVXlKPlVC7FkEcJVhbXjCGBnThdR2GORJVIo3WAszVWIvK66nDpjkP4WGyVjbgzrrLm10Engvz7XuKhbxQlj-W4QpC3gg4fOstoyFJmUB2v8zM_d43N_V41s38xdnwECKjkyg0EAOvhS6rHrPF_FaBTCR5mk0BZipa8OycZ20SDYfKqVDh8DpOK2lUnx8J-a9eWF9l_rU_LSNXI0aLSLwh-8xFguXr4ItnjC8NfrxHCFZ_js4Bl2HMiYP9WYWdoq9Zd3bRnoyFX0hEKQiKCEQ
set BASE_URL=https://dev-jms.awsansys11np.onscale.com/hps
set ACCOUNT=30b226d7-aa1b-4001-b763-f88525abde4d

python examples/generic_api/project_setup.py --urls "%BASE_URL%"  --accounts "%ACCOUNT%" --token=%TOKEN%
python examples/mapdl_tyre_performance/project_setup.py --name "Burst Account tests" -v "2025 R1" --url "%BASE_URL%" --num-jobs=1 --account="%ACCOUNT%" --token=%TOKEN%
python examples/generic_api/project_setup.py --urls "%BASE_URL%"  --accounts "%ACCOUNT%" --token=%TOKEN%
REM python project_setup.py --urls "%BASE_URL%" --accounts "onprem_account" --token=%TOKEN% REM --verbose=True
REM python project_setup.py --urls "%BASE_URL%"  --accounts "30b226d7-aa1b-4001-b763-f88525abde4d" "0fea8f1b-0f0f-4998-938a-37a62db59481" --token=%TOKEN%

pause