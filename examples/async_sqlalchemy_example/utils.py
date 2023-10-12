from sqlalchemy.ext.asyncio import AsyncSession

from .models import Tag, User, Paper, Address


async def seed_db(db: AsyncSession):
    tags = [
        Tag(name="Engineering"),
        Tag(name="Computer Science"),
        Tag(name="Artificial Intelligence (AI)"),
        Tag(name="Natural Language Processing (NLP)"),
        Tag(name="Computer Vision (CV)"),
        Tag(name="Healthcare"),
        Tag(name="Medicine"),
        Tag(name="Biology"),
        Tag(name="Chemistry"),
    ]

    users = [
        User(
            first_name="John",
            last_name="Doe",
            email="johndoe@email.com",
            tags=tags[:5],
            shipping_address=Address(
                line_1="Main Street 1",
                city="San Diego",
                zip_code="90123",
                state="CA",
                country="US"
            ),
            billing_address=Address(
                line_1="32th West Street 2",
                city="San Diego",
                zip_code="90123",
                state="CA",
                country="US"
            )

        ),
        User(
            first_name="Mia",
            last_name="Morris",
            email="miamorris@email.com",
            tags=[tags[2], tags[5], tags[6]]
        ),
        User(
            first_name="Paul",
            last_name="Walker",
            email="paulwalker@email.com",
            tags=tags[5:]
        )
    ]

    papers = [
        Paper(
            title="Attention Is All You Need",
            author=users[0],
            tags=tags[2:4]
        ),
        Paper(
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            author=users[0],
            tags=tags[2:4]
        ),
        Paper(
            title="Large language models encode clinical knowledge",
            author=users[1],
            tags=[tags[3], tags[5], tags[6]]
        ),
    ]

    db.add_all([
        *tags,
        *users,
        *papers
    ])
    await db.commit()
