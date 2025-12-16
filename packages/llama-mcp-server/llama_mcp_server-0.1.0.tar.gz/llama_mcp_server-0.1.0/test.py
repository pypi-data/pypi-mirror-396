import os
from llama_cloud_services import LlamaParse

# Hardcoded keys for testing
os.environ["LLAMA_CLOUD_API_KEY"] = "llx-AGTygqkQ3fTUDIfPc8C90rqm3xSXR1PM59bRsLfsXhg2Iu4V"
os.environ["OPENAI_API_KEY"] = "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"

parser = LlamaParse(
    result_type="markdown",
    parse_mode="parse_page_with_agent",  # Premium mode - no vendor key allowed
)

# Update this path to your actual Word doc
result = parser.load_data(r"D:\Users\Work\Downloads\SOP for IOT Orders Recovery (1).docx")

# Check how many documents/pages were returned
print(f"Number of documents: {len(result)}")

# Combine ALL documents
full_text = "\n\n---\n\n".join([doc.text for doc in result])

with open("parsed_output.md", "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"Saved {len(full_text)} characters to parsed_output.md")