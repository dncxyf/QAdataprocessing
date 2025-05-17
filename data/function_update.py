import numpy as np
import pandas as pd
import os
from decimal import Decimal, ROUND_HALF_UP


def round(number, ndigits=None):
    """强制四舍五入"""
    exp = Decimal('1.{}'.format(ndigits * '0')) if ndigits else Decimal('1')
    return type(number)(Decimal(number).quantize(exp, ROUND_HALF_UP))


def readxl(name, sheet_name):
    """接受文件名（指定目录的前提下），转为dataframe，改index并输出"""
    data = pd.read_excel('input/'+name, sheet_name=sheet_name).dropna(how='all')
    column_list = data.columns.tolist()
    column_d = {}
    column_d1 = {}
    for i in range(len(column_list)):
        x1 = 'q' + str(i + 1)
        column_d[column_list[i]] = x1
        column_d1[x1] = column_list[i]

    data1 = data.rename(columns=column_d)
    data_column_d1 = pd.DataFrame(column_d1, index=['content']).T
    if not os.path.exists('index/index_' + name):
        data_column_d1.to_excel('index/index_' + name)
    return data1, column_d1

def mean_percentage(data, columns_d, column, name, percentage=0,sheet_name='Sheet1'):
    """给定列数，输出列数的平均数，以及给定列数下的比例"""
    if type(column) == str:
        column = column.split(' ')
        column = ['q' + str(i) for i in range(int(column[0]), int(column[1]) + 1)]
        # column = ['q'+i for i in column.split()]
        # print(column)
    else:
        column = ['q' + str(column)]
    x = data[column]
    # .apply(lambda x: [np.nan if x[i] == missing_data else x[i] for i in range(len(x))])
    mean = x.mean()
    mean1 = pd.DataFrame(mean).T.rename(columns=columns_d)
    count = x.count()
    count1 = pd.DataFrame(count).T.rename(columns=columns_d)
    if percentage == 0:
        z = pd.concat([count1, mean1]).set_index(pd.Series(['n', 'mean']))
    else:
        p = mean.div(mean.sum()).rename(index=columns_d)
        p1 = pd.DataFrame(p).T
        z = pd.concat([count1,mean1, p1]).set_index(pd.Series(['n', 'mean', 'percentage']))
    name = pd.Series(name)
    with pd.ExcelWriter('output.xlsx', mode='a', if_sheet_exists='overlay') as writer:
        df1 = pd.DataFrame(pd.read_excel('output.xlsx', sheet_name=sheet_name))
        df_rows = df1.shape[0]
        name.to_excel(writer, sheet_name=sheet_name, header=False, index=False, startrow=df_rows + 3)
        z.to_excel(writer, sheet_name=sheet_name, startrow=df_rows + 4)
    return z

def vc(data, columns_d, column, name,base='sum',sheet_name='Sheet1'):
    """给定列的范围，对每一列进行value_count,并输出value count的比例,以index合并输出"""
    if type(column) == str:
        column = column.split(' ')
        column = ['q' + str(i) for i in range(int(column[0]), int(column[1]) + 1)]
        # column = ['q'+i for i in column.split()]
        # print(column)
        vc_list = []
        for i in column:
            x = data[i].value_counts().sort_index()
            vc_list.append(x)
        x1 = pd.concat(vc_list,axis=1)
        x1 = x1.fillna(0)
        x1.columns = column
        x1 = x1.rename(columns=columns_d)
        if base == 'shape':
            x2 = x1.apply(lambda x: x / data.shape[0], axis=0)
        else :
            x2 = x1.apply(lambda x: x / x.sum(), axis=0)
        x2_format = x2.applymap(lambda x:str(int(round(x*100)))+'%' if not pd.isna(x) else x)
        x3 = pd.concat([x1, x2, x2_format], axis=1)
    else:
        column = 'q'+str(column)
        x1 = data[column].value_counts().sort_index()
        x2 = x1.apply(lambda x: x / x1.sum())
        x2_format = x2.map(lambda x:str(int(round(x*100)))+'%' if not pd.isna(x) else x)
        x3 = pd.concat([x1, x2,x2_format], axis=1).reset_index()
        x3.columns=[column,'count','percentage','format_percentage']
        x3 = x3.rename(columns=columns_d)
        x3 = x3.set_index(x3.columns[0])
    name = pd.Series(name)
    with pd.ExcelWriter('output.xlsx', mode='a', if_sheet_exists='overlay') as writer:
        df1 = pd.DataFrame(pd.read_excel('output.xlsx', sheet_name=sheet_name))
        df_rows = df1.shape[0]
        name.to_excel(writer, sheet_name=sheet_name, header=False, index=False, startrow=df_rows + 3)
        x3.to_excel(writer, sheet_name=sheet_name, startrow=df_rows + 4)
    return x3


