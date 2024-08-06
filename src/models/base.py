from sqlmodel import SQLModel

# class Base(SQLModel, table=True):
class Base(SQLModel):
    def __repr__(self):
        return str(self.__dict__)

    # def __eq__(self)
