import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.stats.multitest import multipletests
import numpy as np
import os
import subprocess

## 全局变量设置
project_dir   = "/SGRNJ03/pipline_test/datascience/zhangjinbo/projects/streamlit/test/"
r_script_path = '/SGRNJ03/pipline_test/datascience/zhangjinbo/projects/streamlit/DESeq2.r'


def create_user_temp_dir(user_id):
    # 构造用户的临时文件夹路径
    temp_dir = os.path.join(project_dir, "user_" + user_id)
    # 创建用户临时文件夹（如果不存在）
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    return temp_dir


def get_sessionID():
    from streamlit.runtime import get_instance
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    runtime = get_instance()
    session_id = get_script_run_ctx().session_id
    session_info = runtime._session_mgr.get_session_info(session_id)
    if session_info is None:
        raise RuntimeError("Couldn't get your Streamlit Session object.")
    return session_info.session.id

def run_r_script(exp_file, meta_file, out_file):
    # Call R script using subprocess
    subprocess.call(['Rscript', r_script_path, exp_file, meta_file, out_file])

# Visualize differential expression results
def plot_de_results(results):
    # Adjust p-values for multiple testing
    results['padj'] = multipletests(results['padj'], method='fdr_bh')[1]

    # Calculate -log10 adjusted p-value
    results['log10padj'] = -np.log10(results['padj'] + 1e-100)
    
    # Plot volcano plot
    plt.figure(figsize=(10, 6))
    plt.scatter(results['log2FoldChange'], -1 * results['log10padj'], color='blue', alpha=0.5)
    plt.xlabel('Log2 Fold Change')
    plt.ylabel('-Log10 Adjusted P-value')
    plt.title('Volcano Plot')
    st.pyplot(plt.gcf())

# Main function to run the app
def main():
    # 获得session id 用于创建文件夹
    user_id       = get_sessionID()
    st.title("Bulk RNA-Seq Differential Expression Analysis")

    # File upload for RNA-Seq data
    st.subheader("Upload your RNA-Seq data (CSV format)")
    exp_file  = st.file_uploader("Choose a CSV file for gene expression",   type="csv")
    meta_file = st.file_uploader("Choose a CSV file for group comparisons", type="csv")

    if exp_file is not None and meta_file is not None:

        # 获取当前用户的会话ID & 创建用户临时文件夹
        user_temp_dir = create_user_temp_dir(user_id)
        st.write(f"您的临时文件夹路径：{user_temp_dir}")
        # Load gene expression
        data = pd.read_csv(exp_file)
        # Display raw data
        st.subheader("gene expression (Top 10 rows)")
        st.write(data.head(10))
        ## 重新保存后面网上修改了可以存储
        exp_file = user_temp_dir + "/gene.csv"
        data.to_csv(exp_file, index=False)
        

        # Load group comparisons
        meta = pd.read_csv(meta_file)
        st.subheader("group comparisons")
        st.write(meta)
        meta_file = user_temp_dir + "/meta.csv"
        meta.to_csv(meta_file, index=False)

        ## output file
        out_file = user_temp_dir + "/res.csv"

        # Button to trigger R script execution
        if st.button('Run DESeq2 for comparisons:'):
        # Call the function to run R script
            run_r_script(exp_file, meta_file, out_file)
            st.write('DESeq2 executed successfully!')

            # Display differential expression results
            results = pd.read_csv("res.csv")
            st.subheader("Differential Expression Results")
            st.write(results)
        
            # Plot differential expression results
            st.subheader("Visualizations")
            plot_de_results(results)





if __name__ == "__main__":
    main()