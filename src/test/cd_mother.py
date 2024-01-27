from openmath.cd import *
from random import randint, choice
import test.sd_mother as sd_mother


def of(
    name: str = "test_cd_%03d" % randint(0, 999),
    description: str = "description",
    revision: str = "2024-01-01",
    review: str = "2025-01-01",
    version: str = "1.0",
    status: str = choice(["official", "experimental", "private"]),
    base: str = "test_cdbase_%03d" % randint(0, 999),
    url: str = "url",
    comment: str = "dictionary comment",
    definitions: list = [sd_mother.of() for _ in range(randint(0, 6))],
):
    return ContentDictionary(
        name=name,
        description=description,
        revision=revision,
        review=review,
        version=version,
        status=status,
        base=base,
        url=url,
        comment=comment,
        definitions=definitions,
    )
