# Overview

## Contact me

* Blog -> <https://cugtyt.github.io/blog/index>
* Email -> <cugtyt@qq.com>
* GitHub -> [Cugtyt@GitHub](https://github.com/Cugtyt)

> **本系列博客主页及相关见**[**此处**](https://cugtyt.github.io/blog/k8s/index)

---

来自[kubernetes.io文档](https://kubernetes.io/docs/concepts/overview/)

![](figs/container_evolution.svg)
![](figs/components-of-kubernetes.svg)

## 控制面板组件

控制面板的组件对集群做整体决策，也可以检测和响应集群事件。

### kube-apiserver

用于显示k8s的api，即k8s控制面板的前端。它是面向水平扩容设计的，也就是说用于部署更多的实例。

### etcd

持续高可用的键值存储，用于备份保存所有集群数据。

### kube-scheduler

监视新创建的没有node的Pods，然后给他们挑选需要运行的node。在做调度的时候需要考虑的因素有：单个或者共有的资源需求，硬件软件政策限制，结合和反结合的指定，数据位置，内部负载接口和截止日期。

### kube-controller-manager

运行控制进程，逻辑上每个控制器是一个独立的进程，但是为了避免复杂，他们都编译到一个二进制文件中，运行到单个进程中。

* 节点控制器：在节点不可用时提醒和响应
* 工作控制器：监察一次性的任务，创建Pods运行这些任务直到完成
* 端点控制器：填充在端点对象中
* 服务账户&符号（Token）控制器：为新的命名空间创建默认账户和API访问符

### cloud-control-manager

云控制管理器可以把集群连接到云端，隔离与云端平台交互和集群交互的组件。它只运行在云端，如果在本地运行，你的集群没有这个部分。

可能会有云控制依赖的是：

* 节点控制器：在节点不响应的时候检查节点是不是删掉了
* 路由控制器：在云基础设施中设置路由
* 服务控制器：创建、更新和删除云端负载平衡

## 节点组件

运行在所有节点中，维持pods的运行，为k8s提供运行环境

### kubelet

每个节点的代理，能确保容器运行在一个Pod中。通过一系列机制后，kubelet拿到一系列PodSpecs，确保这些PodSpecs描述的容器正确健康的运行。对于不是k8s创建的容器不负责。

### kube-proxy

网络代理，是服务的一部分。维护节点的网络规则，让Pods可以在集群内外通信。

### 容器运行时

用于负责运行容器。

## 插件

### DNS

所有的集群应该有集群的DNS，他是一个DNS服务器，用于对k8s服务提供记录。由k8s启动的容器自动包括了DNS服务器。

### Web UI

提供了图形界面

### 容器资源监控

记录通用的时序指标，提供UI来查看

### 集群级别的日志

用于保存容器日志到一个中心化的日子存储，提供了搜索和查看的接口。

## k8s对象

k8s对象是k8s系统的持久化实体，用于表示集群的状态。一个k8s对象是一个意图的记录，一旦创建了这个对象，k8s系统就会持续工作保证这个对象存活。创建对象，也就是告诉k8s系统你期望的集群状态。

#### 对象Spec和状态

基本上每个对象包括两个内嵌字段，用于管理对象的配置：Spec和Status。在创建对象时，需要设置spec，它用于描述这个资源应该的状态。Status描述了对象的当前状态，由k8s系统和组件提供和更新。控制面板会持续管理每个对象的当前状态，用于确保满足我们所期望的状态。

例如：在k8s中，Deployment是一个对象用于描述集群中运行一个应用。创建Deployment的时候，就需要设置spec来指定你希望应用运行三个副本。k8s系统读取这个spec，创建三个实例，并更新当前状态来匹配spec。如果其中实例挂掉，会导致当前状态更改，k8s会对这个变化响应，做出更正。

#### 描述k8s对象

通常将配置信息写入yaml文件，并传入kubectl命令，kubectl会将文件转成json来请求API。例子：

``` yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  selector:
    matchLabels:
      app: nginx
  replicas: 2 # tells deployment to run 2 pods matching the template
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
```

使用kubectl apply命令：

`kubectl apply -f https://k8s.io/examples/application/deployment.yaml --record`

#### 必须字段

* `apiVersion` 指定使用的api版本
* `kind` 创建对象的类型
* `metadata` 用于唯一标识对象的数据，包括name, UID, 和可选的namespace
* `spec` 需要的状态

### 对象管理

![](figs/object-management.png)

#### 命令式指令

在使用命令式指令的时候，用户直接在集群的对象上进行操作。把所需要的操作以参数形式传给kubectl。对于初始或者一次性任务是推荐的方法，因为它直接对对象进行操作，也不需要提供任何之前的配置。

`kubectl apply -f https://k8s.io/examples/application/deployment.yaml --record`

优势：
* 指令使用简单的动作词汇
* 指令只需要指定一个改变步骤

劣势：
* 指令不能和代码更改评审过程集成在一起
* 指令不能提供审计追踪
* 指令不能提供记录源
* 指令不能创建新对象的模板template

#### 命令式对象配置

在命令式对象配置中，kubectl命令指定操作，可选参数和至少一个文件。文件必须包含对象的完整定义，形式包括YAML或JSON格式。

`kubectl create -f nginx.yaml` 创建
`kubectl delete -f nginx.yaml -f redis.yaml` 删除两个配置
`kubectl replace -f nginx.yaml` 更新

与命令式指令优势：
* 对象配置可以保存在版本控制中
* 可以集成在评审过程中，支持审计追踪
* 提供模板用于创建新的对象

劣势：
* 对象配置需要对对象模式由基本的理解
* 需要编写专门的YAML文件

与声明式对象配置相比优势：
* 简单容易理解
* 在1.5版中更加成熟

劣势：
* 在文件中工作的很好，目录中不是很好
* 更新现有的对象必须反映在配置文件中，不然在下次替换中会丢失

#### 声明式对象配置

使用声明式对象配置，用户对在本地的对象配置文件操作，不需要定义具体操作。创建更新和删除都由kubectl自动从配置中检测。这样可以在目录中完成，不同的运算用于不同的对象。

先查看更改，再执行：

```
kubectl diff -f configs/
kubectl apply -f configs/
```

递归执行：
```
kubectl diff -R -f configs/
kubectl apply -R -f configs/
```

相比于命令式对象配置的优势：
* 对于对象的更改可以留存
* 对于目录的支持很好，可以对每个对象自动检测操作类型

劣势：
* 声明式更难理解和debug
* 使用diff的部分更新会生成复杂的合并和碎片操作

### 对象名字和ID

每个集群的对象都有一个名字，对于资源类型来说是唯一的。也有一个UID，对于整个集群来说是唯一的。

例如，在一个名字空间中只能有一个Pod名为myapp-1234，但是可以有一个Pod和一个Deployment都为myapp-1234。

对于非唯一的属性，k8s提供了标签label和标记annotation。

#### 名字

名字会对应一个资源URL，例如/api/v1/pods/some-name。

#### UID

k8s系统会生成唯一的UID字符串。

### 名字空间

名字空间用于区分不同环境下不同组/项目的不同用户。

`kubectl get namespace`

```
NAME              STATUS   AGE
default           Active   1d
kube-node-lease   Active   1d
kube-public       Active   1d
kube-system       Active   1d
```

k8s有4个初始名字空间：
* default 默认
* kube-system 由k8s系统创建的
* kube-public 自动创建，所有用户都可以读，主要集群使用，用于被整个集群可见
* kube-node-lease 和每个节点关联的租用对象

#### 在请求时设置名字空间

```
kubectl run nginx --image=nginx --namespace=<insert-namespace-name-here>
kubectl get pods --namespace=<insert-namespace-name-here>
```

设置名字空间偏好

### 标签和选择器

标签是附在对象上的键值对，用于标记对用户相关或有含义的标志属性，对系统本身来说是没有区别的。标签可以用于管理和选择对象的子集，可以在创建时添加或者随后添加，也可以随时更改。

标签可以让用户已松耦合的方式组织系统对象，不需要客户端存储这些映射。

通过标签选择器，用户可以指定对象的一个集合，标签选择器也是k8s中的核心聚合元语。现在API支持两种选择器：基于相等和基于集合。标签选择可以多维，使用都好分割。

基于相等的：

```
environment = production
tier != frontend
environment=production,tier!=frontend
```

另一个用法是让Pod选定node，例如

``` 
apiVersion: v1
kind: Pod
metadata:
  name: cuda-test
spec:
  containers:
    - name: cuda-test
      image: "k8s.gcr.io/cuda-vector-add:v0.1"
      resources:
        limits:
          nvidia.com/gpu: 1
  nodeSelector:
    accelerator: nvidia-tesla-p100
```

基于集合的操作有in，notin和exists，例如

```
environment in (production, qa)
tier notin (frontend, backend)
partition
!partition
```

基于相等的例子：

```
kubectl get pods -l environment=production,tier=frontend
```

基于集合的例子：

``` 
kubectl get pods -l 'environment in (production),tier in (frontend)'
```

#### 服务和ReplicationController

服务面向的pod集合是使用标签选择来定义的，ReplicationController选择的pods也是用标签选择来定义的。

``` JSON
"selector": {
    "component" : "redis",
}
```

``` yaml
selector:
    component: redis
```

``` yaml
selector:
  matchLabels:
    component: redis
  matchExpressions:
    - {key: tier, operator: In, values: [cache]}
    - {key: environment, operator: NotIn, values: [dev]}
```

### 标记

标记可以在对象中附加一些信息，和标签类似：

``` json
"metadata": {
  "annotations": {
    "key1" : "value1",
    "key2" : "value2"
  }
```

这些标记的键值对都只能使用字符串。

一些可以存在标记中的信息例子：
* 由声明配置层管理的字段，附加这些字段可以和默认值进行区分。
* 编译、发行或者镜像的信息，例如时间戳，发布id，分支，pr数，镜像hash，仓库地址。
* 日志，监视器，分析和审计仓库的地址
* 客户端库和工具信息，用于debug
* 用户或者工具出处信息，例如其他系统组件的关联对象URL
* 轻量试运行工具元数据，例如配置和检验点
* 负责人的联系方式，项目组的网站
* 用户修改的行为指令

### 字段选择器

可以做到以下查询：

```
metadata.name=my-service
metadata.namespace!=default
status.phase=Pending
```

`kubectl get pods --field-selector status.phase=Running`

支持的字段：所有的k8s资源类型都支持metadata.name和metadata.namespace。对于不支持的字段，会产生错误：

```
kubectl get ingress --field-selector foo.bar=baz 

Error from server (BadRequest): Unable to find "ingresses" that match label selector "", field selector "foo.bar=baz": "foo.bar" is not a known field selector: only "metadata.name", "metadata.namespace"
```

可以使用逗号分割多个选择进行串联，

`kubectl get pods --field-selector=status.phase!=Running,spec.restartPolicy=Always`

### Finalizers 终结器

终结器是名字空间的键，告诉k8s等待条件满足后再删除资源，它提醒控制器清理对象所拥有的资源。在所有执行完成后，控制器会移除对应的终结器，当`meta.finalizers`字段为空的时候，k8s会认为删除完成。

通常，终结器不需要指定执行代码，而是指定一些特定的资源键，类似于标记。k8s会自动具化代码。

#### 终结器如何运作

在创建一个配置文件时，你可以指定`metadata.finalizers`。当你尝试去删除资源时，控制器会注意到这些值在终结器中，它会：
* 更改对象，添加`metadata.deletionTimestamp`字段为你开始删除的时间
* 把对象设为只读，直到`metadata.finalizers`字段为空

控制器会尝试满足删除器的要求，当要求满足后，控制器移除资源的`finalizers`中的键，在这个字段为空后，垃圾回收继续。

一个例子是`kubernetes.io/pv-protection`，它可以防止误删除`PersistentVolume`对象，当`PersistentVolume`在Pod还使用的时候，k8s会添加`pv-protection`终结器。尝试删除`PersistentVolume`时，它会进入`Terminating `状态，但是控制器无法删除。在Pod停止使用`PersistentVolume`时，k8s清理`pv-protection`终结器，控制器删除它。

### 所有者Owners和依赖Dependents

一些对象时其他对象的所有者，例如ReplicaSet时一些Pods的所有者，这些Pod依赖于他们的所有者。

所有者不同于标签和选择器，例如一个服务创建了`EndpointSlice`对象，这个服务使用标签来让控制面板决定哪些`EndpointSlice`在服务中使用。除了标签，每个`EndpointSlice`受服务的所有者引用管理，所有者引用让k8s防止干扰他们不能控制的对象。

依赖对象有一个`metadata.ownerReferences`字段来引用他们的所有者对象。一个可用的所有者引用包括对象名字和UID。这些值由k8s自动设置所有对象为ReplicationSet，DaemonSet，Deployment，Jobs，CronJons和ReplicationController的值。你也可以自己手动更改这些值。

依赖对象有一个`ownerReferences.blockOwnerDeletion`的字段，是一个布尔值，控制特定的依赖不让垃圾回收删除他们的拥有者对象。如果一个控制器设置了`metadata.ownerReferences`，k8s会自动把这个字段设置为true。也可以自己手动指定。

### 推荐的标签

![](figs/common-labels.png)

``` yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  labels:
    app.kubernetes.io/name: mysql
    app.kubernetes.io/instance: mysql-abcxzy
    app.kubernetes.io/version: "5.7.21"
    app.kubernetes.io/component: database
    app.kubernetes.io/part-of: wordpress
    app.kubernetes.io/managed-by: helm
    app.kubernetes.io/created-by: controller-manager
```

考虑一个简单的使用Deployment和Service对象部署的无状态stateless服务。下面一个简单示例展示了标签的用法：

``` yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app.kubernetes.io/name: myservice
    app.kubernetes.io/instance: myservice-abcxzy
...
```

``` yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app.kubernetes.io/name: myservice
    app.kubernetes.io/instance: myservice-abcxzy
...
```

考虑一个稍微复杂的应用：网页应用（WordPress）使用数据库（MySQL），使用Helm安装。

``` yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app.kubernetes.io/name: wordpress
    app.kubernetes.io/instance: wordpress-abcxzy
    app.kubernetes.io/version: "4.9.4"
    app.kubernetes.io/managed-by: helm
    app.kubernetes.io/component: server
    app.kubernetes.io/part-of: wordpress
...
```

``` yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  labels:
    app.kubernetes.io/name: mysql
    app.kubernetes.io/instance: mysql-abcxzy
    app.kubernetes.io/version: "5.7.21"
    app.kubernetes.io/managed-by: helm
    app.kubernetes.io/component: database
    app.kubernetes.io/part-of: wordpress
...
```

``` yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app.kubernetes.io/name: mysql
    app.kubernetes.io/instance: mysql-abcxzy
    app.kubernetes.io/version: "5.7.21"
    app.kubernetes.io/managed-by: helm
    app.kubernetes.io/component: database
    app.kubernetes.io/part-of: wordpress
...
```