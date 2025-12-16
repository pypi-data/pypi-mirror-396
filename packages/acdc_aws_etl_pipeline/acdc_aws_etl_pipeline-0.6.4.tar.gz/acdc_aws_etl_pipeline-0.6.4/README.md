# acdc-aws-etl-pipeline
Infrastructure and code for the ACDC ETL pipeline and data operations in AWS

## Ingestion
- [ingestion](docs/ingestion.md)
- [upload_synthdata_s3](docs/upload_synthdata_s3.md)

## DBT



## Release Management
- [Writing DBT Releases](docs/write_dbt_release_info.md)


## Deploying the dictionary
e.g. to testing

```bash
# Example 
bash services/dictionary/pull_dict.sh <raw_dictionary_url>
bash services/dictionary/upload_dictionary.py <local_dictionary_path> <s3_target_uri>

# Deploying to test
VERSION=v0.6.3
bash services/dictionary/pull_dict.sh "https://raw.githubusercontent.com/AustralianBioCommons/acdc-schema-json/refs/tags/${VERSION}/dictionary/prod_dict/acdc_schema.json"
python3 services/dictionary/upload_dictionary.py "services/dictionary/schemas/acdc_schema_${VERSION}.json" s3://gen3schema-cad-uat-biocommons.org.au/cad.json


# Deploying to staging
VERSION=v1.0.0
bash services/dictionary/pull_dict.sh "https://raw.githubusercontent.com/AustralianBioCommons/acdc-schema-json/refs/tags/${VERSION}/dictionary/prod_dict/acdc_schema.json"
python3 services/dictionary/upload_dictionary.py "services/dictionary/schemas/acdc_schema_${VERSION}.json" s3://gen3schema-cad-staging-biocommons.org.au/cad.json
```

## Generating synthetic metadata
- Run this script to generate synthetic metadata for the studies in the dictionary

```bash
# this will generate 30 samples for AusDiab_Simulated and 60 samples for Baker-Biobank_Simulated
bash services/synthetic_data/generate_synth_metadata.sh --studies "AusDiab_Simulated,Baker-Biobank_Simulated" --permute-max-samples "30,60"
```

## uploading synthetic metadata to sheepdog
- Run this script to upload synthetic metadata to sheepdog

```python
# to see argumments
python3 services/synthetic_data/upload_synth_metadata_sheepdog.py -h

# to upload metadata for version v0.6.3
python3 services/synthetic_data/upload_synth_metadata_sheepdog.py --version v0.6.3
```