# PyJSCaller

## 用于Py中执行JS代码的调用器。

# 说明
目前仅仅支持Nodejs，以后会加入其他支持。



# 更新说明
* **2019/05/01**
	* 修复生成表达式的错误重用问题。
* **2019/04/11**
	* 上传代码


# 使用方法

使用会话形式实现Nodejs的调用：

### 例：使用Py执行如下JS脚本，执行triMul(triAdd(a, b, c), triAdd(c, b, a), 1)，其中a,b,c是变量。

#### 文件example.js

```javascript
function triAdd(a, b, c){
	return a + b + c;
}

function triMul(a, b, c){
	return a * b * c;
}

```

#### 文件use.py

```python
import PyJSCaller

setNodePath('') # 手动设置Nodejs所在路径

import time
start = time.clock()

a = 2
b = 3
c = 5

with Sesson('example.js') as sess:  # 其中example.js指要调用的JS脚本所在路径。
    triAdd, triMul = sess.require('triAdd', 'triMul')
    res = triMul(triAdd(a, b, c), triAdd(c, b, a), 1)  # 使用方法跟JS中基本一致。
    sess.call(res)  # 告诉sess我要你执行res

    print('PyJSCaller执行时间消耗：%s' % (time.clock() - start))

print('res响应: %s' % res.getValue())  # 将得到最后执行结果 100

print('执行JS脚本总耗时：%s' % (time.clock() - start))

start = time.clock()
# 　如果要调用Nodejs下函数，通过require获取querystring库，来执行stringify。

with Sesson('example.js') as sess:
    require = sess.require('require')

    querystring = require('querystring')  # 获取querystring库
    querystring.require('stringify')  # 告诉sess我要用到querystring的stringify方法

    query_dict = {'one': 2, 'two': [1, 'haha']}

    query_str = querystring.stringify(query_dict)
    # 如果querystring下attr与方法重名，可以使用getMethod()获取方法，如 querystring.getMethod('stringify')

    # 对query_dict进行call是不必须的，sess会自动处理# 依赖关系，只需要call其中需要执行结果的变量即可。
    sess.call(query_str)

    print('PyJSCaller执行时间消耗：%s' % (time.clock() - start))

print('query_str响应: %s' % query_str.getValue())

print('执行JS脚本总耗时: %s' % (time.clock() - start))

```

以下是一次执行输出：

```python

res响应: 100
执行JS脚本总耗时：0.390953550251                  # 其中（PyJSCaller执行时间消耗：0.00109604951766）
query_str响应: two=1&two=haha&one=2
执行JS脚本总耗时: 0.390286426861                  # 其中（PyJSCaller执行时间消耗：0.00126283036506）

```

以下是程序自动生成的代码

```javascript
var ___=[];
___.push([1, 'haha']);
___.push(require('querystring'));
___.push({'two': ___[0], 'one': 2});
___.push(___[1].stringify(___[2]));;
console.log(JSON.stringify(___))

```


### 其中在Sesson.__exit__ 后调用Nodejs执行，所以使用with as，会更加直观显示调用执行区域。

### 使用Sesson.require获取函数方法。

### 注意：不要在JS脚本中对控制台进行输出哦，因为控制台是该项目接收的源，若输出信息将会干扰到接收端，而产生错误。 

# 项目起因

由于在使用PyExecJs中出现的一些问题：

1. 在pyinstaller 中加入-w 去除控制台后出现的黑窗一闪而过的问题。
2. 执行缺少上下文联系，只能执行单条函数。
3. 由于上一问题中频繁IO导致的执行效率低的问题（多条指令时）。


虽然2，3问题可以直接添加JS代码来避免，但是这不优雅。所以就做了这个项目。

# 工作原理

1. 使用subprocess来实现静默调用Nodejs解决问题1。
2. 使用Py对JS的表达式转换，生成对应的JS代码，使用console.log输出表达式结果的JSON。
3. 由以上代码生成临时文件TMP.js，管道运行Nodejs，执行JSON转换成Py数据。


# TO-DO

* [ ] 兼容py2,py3。
* [ ] 兼容Linux。
* [ ] 支持对环境变量的查找，避免手动设置Nodejs路径。
* [ ] 加入对其他JS执行引擎的支持。



# LICENSE
Apache License 2.0