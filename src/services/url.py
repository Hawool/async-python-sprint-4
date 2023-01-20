from src.models.urls import UrlModel
from src.schemas.url import UrlCreate, UrlUpdate
from src.services.crud import RepositoryDB


class RepositoryUrl(RepositoryDB[UrlModel, UrlCreate, UrlUpdate]):
    pass


url_crud = RepositoryUrl(UrlModel)
