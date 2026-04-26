import os
import uuid
import boto3

R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_BUCKET = os.getenv("R2_BUCKET")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_REGION = os.getenv("R2_REGION", "auto")

if not all([R2_ENDPOINT, R2_BUCKET, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
    raise RuntimeError("R2 env vars are missing")

# Pripojenie na Cloudflare R2 endpoint
s3 = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name=R2_REGION,
)

# Vytvorenie kľúča objektu (cesta k súboru)
def build_cv_object_key(user_id: int, group_id: int, filename: str) -> str:
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return f"cv/u{user_id}/g{group_id}/{uuid.uuid4().hex}{ext}"

# Upload objektu do storage
def upload_cv_file(file_obj, object_key: str, content_type: str | None = None):
    if content_type:
        s3.upload_fileobj(file_obj, R2_BUCKET, object_key, ExtraArgs={"ContentType": content_type})
    else:
        s3.upload_fileobj(file_obj, R2_BUCKET, object_key)

# Delete objektu v storage
def delete_cv_file(object_key: str) -> None:
    if not object_key:
        raise ValueError("object_key is required")
    s3.delete_object(
        Bucket=R2_BUCKET,
        Key=object_key,
    )

# Vygeneruje dočasný URL pre čítanie objektu z R2
def get_cv_presigned_url(
    object_key: str,
    expires_in: int = 300,
    response_content_disposition: str | None = None,
    response_content_type: str | None = None,
) -> str:
    
    if not object_key:
        raise ValueError("object_key is required")
    
    params = {
        "Bucket": R2_BUCKET,
        "Key": object_key,
    }

    if response_content_disposition:
        params["ResponseContentDisposition"] = response_content_disposition
    if response_content_type:
        params["ResponseContentType"] = response_content_type
    return s3.generate_presigned_url(
        ClientMethod="get_object",
        Params=params,
        ExpiresIn=expires_in,
    )