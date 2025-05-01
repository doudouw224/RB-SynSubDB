import pandas as pd
import os

def find_intersection():
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 读取第一个文件（假设是Excel文件）
    # 注意：data.txt实际上是一个制表符分隔的文件，而不是真正的Excel文件
    # 我们使用pandas的read_csv函数并指定分隔符为制表符
    file1_path = os.path.join(current_dir, 'data.txt')
    df1 = pd.read_csv(file1_path, sep='\t')
    
    # 读取第二个文件（CSV文件）
    file2_path = os.path.join(current_dir, 'dataKNN.csv')
    df2 = pd.read_csv(file2_path)
    
    # 获取第一个文件的第一列和第五列
    # 注意：pandas中的列索引从0开始，所以第一列是0，第五列是4
    col1_file1 = df1.iloc[:, 0]  # 第一列（GENE NAME）
    col5_file1 = df1.iloc[:, 4]  # 第五列（Posterior cortex1）
    
    # 获取第二个文件的第一列
    col1_file2 = df2.iloc[:, 0]  # 第一列（GENE NAME）
    
    # 创建一个包含第一个文件第一列和第五列的DataFrame
    result_df = pd.DataFrame({
        '第一个文件第一列': col1_file1,
        '第一个文件第五列': col5_file1
    })
    
    # 找出第一个文件第五列和第二个文件第一列的交集
    intersection = set(col5_file1).intersection(set(col1_file2))
    
    # 筛选出第一个文件中第五列值在交集中的行，并保留对应的第一列
    filtered_df = result_df[result_df['第一个文件第五列'].isin(intersection)]
    
    # 输出结果
    print(f"交集元素数量: {len(intersection)}")
    print("\n第一个文件中第五列在交集中的行，及其对应的第一列值:")
    print(filtered_df)
    
    # 保存结果到CSV文件
    output_path = os.path.join(current_dir, 'intersection_result.csv')
    filtered_df.to_csv(output_path, index=False)
    print(f"\n结果已保存到: {output_path}")

if __name__ == "__main__":
    find_intersection()