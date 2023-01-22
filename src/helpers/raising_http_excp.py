from fastapi import HTTPException
from starlette import status

from src.core.constants import APIAnswers


class RaiseHttpException:

    @staticmethod
    def check_is_exist(item):
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=APIAnswers.NOT_FOUND
            )

    @staticmethod
    def check_is_delete(item):
        if item.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_410_GONE, detail=APIAnswers.GONE
            )