def mean_arrange(data, columns_d, column, name, n, missing_data=np.nan, sheet_name='Sheet1'):
    """排除异常值nan，计算平均值，根据n拆分排列，输出表格"""
    column = column.split(' ')
    column = ['q' + str(i) for i in range(int(column[0]), int(column[1]) + 1)]
    n = int(n)
    re = data[column]
    # re = re.apply(lambda x: [np.nan if x[i] == missing_data else x[i] for i in range(len(x))])
    mean = re.mean(numeric_only=True)
    count = re.count()
    index = mean.iloc[:n].index
    if len(mean) == len(count):
        pass
    else:
        print('检查是否有非数值')
    d_count,d_mean = {},{}
    for i in index:
        d_count[i] = []
        d_mean[i] = []

    a = 0
    for i in d_count.keys():
        for j in range(len(count) // n):
            d_count[i].append(count.iloc[n * j + a])
        a += 1
    a = 0
    for i in d_mean.keys():
        for j in range(len(mean) // n):
            d_mean[i].append(mean.iloc[n * j + a])
        a += 1

    d_count['index'] = []
    d_mean['index'] = []
    for i in range(len(count) // n):
        x = count.index[n * i]
        d_count['index'].append(x)
    for i in range(len(mean) // n):
        x = mean.index[n * i]
        d_mean['index'].append(x)

    k_count = pd.DataFrame(d_count).set_index('index').rename(index=columns_d, columns=columns_d)
    # 功能备注：pdt推广活动部分输出coverage
    # k_count_percentage = k_count.map(lambda x:x/data.shape[0])
    # k_count = pd.concat([k_count,k_count_percentage],axis=1)
    k_mean = pd.DataFrame(d_mean).set_index('index').rename(index=columns_d, columns=columns_d)
    # print(k_count,k_mean)
    # k = pd.concat([k_count,k_mean],axis=0)
    name = pd.Series(name)
    with pd.ExcelWriter('output.xlsx', mode='a', if_sheet_exists='overlay') as writer:
        df1 = pd.DataFrame(pd.read_excel('output.xlsx', sheet_name=sheet_name))
        df_rows = df1.shape[0]
        name.to_excel(writer, sheet_name=sheet_name, header=False, index=False, startrow=df_rows + 3)
        pd.Series('base').to_excel(writer, sheet_name=sheet_name, header=False, index=False, startrow=df_rows + 4)
        k_count.to_excel(writer, sheet_name=sheet_name, startrow=df_rows + 5)
        pd.Series('mean').to_excel(writer, sheet_name=sheet_name, header=False, index=False,startrow=df_rows +5+ len(count)//n+1)
        k_mean.to_excel(writer, sheet_name=sheet_name, startrow=df_rows +5+ len(count)//n+2)

    return k_mean


def break_down(data, index,break_down_d,index_name=False):
    """获得根据index区分的data，存在列表里"""
    index = 'q' + str(index)
    if index_name == False:
        list_unique = data[index].unique().tolist()
    else:
        list_unique = index_name
    for i in range(len(list_unique)):
        break_down_d[list_unique[i]] = data[data[index] == list_unique[i]].reset_index(drop=True)
    print(list_unique)
    return break_down_d

def xy(data,percent=False,decimals=1):
    """两期数据对比，暂时不用"""
    x,y = pd.read_excel(data,sheet_name=0),pd.read_excel(data,sheet_name=1)
    if x.shape == y.shape:
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                if pd.isna(x.iloc[i,j]) or type(x.iloc[i,j]) == str:
                    pass
                else:
                    if percent==False:
                        k1 = np.around(x.iloc[i,j]-y.iloc[i,j],decimals=1)
                        k2 = np.around(x.iloc[i,j],decimals=decimals)
                        if k1>0:
                            x.iloc[i,j] = str(k2)+'(+'+str(k1)+')'
                        elif k1==0:
                            x.iloc[i,j] = str(k2)+'(--)'
                        else:
                            x.iloc[i,j] = str(k2)+'('+str(k1)+')'
                    else:
                        k1 = int(np.rint((x.iloc[i,j]-y.iloc[i,j])*100))
                        k2 = int(np.rint(x.iloc[i,j]*100))
                        if k1>0:
                            x.iloc[i,j] = str(k2)+'%(+'+str(k1)+'%)'
                        elif k1==0:
                            x.iloc[i,j] = str(k2)+'%(--)'
                        else:
                            x.iloc[i,j] = str(k2)+'%('+str(k1)+'%)'
    else:
        print('shape不匹配')
    x.to_excel('xy_'+data,index=False)
    return x

def make_index(list_alpha):
    """接受列名，输出用于function表的index，包括每个问题的标题，对应excel的起始、终止标记点，后续在function表上设置对于每个问题的计算函数和函数内参数"""
    list_sp = []
    list_index_p = []
    list_index_n = []
    for i in list_alpha:
        sp = i.split('[')
        #print(sp[0])
        list_sp.append(sp[0])
    list_sp_set = []
    list_sp_set.append(list_sp[0])#元素标记1
    list_index_p.append(1)#起始标记1
    list_index_n.append(1)#结束标记1#默认第一个和第二个不重复
    for i in range(1,len(list_sp)):
        if list_sp[i] != list_sp[i-1]:
            list_sp_set.append(list_sp[i])
            list_index_p.append(i+1)
            if i<len(list_sp)-1:
                if list_sp[i] != list_sp[i+1]:
                    list_index_n.append(i+1)
            else:
                list_index_n.append(i+1)
        else:
            if list_sp[i] != list_sp[i+1]:
                list_index_n.append(i+1)

    df = pd.DataFrame()
    df = pd.concat([df,pd.DataFrame(list_sp_set,columns=['title']),pd.DataFrame(list_index_p,columns=['start']),pd.DataFrame(list_index_n,columns=['end'])],axis=1)
    df.to_excel('function/function_row.xlsx',index=False)


def sum_percentage(data, columns_d, column, name, n, sheet_name='Sheet1'):
    """给定列数column和base column，计算加权平均数"""
    if type(column) == str:
        column = column.split(' ')
        column = ['q' + str(i) for i in range(int(column[0]), int(column[1]) + 1)]
        # column = ['q'+i for i in column.split()]
        # print(column)
    else:
        column = ['q' + str(column)]
    x = data[column]
    #x = x.fillna(0)
    if type(n) == int:
        n = ['q' + str(n)]
    else:
        n = n.split(' ')
        n = ['q' + str(i) for i in n]
    y = 1
    z = pd.DataFrame()
    for i in n:
        y = y * data[i]
        #print(y.shape)
    for i in column:
        z[i] = y * x[i]
    # .apply(lambda x: [np.nan if x[i] == missing_data else x[i] for i in range(len(x))])
    z_sum = z.sum() / y.sum()
    z_sum1 = pd.DataFrame(z_sum).T.rename(columns=columns_d)
    count = x.count()
    count1 = pd.DataFrame(count).T.rename(columns=columns_d)
    z_sum2 = pd.concat([count1, z_sum1]).set_index(pd.Series(['n', 'percentage']))

    name = pd.Series(name)
    with pd.ExcelWriter('output.xlsx', mode='a', if_sheet_exists='overlay') as writer:
        df1 = pd.DataFrame(pd.read_excel('output.xlsx', sheet_name=sheet_name))
        df_rows = df1.shape[0]
        name.to_excel(writer, sheet_name=sheet_name, header=False, index=False, startrow=df_rows + 3)
        z_sum2.to_excel(writer, sheet_name=sheet_name, startrow=df_rows + 4)
    return z_sum2