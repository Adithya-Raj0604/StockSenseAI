# State backend — LOCAL by default (see live/backend.tf for the S3 option).
# full-demo is applied manually and destroyed in the same session, so local
# state is fine; just don't lose the state file before you `terraform destroy`.
