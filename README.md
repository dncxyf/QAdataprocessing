# 使用python进行医疗专业问卷调研数据分析
### 1.项目在做什么？
针对qc(quality control)后的问卷调研数据，使用python程序输出多维度聚合分析数据，用于研究报告展示和业务洞察。

说明：sample数据已脱敏。数据label信息以label+序号代替、问卷数据的题目标题以question+序号代替
### 2.实现过程
#### （1）列名标号（function_update.py--readxl）
将问卷数据的复杂长列名，用标号表示（q1，q2，...），用于查询和指定列名；同时保存反向字典，用于最终输出表格
#### （2）索引标记（function_update.py--make_index）
接受列名，输出用于function表的index，包括每个问题的标题，对应excel的起始、终止标记点，后续在function表上设置对于每个问题的计算函数和函数内参数
#### （3）计算函数（function_update.py）
mean_percentage(data, columns_d, column, name, percentage=0,sheet_name='Sheet1')

给定列的范围（根据索引和标记点），输出对应列的平均数，以及比例

vc(data, columns_d, column, name,base='sum',sheet_name='Sheet1')

给定列的范围，对每一列进行value_count,并输出value count的比例,以index合并输出

mean_arrange(data, columns_d, column, name, n, missing_data=np.nan, sheet_name='Sheet1')

给定列的范围，排除异常值nan，计算平均值，根据n拆分排列，并输出

例：

输入列：

| a1-b1 | a1-b2 | a2-b1 | a2-b2 | a3-b1 | a3-b2 |
|----|----|----|----|----|----|
| 数值 | 数值 | 数值 | 数值 |数值 | 数值 |
| 数值 | 数值 | 数值 | 数值 |数值 | 数值 |

输出列：

|    | a1 | a2 | a3 |
|----|----|----|----|
| b1 | 数值 | 数值 | 数值 |
| b2 | 数值 | 数值 | 数值 |

sum_percentage(data, columns_d, column, name, n, sheet_name='Sheet1')

给定列的范围column和base column，计算加权平均数
#### （4）维度拆分函数（function_update.py--break_down）
根据列名序号指定拆分列，拆分data，以dataframe形式存在列表里
#### （5）设置function参数表
在（2）索引标记的基础上，根据报告需要的计算类型，选择function，并设置参数，格式如下：

| title | start | end   | function | n  | nan | vc_base | index |columns|
|----|----|----|----|----|----|----|----|----|
|标题|起始标记点|终止标记点|聚合函数|参数| 参数 |参数|参数|参数|

#### （7）执行输出（sample_data_implement.ipynb）
输入：

a.清洗后的数据sample_data_脱敏.xlsx → 维度拆分后以多个dataframe存在input_dict字典中

b.函数参数表function_sample.xlsx → 转为字典func_dict以供调用

输出：

output.xlsx
### 3.评价
#### （1）优点
一次性输出报告所需的所有维度数据，效率高，复用性高，使得项目团队有更多时间在数据驱动的业务洞察上；
项目过程中有数据调整时，可以快速输出新一版数据以供参考。
#### （2）缺点
在output表过千行时，效率有所降低（10+min），对于长问卷、多维度可以根据需求考虑分表输出。
