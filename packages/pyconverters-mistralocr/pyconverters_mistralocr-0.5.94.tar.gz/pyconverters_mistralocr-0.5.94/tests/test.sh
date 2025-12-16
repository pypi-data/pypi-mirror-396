# Read the pdf file
input_file_path="data/test_pdf.pdf"
base64_value=$(base64 "$input_file_path")
input_base64_value="data:application/pdf;base64,${base64_value}"
# echo $input_base64_value

# Prepare JSON data
payload_body=$(cat <<EOF
{
    "model": "mistral-ocr-2505",
    "document": {
        "type": "document_url",
        "document_url": "$input_base64_value"
    },
    "include_image_base64": true
}
EOF
)

echo "$payload_body" | curl https://mistral-ocr-2503-aavuq.swedencentral.models.ai.azure.com/v1/ocr \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer lxxcFBig0iSag5EtOujgCxu0B3DcVQhb" \
  -d @- -o ocr_pdf_output.json