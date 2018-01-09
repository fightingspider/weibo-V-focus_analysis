import pymongo
import networkx as nx
from matplotlib import pyplot as plt,font_manager
import re
'''
    描述：从mongo数据库中筛选数据并提取，利用network包分析并绘制社交网络图
    如果无法显示中文，可以通过linux命令fc-list :lang=zh 查看中文字体文件地址，
    将matplotlib/mpl-data/fonts/DejaVuSans.ttf 替换成你选择的字体文件
    或者font-family= 临时修改
'''
#建立mongo数据库连接
client = pymongo.MongoClient('127.0.0.1',27017)
#实例化一个数据库操作对象，指明数据库名称
db = client.weibo
#构建查询语句，从数据库中提取数据
query = {'fans_num':{'$gt':5000000}}
V = db.focus.find(query)
#构建符合导入格式的数据结构，[(),(),(),()],剔除包含微博关键字的官方账号
V_list = [(v['focus_by'],v['name']) for v in V if not re.search('微博',v['name'])]
#初始化
plt.figure(figsize=(18,10),dpi=80)
G = nx.Graph(V_list)
#获取节点的度，Graph.degree()=DiGraph.out_degree()+DiGraph.in_degree()，在无向图中，全图的度数等于有向图中初度和入度之和
degree = G.degree()
#绘图，拥有更多关注关系的账户，点越大
nx.draw(G, pos=nx.spring_layout(G), with_labels = True, node_shape='*',node_size = [ (5*num)**2 for num in degree.values()],node_color='orange',edge_color='dodgerblue',width=0.5,font_size=10)
#保存绘制图片
plt.savefig('./V_focus_network.png')
#展示
plt.show()

