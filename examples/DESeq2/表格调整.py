import streamlit as st
import pandas as pd
from streamlit import session_state as ss
import uuid


def update_value():
    """
    Located on top of the data editor.
    """
    ss.dek = str(uuid.uuid4())  # triggers reset



def main():
    # Create de key
    if 'dek' not in ss:
        ss.dek = str(uuid.uuid4())

    meta_file = st.file_uploader("Choose a CSV file for group comparisons", type="csv")

    if meta_file is not None:
        # 加载原始数据
        meta     = pd.read_csv(meta_file)

        # 展示数据
        st.subheader("group comparisons")
        edf = st.data_editor(meta, hide_index=True, use_container_width=True, disabled=["sample"], key=ss.dek)

        st.button("Reset", on_click=update_value)


if __name__ == "__main__":
    main()
