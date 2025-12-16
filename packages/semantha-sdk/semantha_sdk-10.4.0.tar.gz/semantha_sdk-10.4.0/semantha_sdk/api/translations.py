from semantha_sdk.model.translation import Translation
from semantha_sdk.model.translation import TranslationSchema
from semantha_sdk.model.translation_response import TranslationResponse
from semantha_sdk.model.translation_response import TranslationResponseSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient, RestEndpoint

class TranslationsEndpoint(RestEndpoint):
    """
    Class to access resource: "/api/domains/{domainname}/translations"
    author semantha, this is a generated class do not change manually! 
    
    """

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/translations"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    
    def post(
        self,
        body: Translation = None,
    ) -> TranslationResponse:
        """
        Translates a single text to a target language, optionally from a source language.
        Args:
        body (Translation): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=TranslationSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(TranslationResponseSchema)

    
    
    