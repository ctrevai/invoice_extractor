import random
import string
import streamlit as st
import os
import boto3
import io

session = boto3.Session()
s3 = session.client("s3")
agent_client_runtime = session.client("bedrock-agent-runtime")

model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

s3_bucket_name = os.getenv("S3_BUCKET_NAME")


def _session_generator():
    # Generate random characters and digits
    digits = ''.join(random.choice(string.digits)
                     for _ in range(4))  # Generating 4 random digits
    chars = ''.join(random.choice(string.ascii_lowercase)
                    for _ in range(3))  # Generating 3 random characters

    # Construct the pattern (1a23b-4c)
    pattern = f"{digits[0]}{chars[0]}{digits[1:3]}{
        chars[1]}-{digits[3]}{chars[2]}"
    print("Session ID: " + str(pattern))

    return pattern


def _retrieve_generate(input_text, sourceType, document_s3_uri):

    if sourceType == "S3":
        return agent_client_runtime.retrieve_and_generate(
            input={'text': input_text},
            retrieveAndGenerateConfiguration={
                'type': 'EXTERNAL_SOURCES',
                'externalSourcesConfiguration': {
                    'modelArn': model_id,
                    'sources': [
                        {
                            'sourceType': sourceType,
                            's3Location': {'uri': document_s3_uri
                                           }
                        }
                    ]
                }
            }
        )
    else:
        return None


class ExtractInvoice:
    def upload_invoice(self):
        st.write("Upload Invoice")
        uploaded_file = st.file_uploader("Choose a file", type=["pdf"])
        if uploaded_file is not None:
            st.write(uploaded_file)
            st.write(uploaded_file.name)
            file_content = uploaded_file.getvalue()
            try:
                file_obj = io.BytesIO(file_content)
                s3.upload_fileobj(file_obj, s3_bucket_name, uploaded_file.name)
                st.success("File uploaded successfully")
                st.session_state.s3_uri = f"s3://{
                    s3_bucket_name}/{uploaded_file.name}"
            except Exception as e:
                st.error(f"Error uploading file: {e}")

    def analyse_invoice(self):
        st.write("Analyse Invoice")

    def ask_anything(self):
        st.write("Ask Anything")
        query = st.text_input(
            "Ask Anything", value="", placeholder="Ask question about the invoice", label_visibility="visible")
        if st.session_state.s3_uri == "":
            st.error("Please upload the invoice")
            return
        elif query == "":
            return
        else:
            response = _retrieve_generate(query, "S3", st.session_state.s3_uri)
        if response is not None:
            st.write(response['output']['text'])

    def render(self):
        st.set_page_config(page_title="Extract Invoice",
                           page_icon="📄", layout="wide")
        st.title("Extract Invoice")
        st.write("Extract Invoice")

        if "session_id" not in st.session_state:
            st.session_state.session_id = _session_generator()

        if "s3_uri" not in st.session_state:
            st.session_state.s3_uri = ""

        self.upload_invoice()
        self.analyse_invoice()
        self.ask_anything()


if __name__ == "__main__":
    ExtractInvoice().render()
