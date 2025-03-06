import argparse
import pandas as pd
import matplotlib.pyplot as plt
import json
import re
import sys
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import matplotlib
sys.path.append(".")
from question_config import QuestionConfig,QuestionInfoManager

def match_pattern(prefix: str,input: str):
    safe_prefix = re.escape(prefix)
    pattern = rf".*{safe_prefix}_([^_]+)_.*"
    matched_content = re.search(pattern, input).group(1)
    return matched_content

def process_file(file_name):
    """处理文件的函数"""
    
    turn_num = match_pattern("turn_num",file_name)
    question_type = match_pattern("question_type",file_name)
    noun = match_pattern("noun",file_name)
    sensory = match_pattern("sensory",file_name)
    print("question_type:",question_type)  # 输出：create
    
    with open(file_name,'r',encoding='utf-8') as file:
        answer_data = json.load(file)
    
    question_info_manager = QuestionInfoManager()

    if question_type == "create":
        print("create")
        answer_summary = {noun_content:{sensory:[],"confidence_level":[]} for noun_content in question_info_manager.noun_dict[noun]}
        for turn_key,answer_data in answer_data['content'].items():
            for i,(question_index, answer_output) in enumerate(answer_data.items()):
                filtered_answer_output = re.search(r'【(.*?)，(.*?)】', answer_output)
                if filtered_answer_output:
                    color = str(filtered_answer_output.group(1).strip())      # 提取颜色
                    confidence_level = int(filtered_answer_output.group(2).strip())  # 提取自信程度并转换为整数
                    print(f"颜色: {color}")
                    print(f"自信程度: {confidence_level}")
                    answer_summary[question_info_manager.noun_dict[noun][i]][sensory].append(color)
                    answer_summary[question_info_manager.noun_dict[noun][i]]["confidence_level"].append(confidence_level)
                else:
                    print(answer_output)
                    print("未找到匹配的内容")
        print(answer_summary)
        return answer_summary,sensory

def create_matrix(data,sensory):
    # Get all unique colors
    all_sensories = set()
    for word_data in data.values():
        all_sensories.update(word_data[sensory])
    all_sensories = sorted(all_sensories)  # Sort for consistent ordering

    # Initialize an empty dictionary for aggregation
    matrix_data = {word: {sensory: [] for sensory in all_sensories} for word in data.keys()}

    # Fill the dictionary with values
    for word, word_data in data.items():
        for color, confidence in zip(word_data[sensory], word_data['confidence_level']):
            matrix_data[word][color].append(confidence)

    # Compute the mean for each word-color pair
    for word in matrix_data:
        for color in matrix_data[word]:
            values = matrix_data[word][color]
            matrix_data[word][color] = np.sum(values) if values else 0


    # Convert to DataFrame
    return pd.DataFrame(matrix_data).T  # Transpose for words as rows, colors as columns


def plot_data(matrix_df):
    """绘制图表的函数"""
    def purple_alpha_colormap():
        colors = [(0.5, 0, 0.5, 0), (0.5, 0, 0.5, 1)]  # RGBA: Transparent to fully opaque purple
        return LinearSegmentedColormap.from_list("purple_alpha", colors)
    cmap = purple_alpha_colormap()
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
    # Plot the matrix as a heatmap
    plt.figure(figsize=(10, 6))
    plt.imshow(matrix_df, cmap=cmap, aspect="auto")
    plt.colorbar(label="Mean Value")
    plt.xticks(ticks=range(len(matrix_df.columns)), labels=matrix_df.columns, rotation=45)
    plt.yticks(ticks=range(len(matrix_df.index)), labels=matrix_df.index)
    plt.title("Word-Color Mapping of Non Gender Chinese Feedback (Sum Values)")
    plt.xlabel("Colors")
    plt.ylabel("Words")
    plt.show()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="处理文件与作图")
    parser.add_argument('-f', '--file_name', type=str,  help='filename')

    args = parser.parse_args()
    print(args.file_name)
    # try:
        # 处理文件
    processed_data,sensory = process_file(args.file_name)
        # 绘制图表
        # plot_data(processed_data)
    matrix_df = create_matrix(processed_data,sensory)
    print(matrix_df)
    plot_data(matrix_df)
    print("操作完成")

    # except FileNotFoundError:
    #     print(f"错误：找不到文件 {args.file_name}")
    # except Exception as e:
    #     print(f"发生未知错误: {str(e)}")
