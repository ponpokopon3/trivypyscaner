# trivypyscaner

'''
docker build -t sbom-generator .
docker run --rm -v ${PWD}/input.csv:/app/input.csv -v ${PWD}/sbom_outputs:/app/sbom_outputs sbom-generator
