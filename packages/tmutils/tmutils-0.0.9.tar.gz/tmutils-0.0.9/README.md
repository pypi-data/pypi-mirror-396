```bash
https://pypi.org/
OpsApi
TM5

[pypi]
  username = __token__
  password = pypi-AgEIcHlwaS5vcmcCJDMyMTliY2FjLWVlZGQtNDFhYy1hOGY1LTFiNTIwNjc4NzI5ZAACKlszLCJkNjVkM2U3NS03M2JlLTQ1NzMtOGMwYi04NTVhZTZkMmNhMDYiXQAABiB94H-g1B1WELz1WImIk6WR0EWkKiP3qDK4VDbZV9gErg

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