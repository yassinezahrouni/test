import kagglehub

# Download latest version
path = kagglehub.dataset_download("amirmotefaker/supply-chain-dataset")

print("Path to dataset files:", path)