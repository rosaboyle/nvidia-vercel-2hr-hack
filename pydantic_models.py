from pydantic import BaseModel


class ToxinList(BaseModel):
    """
    A list of toxins.
    """

    class Toxin(BaseModel):
        name: str
        sources: list[str]
        health_effects: list[str]
        related_diseases: list[str]
        reference_context: str
        relevant_regulations: list[str]

    toxins: list[Toxin]


class ToxinListResponse(BaseModel):
    toxins: list[ToxinList.Toxin]
    urls: list[str]
