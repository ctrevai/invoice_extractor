import streamlit as st


class ExtractInvoice:
    def render(self):
        st.set_page_config(page_title="Extract Invoice",
                           page_icon="📄", layout="wide")
        st.title("Extract Invoice")
        st.write("Extract Invoice")


if __name__ == "__main__":
    ExtractInvoice().render()
