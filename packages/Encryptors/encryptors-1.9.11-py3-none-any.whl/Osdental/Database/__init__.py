from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

class Connection:
    """
    Produce:
    - engine (una sola vez)
    - session_factory, usado por cada request
    """
    
    def __init__(self, db_url: str):
        self.engine = create_async_engine(
            db_url,
            pool_size=20,
            max_overflow=40,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True
        )

        self.session_factory = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False,
        )

    async def get_session(self) -> AsyncSession:
        """
        Retorna una nueva sesión por request.
        NO se cachea.
        """
        return self.session_factory()
