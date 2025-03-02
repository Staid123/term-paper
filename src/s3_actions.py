from typing import Annotated
from fastapi import Depends, HTTPException, UploadFile, status
from config import settings
import boto3


class S3Client:
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(settings.aws.bucket_name)

    async def upload_file(
        self, 
        file: UploadFile,
        key: str, 
    ) -> None:
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='No file found!!'
            )
        contents = await file.read()
        size = len(contents)
        if not 0 < size <= 200 * 1024: # 200 MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Supported file size is 0 - 200 MB'
            )

        s3_object = self.bucket.put_object(Key=key, Body=contents)
        if not s3_object:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error during loading file {file.filename}"
            )
        
    @staticmethod
    async def delete_file(
        self,
        key: str,
    ) -> None:
        response = self.bucket.delete_objects(
            Delete={
                'Objects': [
                    {
                        'Key': key
                    }
                ]
            }
        )
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error during deletion file {key}"
            )
        
S3ClientDep = Annotated[S3Client, Depends(S3Client)]