```bash
https://pypi.org/
OpsApi
TM5

vi ~/.pypirc
[pypi]
  username = __token__
  password = pypi-AgEIcHlwaS5vcmcCJGIwN2FjNDQ3LTI1NTItNDg3MS1iOWY2LWNkYzhkY2IwOGU3MgACKlszLCJkNjVkM2U3NS03M2JlLTQ1NzMtOGMwYi04NTVhZTZkMmNhMDYiXQAABiAjkMNGlacLx_E8WO1Vt4CrUnEBt5f5sF1Ta_xSZlkS7Q
  
/Users/tongming/py_vm/netbug/bin/python -m pip install --upgrade twine
/Users/tongming/py_vm/netbug/bin/python -m pip install --upgrade build
cd /Users/tongming/ops/code/python/tmutils
/Users/tongming/py_vm/netbug/bin/python -m build
/Users/tongming/py_vm/netbug/bin/twine upload dist/*.gz
输入密码即可

查看项目
https://pypi.org/project/tmutils/


cd /Users/tongming/ops/code/python/tmutils
这里打包比较麻烦就用shell脚本操作
chmod +x build_upload.sh
./build_upload.sh 0.0.2

```